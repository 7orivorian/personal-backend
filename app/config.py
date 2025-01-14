import os


class Config:
    FLASK_ENV = os.getenv("FLASK_ENV")

    username = os.getenv("MARIADB_USER")
    password = os.getenv("MARIADB_PASSWORD")
    host = os.getenv("MARIADB_HOST")
    port = os.getenv("MARIADB_PORT")
    database = os.getenv("MARIADB_DATABASE")

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
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
