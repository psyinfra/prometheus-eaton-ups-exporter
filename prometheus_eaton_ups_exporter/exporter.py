"""Create and run a Prometheus Exporter for an Eaton UPS."""
import sys
import argparse
import time
import getpass
import json

from prometheus_client import start_http_server, REGISTRY
from prometheus_client.core import GaugeMetricFamily

from prometheus_eaton_ups_exporter.scraper import UPSScraper

NORMAL_EXECUTION = 0


class UPSExporter:
    """
    Prometheus single exporter.

    :param ups_address: str
        Address to a UPS, either an IP address or a DNS hostname
    :param authentication: (username: str, password: str)
        Username and password for the web UI of the UPS
    :param insecure: bool
        Whether to connect to UPSs with self-signed SSL certificates
    """
    def __init__(
            self,
            ups_address,
            authentication,
            insecure):
        self.ups_scraper = UPSScraper(
            ups_address,
            authentication,
            insecure=insecure
        )

    def collect(self):
        """Export UPS metrics on request"""

        ups_data = self.scrape_data()
        for measures in ups_data:
            ups_id = measures.get('ups_id')
            inputs = measures.get('ups_inputs')
            outputs = measures.get('ups_outputs')
            powerbank_details = measures.get('ups_powerbank')
            inputs_rm = inputs['measures']['realtime']
            outputs_rm = outputs['measures']['realtime']
            powerbank_m = powerbank_details['measures']
            powerbank_s = powerbank_details['status']

            relevant_measures = {
                "ups_input_voltage_in_volt":
                    inputs_rm['voltage'],
                "ups_input_frequency_in_herz":
                    inputs_rm['frequency'],
                "ups_input_current_in_ampere":
                    inputs_rm['current'],
                "ups_output_voltage_in_volt":
                    outputs_rm['voltage'],
                "ups_output_frequency_in_herz":
                    outputs_rm['frequency'],
                "ups_output_current_in_ampere":
                    outputs_rm['current'],
                "ups_output_apparent_power_in_voltampere":
                    outputs_rm['apparentPower'],
                "ups_output_active_power_in_watt":
                    outputs_rm['activePower'],
                "ups_output_power_factor":
                    outputs_rm['powerFactor'],
                "ups_output_percent_load_in_percent":
                    outputs_rm['percentLoad'],
                "ups_battery_voltage_in_volt":
                    powerbank_m['voltage'],
                "ups_battery_capacity_in_percent":
                    powerbank_m['remainingChargeCapacity'],
                "ups_battery_remaining_time":
                    powerbank_m['remainingTime'],
                "ups_battery_health":
                    powerbank_s['health']
            }

            for measure_label, value in relevant_measures.items():

                gauge = GaugeMetricFamily(
                    measure_label,
                    'Measure collected from the ups device',
                    labels=['ups_id']
                )
                gauge.add_metric([ups_id], value)
                yield gauge

    def scrape_data(self) -> list:
        """
        Scrape measure data.

        :return: list
            Returns measures as a list with one entry
        """
        return [self.ups_scraper.get_measures()]


class UPSMultiExporter(UPSExporter):
    """
    Prometheus exporter for multiple UPSs.

    Collects metrics from multiple UPSs at the same time. If threading is
    enabled, multiple threads will be used to collect sensor readings which is
    considerably faster.

    :param config: str
        Path to the configuration file, containing UPS ip/hostname, username,
        and password combinations for all UPSs to be monitored
    :param insecure: bool
        Whether to connect to UPSs with self-signed SSL certificates
    """
    def __init__(self, config=str, insecure=False):
        self.ups_devices = self.get_ups_devices(config, insecure)

    @staticmethod
    def get_ups_devices(config, insecure) -> list:
        """
        Creates multiple UPSScraper.

        :param config: str
            Path to a JSON-based config file
        :param insecure:
            Whether to connect to UPSs with self-signed SSL certificates
        :return: list
            List of UPSScrapers
        """
        with open(config) as json_file:
            data = json.load(json_file)

        return [
            UPSScraper(v['address'], (v['user'], v['password']), k, insecure)
            for k, v in data.items()
        ]

    def scrape_data(self) -> list:
        """
        Scrape measure data.

        :return: list
            List with measurements from each UPS
        """
        return [
            ups.get_measures() for ups in self.ups_devices
        ]


def parse_args() -> argparse.Namespace:
    """Prepare command line arguments."""
    parser = argparse.ArgumentParser(
        description="Prometheus Exporter for Eaton UPSs."
    )

    parser.add_argument(
        "-c", "--config",
        help="Configuration JSON file containing UPS addresses and login info"
    )

    parser.add_argument(
        "address",
        help="Specify the address of the UPS device"
    )
    parser.add_argument(
        "-u", "--username",
        help="Specify a user name",
        required=True
    )
    parser.add_argument(
        "-p", "--port",
        help="Listen on this port",
        default=8000
    )
    parser.add_argument(
        "--host-address",
        help="Address on which the Prometheus metrics will be accessible",
        default="127.0.0.1"
    )
    parser.add_argument(
        '-k', '--insecure',
        action='store_true',
        help='Allow the exporter to connect to UPSs with self-signed SSL certificates',
        default=False
    )

    return parser.parse_args()


if __name__ == '__main__':
    try:
        args = parse_args()
        pswd = getpass.getpass('Password:')
        port = int(args.port)
        ups_exporter = UPSExporter(
            args.address,
            (args.username, pswd),
            insecure=args.insecure
        )

        REGISTRY.register(
            ups_exporter
        )

        # Start up the server to expose the metrics.
        start_http_server(port, addr=args.host_address)
        print(f"Starting Prometheus Eaton UPS Exporter on "
              f"{args.host_address}:{port}")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Prometheus Eaton UPS Exporter shut down")
        sys.exit(NORMAL_EXECUTION)
