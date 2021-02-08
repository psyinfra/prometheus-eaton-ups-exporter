#! bin/python3

import json
import getpass
import argparse
from requests import Session, Response
from requests.exceptions import SSLError, ConnectionError
import urllib3


class UPSScraper:

    login_auth_path = '/rest/mbdetnrs/1.0/oauth2/token'
    rest_api_path = '/rest/mbdetnrs/1.0/powerDistributions/1'

    def __init__(self, ups_address, username, password, insecure=False):
        """Create a UPS Scraper based on the UPS API."""
        self.ups_address = ups_address
        self.username = username
        self.password = password
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
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; "
                          "rv:82.0) Gecko/20100101 Firefox/82.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json;charset=utf-8",
            "Content-Length": "103",
            "Connection": "keep-alive",
        }
        data = {
            "username": self.username,
            "password": self.password,
            "grant_type": "password",
            "scope": "GUIAccess"
        }

        try:
            login_request = self.session.post(
                self.ups_address + self.login_auth_path,
                headers=headers,
                data=json.dumps(data))  # needs to be json encoded
            login_response = login_request.json()

            token_type = login_response['token_type']
            access_token = login_response['access_token']

            print("Authentication successful")
            return token_type, access_token
        except KeyError:
            print("Authentication failed")
            exit(1)
        except SSLError as err:
            print("Connection refused")
            if 'CERTIFICATE_VERIFY_FAILED' in str(err):
                print("Try -k to allow insecure server "
                      "connections when using SSL")
            exit(2)
        except ConnectionError:
            print("Connection refused")
            exit(3)

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
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; "
                              "rv:82.0) Gecko/20100101 Firefox/82.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Authorization": f"{self.token_type} {self.access_token}"
            }
            request = self.session.get(url, headers=headers)

            if "Unauthorized" in request.text:
                # try to login, if not authorized
                self.token_type, self.access_token = self.login()
                return self.load_page(url)

            return request
        except ConnectionError:
            self.token_type, self.access_token = self.login()
            return self.load_page(url)

    def get_measures(self) -> dict:
        """
        Get most relevant ups measures.

        :return: dict
        """
        power_dist_request = self.load_page(
            self.ups_address+self.rest_api_path
        )
        power_dist_overview = power_dist_request.json()
        ups_id = power_dist_overview['id']
        ups_inputs_api = power_dist_overview['inputs']['@id']
        ups_ouptups_api = power_dist_overview['outputs']['@id']

        # take first member
        i_member_id = 1
        inputs_request = self.load_page(
            self.ups_address + ups_inputs_api + f'/{i_member_id}'
        )
        inputs = inputs_request.json()

        # take first member
        o_member_id = 1
        outputs_request = self.load_page(
            self.ups_address + ups_ouptups_api + f'/{o_member_id}'
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
            "ups_id": ups_id,
            "ups_inputs": inputs,
            "ups_outputs": outputs,
            "ups_powerbank": powerbank
        }


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Get the log measures from the UPS Web UI"
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
            args_parsed.username,
            pswd,
            insecure=args_parsed.insecure
        )

        measures = scraper.get_measures()
        print(measures)
    except argparse.ArgumentError:
        parser.print_help()
    except ConnectionError:
        print("Can't resolve host name")
