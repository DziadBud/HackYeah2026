class NotFoundError(Exception):
    """requested entity does not exist"""


class InvalidCredentialsError(Exception):
    """wrong email, wrong password or inactive admin; deliberately not distinguished"""


class TooManyAttemptsError(Exception):
    """login rate limit hit for this email or ip"""


class NotAuthenticatedError(Exception):
    """missing, unknown, expired or revoked admin session"""


class InvalidUploadError(Exception):
    """uploaded file is not what the endpoint accepts"""


class UploadTooLargeError(Exception):
    """uploaded file exceeds the size limit"""


class InvalidRequestError(Exception):
    """request is well-formed but breaks a rule that spans fields"""
