from flask import Blueprint

API_PREFIX: str = '/api/v1/admin'
bp = Blueprint('admin_routes', __name__, url_prefix=API_PREFIX)
