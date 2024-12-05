from app.routes.user_routes import bp as user_routes
from app.routes.test_routes import bp as test_routes
from app.routes.project_routes import bp as project_routes

__all__ = ['user_routes', 'test_routes', 'project_routes']
