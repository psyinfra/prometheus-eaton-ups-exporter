"""
Hardcoded globals used by the scraper.

This will need new configurations when the API changes.
"""

# these will be added to the original url (ex: https://eaton.ups.com)
LOGIN_AUTH_PATH = '/rest/mbdetnrs/1.0/oauth2/token'
REST_API_PATH = '/rest/mbdetnrs/1.0/powerDistributions/1'

# Headers for the login form.
LOGIN_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; "
                  "rv:82.0) Gecko/20100101 Firefox/82.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/json;charset=utf-8",
    "Content-Length": "103",
    "Connection": "keep-alive",
}

# Data to post to the login form.
# Must be extended by username and password.
LOGIN_DATA = {
    "grant_type": "password",
    "scope": "GUIAccess"
}

# Authentication header to access the REST API.
# Must be extended by the authentication tokens.
AUTH_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; "
                  "rv:82.0) Gecko/20100101 Firefox/82.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}
