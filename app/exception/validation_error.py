class ValidationError(Exception):
    """
    Exception for validation errors.
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message
