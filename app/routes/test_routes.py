from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

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
