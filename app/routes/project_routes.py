from flask import Blueprint, jsonify, request

from app import db
from app.exception.validation_error import ValidationError
from app.models.models import get_or_create
from app.models.project import Project, Tag
from app.utils.validators import admin_required

API_PREFIX: str = '/api/v1/projects'
bp = Blueprint('project_routes', __name__, url_prefix=API_PREFIX)


@bp.route('/', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    return jsonify([project.dump() for project in projects]), 200


@bp.route('/<int:project_id>', methods=['GET'])
def get_project(project_id):
    project = Project.query.get_or_404(project_id, description="Project not found")
    return jsonify(project.dump()), 200


@bp.route('/', methods=['POST'])
@admin_required
def create_project():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        # Extract tags information (if provided)
        tags_data = data.pop('tags', [])  # Default to empty list if 'tags' key is not present
        tech_tags_data = data.pop('tech_stack', [])  # Default to empty list if 'tech_stack' key is not present

        # Validate and deserialize input data into Project object
        project = Project(**data)

        # Attach tag objects to the project
        for tag_name in tags_data:
            tag = get_or_create(db.session, Tag, name=tag_name, is_tech=False)
            project.tags.append(tag)

        # Attach tech tags objects to the project
        for tag_name in tech_tags_data:
            tag = get_or_create(db.session, Tag, name=tag_name, is_tech=True)
            project.tags.append(tag)

        # Persist the new project in the database
        project.save()

        # Serialize the created project for the response
        return jsonify(project.dump()), 201

    except ValidationError as e:  # Handle schema validation errors
        return jsonify({
            "message": e.message,
            "error": "Validation error"
        }), 400

    except Exception as e:
        print(e)  # Log unexpected errors for debugging
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 500


@bp.route('/<int:project_id>', methods=['PATCH'])
@admin_required
def update_project_by_id(project_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    project = Project.query.get_or_404(project_id, description="Project not found")

    try:
        # Wall of code!
        if 'name' in data:
            project.name = data['name']
        if 'description' in data:
            project.description = data['description']
        if 'url' in data:
            project.url = data['url']
        if 'image_url' in data:
            project.image_url = data['image_url']
        if 'source_code_url' in data:
            project.source_code_url = data['source_code_url']
        if 'type' in data:
            project.type = data['type']
        if 'status' in data:
            project.status = data['status']
        if 'featured' in data:
            project.featured = data['featured']
        if 'begin_date' in data:
            project.begin_date = data['begin_date']
        if 'completion_date' in data:
            project.completion_date = data['completion_date']

        # Extract tags information (if provided)
        tags_data = data.pop('tags', [])  # Default to empty list if 'tags' key is not present
        tech_tags_data = data.pop('tech_stack', [])  # Default to empty list if 'tech_stack' key is not present

        # Attach tag objects to the project
        project.tags = []
        for tag_name in tags_data:
            tag = get_or_create(db.session, Tag, name=tag_name, is_tech=False)
            project.tags.append(tag)

        # Attach tech tags objects to the project
        for tag_name in tech_tags_data:
            tag = get_or_create(db.session, Tag, name=tag_name, is_tech=True)
            project.tags.append(tag)

        # Persist the updated project in the database
        project.save()

        # Serialize the updated project for the response
        return jsonify(project.dump()), 200

    except ValidationError as e:  # Handle schema validation errors
        return jsonify({
            "message": e.message,
            "error": "Validation error"
        }), 400

    except Exception as e:
        print(e)  # Log unexpected errors for debugging
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 500


@bp.route('delete/id/<int:project_id>', methods=['DELETE'])
@admin_required
def delete_project_by_id(project_id):
    project = Project.query.get_or_404(project_id, description="Project not found")
    project.delete()
    return jsonify({"message": "Project deleted successfully"}), 204


@bp.route('delete/slug/<string:slug>', methods=['DELETE'])
@admin_required
def delete_project_by_slug(slug):
    project = Project.query.filter_by(slug=slug).first_or_404(description="Project not found")
    project.delete()
    return jsonify({"message": "Project deleted successfully"}), 204
