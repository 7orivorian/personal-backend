from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.exception.validation_error import ValidationError
from app.models import SocialLink
from app.models.models import get_or_create
from app.models.project import Tag, Project
from app.models.user import User

API_PREFIX = '/api/v1/test'
bp = Blueprint('test_routes', __name__, url_prefix=API_PREFIX)


@bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "Pong!"}), 200


@bp.route('/secured/ping', methods=['GET'])
@jwt_required()
def ping_secured():
    current_user = get_jwt_identity()
    if current_user:
        return jsonify({"message": "Halllooo!"}), 200
    return jsonify({"message": "bad request or not auth"}), 401


@bp.route('/createsampledata', methods=['POST'])
def create_sample_data():
    data = request.get_json()

    projects = data.get('projects')
    for project_data in projects:
        try:
            # Extract tags information (if provided)
            # Default to empty list if 'tags' key is not present
            tags_data = project_data.pop('tags', [])
            # Default to empty list if 'tech_stack' key is not present
            tech_tags_data = project_data.pop('tech_stack', [])

            # Validate and deserialize input data into Project object
            new_project = Project(**project_data)

            # Attach tag objects to the project
            for tag_name in tags_data:
                tag = get_or_create(db.session, Tag, name=tag_name, is_tech=False)
                new_project.tags.append(tag)

            # Attach tech tags objects to the project
            for tag_name in tech_tags_data:
                tag = get_or_create(db.session, Tag, name=tag_name, is_tech=True)
                new_project.tags.append(tag)

            # Persist the new project in the database
            new_project.save()

        except ValidationError as e:  # Handle schema validation errors
            print(e)  # Log unexpected errors for debugging
            continue

        except Exception as e:
            print(e)  # Log unexpected errors for debugging
            db.session.rollback()
            continue

    social_links = data.get('social_links')
    for sl_data in social_links:
        try:
            # Validate and deserialize input data into SocialLink object
            new_sl = SocialLink(**sl_data)

            # Persist in the database
            new_sl.save()

        except ValidationError as e:  # Handle schema validation errors
            print(e)  # Log unexpected errors for debugging
            continue

        except Exception as e:
            print(e)  # Log unexpected errors for debugging
            db.session.rollback()
            continue

    users = data.get('users')
    for user_data in users:
        try:
            # Validate and deserialize input data into a User object
            new_user = User(**user_data)

            # Persist the new user in the database
            new_user.save()

        except ValidationError as e:  # Handle schema validation errors
            print(e)  # Log unexpected errors for debugging
            continue

        except Exception as e:
            print(e)  # Log unexpected errors for debugging
            db.session.rollback()
            continue

    return jsonify({"message": "Sample data created successfully"}), 200
