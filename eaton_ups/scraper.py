"""REST API web scraper for Eaton UPS measure data."""
import sys
import json
import getpass
import argparse

import urllib3
from requests import Session, Response
from requests.exceptions import SSLError, ConnectionError,\
    ReadTimeout, MissingSchema

from eaton_ups.scraper_globals import *


class UPSScraper:
    """
    Create a UPS Scraper based on the UPS API.

    :param ups_address: str
        Address to a ups device, either an IP address or a dns entry
    :param authentication: (username: str, password: str)
        Username and password for the WEB UI on that UPS device
    :param name: str
        Name of the UPS device.
        Used as identifier to differentiate
        between multiple ups devices.
    :param insecure: bool
        Whether to allow a connection to an insecure UPS API

    """
    def __init__(self,
                 ups_address,
                 authentication,
                 name=None,
                 insecure=False):
        self.ups_address = ups_address
        self.username, self.password = authentication
        self.name = name
        self.session = Session()

        self.session.verify = not insecure  # ignore self signed certificate
        if not self.session.verify:
            # disable warnings created because of ignoring certificates
            urllib3.disable_warnings(
                urllib3.exceptions.InsecureRequestWarning
            )

        self.token_type, self.access_token = None, None

    def login(self) -> (str, str):
        """
        Login to the UPS Web UI.

        Based on analysing the UPS Web UI this will create a POST request
        with the authentication details to successfully create a session
        on the specified UPS device.

        :return: two for the authentication necessary string values
        """

        try:
            data = LOGIN_DATA
            data["username"] = self.username
            data["password"] = self.password

            login_request = self.session.post(
                self.ups_address + LOGIN_AUTH_PATH,
                headers=LOGIN_HEADERS,
                data=json.dumps(data),  # needs to be json encoded
                timeout=LOGIN_TIMEOUT
            )
            login_response = login_request.json()

            token_type = login_response['token_type']
            access_token = login_response['access_token']

            print("Authentication successful")
            return token_type, access_token
        except KeyError:
            print("Authentication failed")
            sys.exit(AUTHENTICATION_FAILED)
        except SSLError as err:
            print("Connection refused")
            if 'CERTIFICATE_VERIFY_FAILED' in str(err):
                print("Try -k to allow insecure server "
                      "connections when using SSL")
                sys.exit(CERTIFICATE_VERIFY_FAILED)
            sys.exit(SSL_ERROR)
        except ConnectionError:
            print("Connection refused")
            sys.exit(CONNECTION_ERROR)
        except ReadTimeout:
            print(f"Login Timeout > {LOGIN_TIMEOUT} seconds")
            sys.exit(TIMEOUT_ERROR)

    def load_page(self, url) -> Response:
        """
        Load a webpage of the UPS Web UI or API.

        This will try to load the page by the given url.
        If authentication is needed first, the login function gets executed
        before loading the specified page.

        :param url: ups web url
        :return: request.Response
        """
        try:
            headers = AUTH_HEADERS
            headers["Authorization"] = f"{self.token_type} {self.access_token}"
            request = self.session.get(
                url,
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )

            if "Unauthorized" in request.text:
                # try to login, if not authorized
                self.token_type, self.access_token = self.login()
                return self.load_page(url)

            return request
        except ConnectionError:
            self.token_type, self.access_token = self.login()
            return self.load_page(url)
        except ReadTimeout:
            print(f"Request Timeout > {REQUEST_TIMEOUT} seconds")
            sys.exit(TIMEOUT_ERROR)
        except MissingSchema as err:
            print(err)
            sys.exit(MISSING_SCHEMA)

    def get_measures(self) -> dict:
        """
        Get most relevant ups measures.

        :return: dict
        """
        power_dist_request = self.load_page(
            self.ups_address+REST_API_PATH
        )
        power_dist_overview = power_dist_request.json()

        if not self.name:
            self.name = f"ups_{power_dist_overview['id']}"

        ups_inputs_api = power_dist_overview['inputs']['@id']
        ups_ouptups_api = power_dist_overview['outputs']['@id']

        inputs_request = self.load_page(
            self.ups_address + ups_inputs_api + f'/{INPUT_MEMBER_ID}'
        )
        inputs = inputs_request.json()

        outputs_request = self.load_page(
            self.ups_address + ups_ouptups_api + f'/{OUTPUT_MEMBER_ID}'
        )
        outputs = outputs_request.json()

        ups_backup_sys_api = power_dist_overview['backupSystem']['@id']
        backup_request = self.load_page(
            self.ups_address + ups_backup_sys_api
        )
        backup = backup_request.json()
        ups_powerbank_api = backup['powerBank']['@id']
        powerbank_request = self.load_page(
            self.ups_address + ups_powerbank_api
        )
        powerbank = powerbank_request.json()

        return {
            "ups_id": self.name,
            "ups_inputs": inputs,
            "ups_outputs": outputs,
            "ups_powerbank": powerbank
        }


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Get the measures from the UPS Web UI"
    )

    parser.add_argument(
        "host",
        help="Specify the address of the UPS device"
    )

    parser.add_argument(
        "-u", "--username",
        help="specify a user name",
        required=True,
    )
    parser.add_argument(
        '-k', '--insecure',
        action='store_true',
        help='allow a connection to an insecure UPS API',
        default=False
    )

    pswd = getpass.getpass('Password:')
    try:
        args_parsed = parser.parse_args()  # parse sys.args
        scraper = UPSScraper(
            args_parsed.host,
            (args_parsed.username, pswd),
            insecure=args_parsed.insecure
        )

        measures = scraper.get_measures()
        print(json.dumps(measures, indent=1))
    except argparse.ArgumentError:
        parser.print_help()
    except ConnectionError:
        print("Can't resolve host name")
