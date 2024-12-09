from dotenv import load_dotenv
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    from app.models.revoked_token import RevokedToken
    jti = jwt_payload["jti"]
    revoked = RevokedToken.query.filter_by(jti=jti).first()
    return revoked is not None  # True if token is revoked


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")
    app.url_map.strict_slashes = False

    # Initialize extensions with the app
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    app.config["CORS_AUTOMATIC_OPTIONS"] = True
    CORS(
        app,
        supports_credentials=True,
        resources={r"/api/*": {"origins": "*"}}
        if app.config['FLASK_ENV'] == "development"
        else {r"/api/*": {"origins": app.config['FRONTEND_URL']}}
    )

    # Register blueprints
    from app.routes import test_routes, user_routes, project_routes, social_link_routes
    app.register_blueprint(test_routes)
    app.register_blueprint(user_routes)
    app.register_blueprint(project_routes)
    app.register_blueprint(social_link_routes)

    return app
