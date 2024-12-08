from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app import db
from app.models.project import ProjectSchema
from app.models.social_link import SocialLinkSchema
from app.models.user import UserCreateSchema

API_PREFIX = '/api/v1/test'
bp = Blueprint('test_routes', __name__, url_prefix=API_PREFIX)


@bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "Hello World!"}), 200


@bp.route('/secured/ping', methods=['GET'])
@jwt_required()
def ping_secured():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


@bp.route('/createsampledata', methods=['POST'])
def create_sample_data():
    data = request.get_json()

    projects = data.get('projects')
    for project_data in projects:
        project_schema = ProjectSchema()
        try:
            # Validate and deserialize input data into Project object
            new_project = project_schema.load(project_data)

            # Persist the new project in the database
            new_project.save()

        except ValidationError:  # Handle schema validation errors
            continue

        except Exception as e:
            print(e)  # Log unexpected errors for debugging
            db.session.rollback()
            continue

    social_links = data.get('social_links')
    for sl_data in social_links:
        sl_schema = SocialLinkSchema()
        try:
            # Validate and deserialize input data into SocialLink object
            new_sl = sl_schema.load(sl_data)

            # Persist in the database
            new_sl.save()

        except ValidationError:  # Handle schema validation errors
            continue

        except Exception as e:
            print(e)  # Log unexpected errors for debugging
            db.session.rollback()
            continue

    users = data.get('users')
    for user_data in users:
        user_schema = UserCreateSchema()
        try:
            # Validate and deserialize input data into a User object
            new_user = user_schema.load(user_data)

            # Persist the new user in the database
            new_user.save()

        except ValidationError:  # Handle schema validation errors
            continue

        except Exception as e:
            print(e)  # Log unexpected errors for debugging
            db.session.rollback()
            continue

    return jsonify({"message": "Sample data created successfully"}), 200
