from flask import Blueprint, jsonify, request, abort
from flask_bcrypt import check_password_hash
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError

from app.models.user import User, db, UserCreateSchema, UserSchema
from app.utils.validators import validate_user_id

API_PREFIX: str = '/api/v1/users'
bp = Blueprint('user_routes', __name__, url_prefix=API_PREFIX)


@bp.route('/', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([UserSchema().dump(user) for user in users] if users else [])


@bp.route('/', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    user_schema = UserCreateSchema()

    try:
        # Validate and deserialize input data into a User object
        new_user = user_schema.load(data)

        # Persist the new user in the database
        new_user.save()

        # Serialize the created user for the response
        return jsonify(user_schema.dump(new_user)), 201

    except ValidationError as e:  # Handle schema validation errors
        return jsonify({"errors": e.messages}), 400

    except Exception as e:
        print(e)  # Log unexpected errors for debugging
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
            return jsonify({"error": "Username and password required"}), 400

        # Query the user by username
        user = User.query.filter_by(username=username).first()

        # Validate password
        if user and check_password_hash(user.password, password):
            # Create access token
            access_token = create_access_token(identity=str(user.id))
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401

    except ValidationError as e:
        return jsonify({"errors": e.messages}), 400
    except Exception as e:
        print(e)
        return jsonify({"error": "An unexpected error occurred"}), 500


@bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    if not validate_user_id(user_id):
        return abort(400, "Invalid user ID")

    user = User.query.get(user_id)
    if user:
        user_schema = UserCreateSchema()
        return jsonify(user_schema.dump(user))
    else:
        return jsonify({"error": "User not found"}), 404
