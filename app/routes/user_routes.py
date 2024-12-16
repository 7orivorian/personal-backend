from flask import Blueprint, jsonify, request, abort, make_response
from flask_bcrypt import check_password_hash
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies, create_refresh_token, \
    set_refresh_cookies, get_jwt_identity, jwt_required, get_jwt, get_csrf_token

from app.exception.validation_error import ValidationError
from app.models import RevokedToken
from app.models.user import User, db
from app.utils.validators import validate_user_id, admin_required

API_PREFIX: str = '/api/v1/users'
bp = Blueprint('user_routes', __name__, url_prefix=API_PREFIX)


@bp.route('/', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.dump() for user in users] if users else [])


@bp.route('/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    if not validate_user_id(user_id):
        return abort(400, "Invalid user ID")

    user = User.query.get(user_id)
    if user:
        return jsonify(user.dump())
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

    try:
        new_user = User(**data)

        # Persist the new user in the database
        new_user.save()

        # Serialize the created user for the response
        return jsonify(new_user.dump()), 201

    except ValidationError as e:  # Handle schema validation errors
        return jsonify({
            "message": e.message,
            "error": "Validation error"
        }), 400

    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 500


@bp.route('/login', methods=['POST'])
def login_user():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        username = data['username']
        password = data['password']

        if not password:
            return jsonify({
                "message": "Password required",
                "error": "Bad request"
            }), 400

        if not username:
            return jsonify({
                "message": "Username required",
                "error": "Bac request"
            }), 400

        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({
                "message": f"User with username '{username}' does not exist",
            })

        # Validate password
        if check_password_hash(user.password, password):
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
                "message": "Incorrect password",
                "error": "Invalid credentials"
            }), 401

    except ValidationError as e:
        return jsonify({
            "message": e.message,
            "error": "Validation error"
        }), 400
    except Exception as e:
        print(e)
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
    user_id = get_jwt_identity()

    try:
        revoked_token = RevokedToken(jti=jti, user_id=user_id)
        revoked_token.save()

        response = make_response(jsonify({"message": "Logout successful"}), 200)
        unset_jwt_cookies(response)
        return response

    except ValidationError as e:
        return jsonify({
            "message": e.message,
            "error": "Validation error"
        }), 400
    except Exception as e:
        print(e)
        return jsonify({
            "message": "An error occurred while logging out",
            "error": "Unknown error"
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
