from flask_bcrypt import generate_password_hash


def hash_password(plain_text_password):
    return generate_password_hash(plain_text_password, 16)
