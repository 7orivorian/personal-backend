from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from app import db
from app.models.social_link import SocialLink, SocialLinkSchema

API_PREFIX: str = '/api/v1/sociallinks'
bp = Blueprint('social_link_routes', __name__, url_prefix=API_PREFIX)


@bp.route('/', methods=['GET'])
def get_social_links():
    social_links = SocialLink.query.all()
    return jsonify([sl.to_dict() for sl in social_links]), 200


@bp.route('/<int:social_link_id>', methods=['GET'])
def get_social_link(social_link_id):
    social_link = SocialLink.query.get_or_404(social_link_id)
    return jsonify(SocialLinkSchema().dump(social_link)), 200


@bp.route('/', methods=['POST'])
def create_social_link():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    sl_schema = SocialLinkSchema()

    try:
        # Validate and deserialize input data into SocialLink object
        new_sl = sl_schema.load(data)

        # Persist in the database
        new_sl.save()

        # Serialize for the response
        return jsonify(sl_schema.dump(new_sl)), 201

    except ValidationError as e:  # Handle schema validation errors
        return jsonify({"errors": e.messages}), 400

    except Exception as e:
        print(e)  # Log unexpected errors for debugging
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 500


@bp.route('/<int:social_link_id>', methods=['PATCH'])
def update_social_link(social_link_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    social_link = SocialLink.query.get_or_404(social_link_id)
    sl_schema = SocialLinkSchema(partial=True)

    try:
        # Validate and deserialize input data into object
        updated_sl = sl_schema.load(data, instance=social_link)

        # Persist in the database
        updated_sl.save()

        # Serialize for the response
        return jsonify(sl_schema.dump(updated_sl)), 200

    except ValidationError as e:  # Handle schema validation errors
        return jsonify({"errors": e.messages}), 400

    except Exception as e:
        print(e)  # Log unexpected errors for debugging
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 500


@bp.route('/<int:social_link_id>', methods=['DELETE'])
def delete_social_link(social_link_id):
    social_link = SocialLink.query.get_or_404(social_link_id)
    social_link.delete()
    return jsonify({"message": "Project deleted successfully"}), 204
