def validate_user_id(user_id):
    try:
        # Convert to Python int and check for SQLite integer limit
        user_id = int(user_id)
        if user_id > 9223372036854775807 or user_id < -9223372036854775807:
            return False
    except ValueError:
        return False

    return True
