import os


class Config:
    FLASK_ENV = os.getenv("FLASK_ENV")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = FLASK_ENV == "production"
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_CSRF_IN_COOKIES = False
