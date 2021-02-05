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
    rest_api_path = '/rest/mbdetnrs/1.0/powerDistributions/1'

    def __init__(self, ups_address, username, password, verify=False):
        self.ups_address = ups_address
        self.username = username
        self.password = password
        self.session = Session()
        self.session.verify = verify  # ignore self signed certificate
        self.token_type, self.access_token = None, None

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
            return token_type, access_token
        except KeyError:
            print("Authentication failed")
            exit(0)
        except ConnectionError:
            print("Connection refused")
            exit(0)

    def load_page(self, url):
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
                self.token_type, self.access_token = self.login()
                return self.load_page(url)
            return request
        except ConnectionError:
            self.token_type, self.access_token = self.login()
            return self.load_page(url)

    def get_measures(self):
        power_dist_request = self.load_page(
            self.ups_address+self.rest_api_path
        )
        power_dist_overview = power_dist_request.json()
        configuration = power_dist_overview['configuration']
        ups_id = power_dist_overview['id']

        inputs_request = self.load_page(
            self.ups_address +
            '/rest/mbdetnrs/1.0/powerDistributions/1/inputs/1'
        )
        inputs = inputs_request.json()
        inputs_rm = inputs['measures']['realtime']
        ups_input_voltage_in_volt = inputs_rm['voltage']
        ups_input_frequency_in_herz = inputs_rm['frequency']
        ups_input_current_in_ampere = inputs_rm['current']

        outputs_request = self.load_page(
            self.ups_address +
            '/rest/mbdetnrs/1.0/powerDistributions/1/outputs/1'
        )
        outputs = outputs_request.json()
        outputs_rm = outputs['measures']['realtime']
        ups_output_voltage_in_volt = outputs_rm['voltage']
        ups_output_frequency_in_herz = outputs_rm['frequency']
        ups_output_current_in_ampere = outputs_rm['current']
        ups_output_apparent_power_in_voltampere = outputs_rm['apparentPower']
        ups_output_active_power_in_watt = outputs_rm['activePower']
        ups_output_power_factor = outputs_rm['powerFactor']
        ups_output_percent_load_in_percent = outputs_rm['percentLoad']

        # bypass_request = self.load_page(
        #     self.ups_address + '/rest/mbdetnrs/1.0/powerDistributions/1/bypass/1'
        # )
        # bypass_overview = bypass_request.json()
        # bypass_rm = outputs['measures']['realtime']
        # print(json.dumps(bypass_overview, indent=2))

        # "ups_bypass_voltage_in_volt",
        # "ups_bypass_frequency_in_herz",

        battery_request = self.load_page(
            self.ups_address +
            '/rest/mbdetnrs/1.0/powerDistributions/1/backupSystem/powerBank'
        )
        powerbank = battery_request.json()
        battery_m = powerbank['measures']
        ups_battery_voltage_in_volt = battery_m['voltage']
        ups_battery_capacity_in_percent = battery_m['remainingChargeCapacity']
        ups_battery_remaining_time = battery_m['remainingTime']

        return {
            "ups_id": ups_id,
            "ups_inputs": inputs,
            "ups_outputs": outputs,
            "ups_powerbank": powerbank
        }

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
            self.ups_address + self.rest_api_path,
            headers=csv_headers
        )

        return csv.text


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

    pswd = getpass.getpass('Password:')
    try:
        args_parsed = parser.parse_args()  # parse sys.args
        scraper = UPSScraper(
            args_parsed.host,
            args_parsed.username,
            pswd
        )

        measures = scraper.get_measures()

        print(measures)
    except argparse.ArgumentError:
        parser.print_help()
    except ConnectionError:
        print("Can't resolve host name")
