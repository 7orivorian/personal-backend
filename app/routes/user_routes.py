from email_validator import EmailNotValidError
from flask import Blueprint, jsonify, request, abort, make_response
from flask_bcrypt import check_password_hash
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies, create_refresh_token, \
    set_refresh_cookies, get_jwt_identity, jwt_required, get_jwt, get_csrf_token

from app.exception.validation_error import ValidationError
from app.models import RevokedToken
from app.models.user import User, db
from app.utils.validators import validate_user_id, admin_required

API_PREFIX: str = '/v1/users'
bp = Blueprint('user_routes', __name__, url_prefix=API_PREFIX)


@bp.route('/', methods=['GET'])
@admin_required
def get_users():
    users = User.query.all()
    return jsonify([user.dump() for user in users] if users else [])


@bp.route('/', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data:
        return jsonify({
            "message": "Invalid input data",
            "error": "No data provided"
        }), 400

    try:
        # Remove 'is_admin' key from input data if it exists
        if 'is_admin' in data:
            del data['is_admin']

        new_user = User(is_admin=False, **data)

        # Persist the new user in the database
        new_user.save()

        # Serialize the created user for the response
        return jsonify(new_user.dump()), 201

    except ValidationError as e:  # Handle validation errors
        return jsonify({
            "message": e.message,
            "error": "Validation error"
        }), 400

    except EmailNotValidError as e:  # Handle email specific validation errors
        print("Email not valid: ", e)
        return jsonify({
            "message": e,
            "error": "Email validation error"
        }), 400

    except Exception as e:
        print("Exception: ", e)
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
                "error": "Bad request"
            }), 400

        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({
                "message": f"User with username '{username}' does not exist",
                "error": "User not found"
            }), 404

        # Validate password
        if check_password_hash(user.password, password):
            # Create access token
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))

            csrf_access_token = get_csrf_token(access_token)
            csrf_refresh_token = get_csrf_token(refresh_token)

            response_data = {
                "message": "Login successful",
                "csrf_access_token": csrf_access_token,
                "csrf_refresh_token": csrf_refresh_token,
                "user": user.dump(),
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


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True, verify_type=True)
def refresh_tokens():
    identity = get_jwt_identity()
    user = User.query.get_or_404(identity)

    # Create new access & refresh tokens
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)

    csrf_access_token = get_csrf_token(access_token)

    response = make_response(jsonify({
        "message": "Token refreshed successfully",
        "csrf_access_token": csrf_access_token,
        "user": user.dump(),
    }), 200)

    # Update token cookies
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)

    return response


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


@bp.route('/delete/id/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user_by_id(user_id):
    if not validate_user_id(user_id):
        return abort(400, "Invalid user ID")

    user = User.query.get(user_id)
    if user:
        user.delete()
        return jsonify({"message": "User deleted successfully"}), 204
    else:
        return jsonify({
            "message": "User not found",
            "error": "User not found"
        }), 404
