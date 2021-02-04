#! bin/python3

import json
import getpass
import argparse
from requests import Session, ConnectionError
import urllib3

# disable warnings created because of ignoring certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class UPSScraper:

    login_auth_path = '/rest/mbdetnrs/1.0/oauth2/token'
    logmeasures_path = '/logs/logMeasures.csv'

    def __init__(self, ups_address, username, password, verify=False):
        self.ups_address = ups_address
        self.username = username
        self.password = password
        self.session = Session()
        self.session.verify = verify  # ignore self signed certificate
        self.logged_in = False

    def get_measures(self):
        token_type, access_token = self.login()
        logmeasures = self.load_measures(token_type, access_token)
        return logmeasures

    def login(self) -> (str, str):
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
            self.logged_in = True  # Todo
            return token_type, access_token
        except KeyError:
            print("Authentication failed")
            exit(0)
        except ConnectionError:
            print("Connection refused")
            exit(0)

    def load_measures(self, token_type, access_token):
        csv_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.16; "
                          "rv:82.0) Gecko/20100101 Firefox/82.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Authorization": token_type + " " + access_token
        }
        csv = self.session.get(
            self.ups_address + self.logmeasures_path,
            headers=csv_headers
        )

        return csv.text

    @staticmethod
    def save_measures(measures, output=None):
        if output:
            with open(output, 'w') as file:
                file.write(measures)
            return True
        return False


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
        "-f", '--file',
        help="save output in the given path",
        required=False,
    )

    pswd = getpass.getpass('Password:')
    try:
        args_parsed = parser.parse_args()  # parse sys.args
        scraper = UPSScraper(
            args_parsed.host,
            args_parsed.username,
            pswd
        )

        measures = scraper.get_measures()
        if not scraper.save_measures(
                measures, args_parsed.file):
            print(measures)
    except argparse.ArgumentError:
        parser.print_help()
    except ConnectionError:
        print("Can't resolve host name")
