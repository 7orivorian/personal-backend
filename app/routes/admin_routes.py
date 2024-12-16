from flask import Blueprint, jsonify, abort

from app.models.user import User
from app.utils.validators import validate_user_id, admin_required

API_PREFIX: str = '/api/v1/admin'
bp = Blueprint('admin_routes', __name__, url_prefix=API_PREFIX)


@bp.route('/delete/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    if not validate_user_id(user_id):
        return abort(400, "Invalid user ID")

    user = User.query.get(user_id)
    if user:
        user.delete()
        return jsonify({"message": "User deleted successfully"}), 204
    else:
        return jsonify({
            "message": "User not found",
            "error": "User not found"
        }), 404
