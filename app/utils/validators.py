from functools import wraps

from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity


def validate_user_id(user_id):
    try:
        # Convert to Python int and check for SQLite integer limit
        user_id = int(user_id)
        if user_id > 9223372036854775807 or user_id < -9223372036854775807:
            return False
    except ValueError:
        return False

    return True


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        current_user = get_jwt_identity()
        if not current_user:
            return jsonify({"error": "Invalid user"}), 401
        from app.models import User
        user = User.query.filter_by(id=current_user).first()
        if not user or not user.is_admin:
            return jsonify({"error": "Unauthorized"}), 401
        return fn(*args, **kwargs)

    return wrapper
