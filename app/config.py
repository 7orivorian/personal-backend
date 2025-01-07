import os


class Config:
    FLASK_ENV = os.getenv("FLASK_ENV")
    SQLALCHEMY_DATABASE_URI = os.getenv("MARIADB_PRIVATE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = FLASK_ENV == "production"
    JWT_COOKIE_HTTPONLY = True
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_COOKIE_SAMESITE = "Strict"
    JWT_SESSION_COOKIE = False
    JWT_CSRF_IN_COOKIES = False
