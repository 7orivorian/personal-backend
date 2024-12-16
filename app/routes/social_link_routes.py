from flask import Blueprint, jsonify, request

from app import db
from app.exception.validation_error import ValidationError
from app.models.social_link import SocialLink
from app.utils.validators import admin_required

API_PREFIX: str = '/api/v1/sociallinks'
bp = Blueprint('social_link_routes', __name__, url_prefix=API_PREFIX)


@bp.route('/', methods=['GET'])
def get_social_links():
    social_links = SocialLink.query.all()
    return jsonify([sl.dump() for sl in social_links]), 200


@bp.route('/<int:social_link_id>', methods=['GET'])
def get_social_link(social_link_id):
    social_link = SocialLink.query.get_or_404(social_link_id)
    return jsonify(social_link.dump()), 200


@bp.route('/', methods=['POST'])
@admin_required
def create_social_link():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        new_sl = SocialLink(**data)

        # Persist in the database
        new_sl.save()

        # Serialize for the response
        return jsonify(new_sl.dump()), 201

    except ValidationError as e:  # Handle schema validation errors
        return jsonify({
            "message": e.message,
            "error": "Validation error"
        }), 400

    except Exception as e:
        print(e)  # Log unexpected errors for debugging
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 500


@bp.route('/<int:social_link_id>', methods=['PATCH'])
@admin_required
def update_social_link_by_id(social_link_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    social_link = SocialLink.query.get_or_404(social_link_id)

    try:
        if 'name' in data:
            social_link.name = data['name']
        if 'description' in data:
            social_link.description = data['description']
        if 'url' in data:
            social_link.url = data['url']
        if 'icon' in data:
            social_link.icon = data['icon']

        # Persist in the database
        social_link.save()

        # Serialize for the response
        return jsonify(social_link.dump()), 200

    except ValidationError as e:  # Handle schema validation errors
        return jsonify({
            "message": e.message,
            "error": "Validation error"
        }), 400

    except Exception as e:
        print(e)  # Log unexpected errors for debugging
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 500


@bp.route('/<int:social_link_id>', methods=['DELETE'])
@admin_required
def delete_social_link_by_id(social_link_id):
    social_link = SocialLink.query.get_or_404(social_link_id)
    social_link.delete()
    return jsonify({"message": "Project deleted successfully"}), 204
