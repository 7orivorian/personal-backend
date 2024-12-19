import re

from flask_bcrypt import generate_password_hash


def hash_password(plain_text_password):
    return generate_password_hash(plain_text_password, 16)


# Regex for YYYY-MM-DD format
date_regex = r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$"


def is_valid_date(date_string):
    return bool(re.match(date_regex, date_string))


def is_present(data, key):
    return not (data[key] is None or data[key] == '')