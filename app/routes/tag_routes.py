from flask import Blueprint, jsonify

from app.models import Tag

API_PREFIX: str = '/api/v1/tags'
bp = Blueprint('tag_routes', __name__, url_prefix=API_PREFIX)


@bp.route('/', methods=['GET'])
def get_all_tags():
    tags = Tag.query.all()
    return jsonify([tag.dump() for tag in tags]), 200
