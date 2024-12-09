from flask import Blueprint, jsonify, request, abort, make_response
from flask_bcrypt import check_password_hash
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies, create_refresh_token, \
    set_refresh_cookies, get_jwt_identity, jwt_required, get_jwt, get_csrf_token
from marshmallow import ValidationError

from app.models.revoked_token import RevokedTokenSchema
from app.models.user import User, db, UserCreateSchema, UserSchema
from app.utils.validators import validate_user_id

API_PREFIX: str = '/api/v1/users'
bp = Blueprint('user_routes', __name__, url_prefix=API_PREFIX)


@bp.route('/', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([UserSchema().dump(user) for user in users] if users else [])


@bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    if not validate_user_id(user_id):
        return abort(400, "Invalid user ID")

    user = User.query.get(user_id)
    if user:
        user_schema = UserCreateSchema()
        return jsonify(user_schema.dump(user))
    else:
        return jsonify({
            "message": "User not found",
            "error": "User not found"
        }), 404


@bp.route('/', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data:
        return jsonify({
            "message": "Invalid input data",
            "error": "No data provided"
        }), 400

    user_schema = UserCreateSchema()

    try:
        # Validate and deserialize input data into a User object
        new_user = user_schema.load(data)

        # Persist the new user in the database
        new_user.save()

        # Serialize the created user for the response
        return jsonify(user_schema.dump(new_user)), 201

    except ValidationError as e:  # Handle schema validation errors
        return jsonify({
            "message": "Invalid input data",
            "error": "Validation error",
            "errors": e.messages
        }), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 500


@bp.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    user_schema = UserSchema()

    try:
        # Validate input data
        validated_data = user_schema.load(data, partial=True)
        username = validated_data.get("username")
        password = validated_data.get("password")

        if not username or not password:
            return jsonify({
                "message": "Username and password required",
                "error": "Invalid credentials"
            }), 400

        # Query the user by username
        user = User.query.filter_by(username=username).first()

        # Validate password
        if user and check_password_hash(user.password, password):
            # Create access token
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))

            csrf_access_token = get_csrf_token(access_token)

            response_data = {
                "message": "Login successful",
                "csrf_access_token": csrf_access_token,
                "id": user.id,
                "email": user.email,
                "username": user.username
            }
            response = make_response(jsonify(response_data), 200)

            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)

            return response
        else:
            return jsonify({
                "message": "Invalid username or password",
                "error": "Invalid credentials"
            }), 401

    except ValidationError as e:
        return jsonify({
            "message": "Invalid input data",
            "error": "Validation error",
            "errors": e.messages
        }), 400
    except Exception as e:
        return jsonify({
            "message": "An error occurred while logging in",
            "error": "An unexpected error occurred"
        }), 500


@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout_user():
    jwt_data = get_jwt()
    if not jwt_data:
        return jsonify({
            "message": "Invalid credentials",
            "error": "Invalid JWT token"
        }), 401
    elif 'jti' not in jwt_data:
        return jsonify({
            "message": "Invalid credentials",
            "error": "Missing JWT token"
        }), 401

    jti = jwt_data['jti']

    schema = RevokedTokenSchema()

    try:
        revoked_token = schema.load({"jti": jti})
        revoked_token.save()

        response = make_response(jsonify({"message": "Logout successful"}), 200)
        unset_jwt_cookies(response)
        return response

    except ValidationError as e:
        return jsonify({
            "message": "Invalid input data",
            "error": "Validation error",
            "errors": e.messages
        }), 400
    except Exception as e:
        return jsonify({
            "message": "An error occurred while logging out",
            "error": "An unexpected error occurred"
        }), 500


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True, verify_type=True)
def refresh_tokens():
    current_user = get_jwt_identity()

    # Create new access & refresh tokens
    access_token = create_access_token(identity=current_user)
    refresh_token = create_refresh_token(identity=current_user)

    response = make_response(jsonify({"message": "Token refreshed successfully"}), 200)

    # Update token cookies
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)

    return response
