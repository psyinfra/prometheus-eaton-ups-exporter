#! bin/python3

import json
import argparse
from requests_html import HTMLSession
import urllib3

# disable warnings created because of ignoring cerificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class UPSScraper:

    login_auth_path = '/rest/mbdetnrs/1.0/oauth2/token'
    logmeasures_path = '/logs/logMeasures.csv'

    def __init__(self, ups_url, username, password, output=None):
        self.ups_url = ups_url
        self.username = username
        self.password = password
        self.session = HTMLSession()
        self.session.verify = False # ignore self signed certificate

        token_type, access_token = self.login()
        logmeasures = self.load_logmeasures(token_type, access_token)
        self.save_logmeasures(logmeasures, output)

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

        login_request = self.session.post(
            self.ups_url + self.login_auth_path,
            headers=headers,
            data=json.dumps(data))  # needs to be json encoded
        login_response = login_request.json()
        token_type = login_response['token_type']
        access_token = login_response['access_token']

        return token_type, access_token

    def load_logmeasures(self, token_type, access_token):
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
            self.ups_url + self.logmeasures_path,
            headers=csv_headers)

        return csv.text

    def save_logmeasures(self, logmeasures, output=None):
        if output:
            with open(output, 'w') as file:
                file.write(logmeasures)
        else:
            print(logmeasures)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Get the log measures from the UPS Web UI"
    )

    parser.add_argument(
        "host",
        help="Specify a host"
    )

    parser.add_argument(
        "-u", "--username",
        help="specify a user name",
        required=True,
    )

    parser.add_argument(
        "-p", "--password",
        help="specify the user password",
        required=True,
        type=str
    )

    parser.add_argument(
        "-f", '--file',
        help="save output in the given path",
        required=False,
    )
    try:
        args_parsed = parser.parse_args()  # parse sys.args
        scraper = UPSScraper(
            args_parsed.host,
            args_parsed.username,
            args_parsed.password,
            args_parsed.file
        )
    except argparse.ArgumentError:
        parser.print_help()
