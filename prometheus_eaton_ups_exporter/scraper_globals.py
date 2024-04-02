"""
Hardcoded globals used by the scraper.

This will need new configurations when the API changes.
"""

# these will be added to the original url (ex: https://eaton.ups.com)
LOGIN_AUTH_PATH = '/rest/mbdetnrs/1.0/oauth2/token'
REST_API_PATH = '/rest/mbdetnrs/1.0/powerDistributions/1'

# As there could be multiple inputs and outputs,
# take the first one
INPUT_MEMBER_ID = 1
OUTPUT_MEMBER_ID = 1

# Data to post to the login form.
# Must be extended by username and password.
LOGIN_DATA = {
    "grant_type": "password",
    "scope": "GUIAccess"
}

# Timeouts in seconds
REQUEST_TIMEOUT = 2

# Exit Codes
NORMAL_EXECUTION = 0
AUTHENTICATION_FAILED = 1
SSL_ERROR = 2
CERTIFICATE_VERIFY_FAILED = 3
CONNECTION_ERROR = 4
TIMEOUT_ERROR = 5
MISSING_SCHEMA_ERROR = 6
INVALID_URL_ERROR = 7


class LoginFailedException(Exception):
    """Exception raised for failed login.

    :param error_code: Error code
    :param message: Error description message
    """

    def __init__(self,
                 error_code: int,
                 message: str) -> None:
        self.error_code = error_code
        self.message = message
        super().__init__(self.error_code, self.message)
