from flask import Blueprint, jsonify, request

from app import db
from app.exception.validation_error import ValidationError
from app.models.project import Project, Tag
from app.utils.utils import is_present
from app.utils.validators import admin_required

API_PREFIX: str = '/api/v1/projects'
bp = Blueprint('project_routes', __name__, url_prefix=API_PREFIX)


def update_project(project, data):
    # Wall of code!
    if is_present(data, 'name'):
        project.name = data['name']
    if is_present(data, 'description'):
        project.description = data['description']
    if is_present(data, 'url'):
        project.url = data['url']
    if is_present(data, 'image_url'):
        project.image_url = data['image_url']
    if is_present(data, 'source_code_url'):
        project.source_code_url = data['source_code_url']
    if is_present(data, 'type'):
        project.type = data['type']
    if is_present(data, 'status'):
        project.status = data['status']
    if is_present(data, 'featured'):
        project.featured = data['featured']
    if is_present(data, 'begin_date'):
        project.begin_date = data['begin_date']
    if is_present(data, 'completion_date'):
        project.completion_date = data['completion_date']

    db.session.add(project)

    if is_present(data, 'tags'):
        project.clear_tags()
        tags_data = data.pop('tags', [])
        for tag_name in tags_data:
            tag = Tag.get_or_create(name=tag_name, is_tech=False)
            project.add_tag(tag)

    if is_present(data, 'tech'):
        tech_data = data.pop('tech', [])
        for tag_name in tech_data:
            tag = Tag.get_or_create(name=tag_name, is_tech=True)
            project.add_tag(tag)

    # Persist the updated project in the database
    project.save()


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
        tech_tags_data = data.pop('tech', [])  # Default to empty list if 'tech_stack' key is not present

        # Validate and deserialize input data into Project object
        project = Project(**data)

        # Project must be in session before any tags are added
        db.session.add(project)

        # Attach tag objects to the project
        for tag_name in tags_data:
            tag = Tag.get_or_create(name=tag_name, is_tech=False)
            project.add_tag(tag)

        # Attach tech tags objects to the project
        for tag_name in tech_tags_data:
            tag = Tag.get_or_create(name=tag_name, is_tech=True)
            project.add_tag(tag)

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


@bp.route('update/slug/<int:project_id>', methods=['PATCH'])
@admin_required
def update_project_by_id(project_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    project = Project.query.get_or_404(project_id, description="Project not found")

    try:
        update_project(project, data)

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


@bp.route('/update/slug/<string:project_slug>', methods=['PATCH'])
# @admin_required
def update_project_by_slug(project_slug):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    project = Project.query.filter_by(slug=project_slug).first_or_404(description="Project not found")

    try:
        update_project(project, data)

        # Serialize the updated project for the response
        return jsonify(project.dump()), 200

    except ValidationError as e:
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
