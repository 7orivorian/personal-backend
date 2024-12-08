from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from app import db
from app.models.project import Project, ProjectSchema

API_PREFIX: str = '/api/v1/projects'
bp = Blueprint('project_routes', __name__, url_prefix=API_PREFIX)


@bp.route('/', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    return jsonify([project.to_dict() for project in projects]), 200


@bp.route('/<int:project_id>', methods=['GET'])
def get_project(project_id):
    project = Project.query.get_or_404(project_id)
    return jsonify(ProjectSchema().dump(project)), 200


@bp.route('/', methods=['POST'])
def create_project():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    project_schema = ProjectSchema()

    try:
        # Validate and deserialize input data into Project object
        new_project = project_schema.load(data)

        # Persist the new project in the database
        new_project.save()

        # Serialize the created project for the response
        return jsonify(project_schema.dump(new_project)), 201

    except ValidationError as e:  # Handle schema validation errors
        return jsonify({"errors": e.messages}), 400

    except Exception as e:
        print(e)  # Log unexpected errors for debugging
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 500


@bp.route('/<int:project_id>', methods=['PATCH'])
def update_project(project_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    project = Project.query.get_or_404(project_id)
    project_schema = ProjectSchema(partial=True)

    try:
        # Validate and deserialize input data into Project object
        updated_project = project_schema.load(data, instance=project)

        # Persist the updated project in the database
        updated_project.save()

        # Serialize the updated project for the response
        return jsonify(project_schema.dump(updated_project)), 200

    except ValidationError as e:  # Handle schema validation errors
        return jsonify({"errors": e.messages}), 400

    except Exception as e:
        print(e)  # Log unexpected errors for debugging
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 500


@bp.route('delete/id/<int:project_id>', methods=['DELETE'])
def delete_project_by_id(project_id):
    project = Project.query.get_or_404(project_id, description="Project not found")
    project.delete()
    return jsonify({"message": "Project deleted successfully"}), 204

@bp.route('delete/slug/<string:slug>', methods=['DELETE'])
def delete_project_by_slug(slug):
    project = Project.query.filter_by(slug=slug).first_or_404(description="Project not found")
    project.delete()
    return jsonify({"message": "Project deleted successfully"}), 204
