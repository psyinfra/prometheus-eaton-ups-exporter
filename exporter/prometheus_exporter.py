
import argparse
import random
import time
import csv
import getpass
from io import StringIO

from ups_scraper import UPSScraper
from prometheus_client import start_http_server, REGISTRY
from prometheus_client.core import GaugeMetricFamily, Gauge


class UPSExporter:

    def __init__(
            self,
            ups_address,
            username,
            password,
            ups_id=None,
            rack_id=None):
        self.ups_scraper = UPSScraper(
            ups_address,
            username,
            password
        )
        self.ups_id = ups_id
        self.rack_id = rack_id

    def collect(self):
        """
        Prometheus will call this function in a specified cycle
        :return:
        """

        latest_measures = self.get_latest_measures()

        # define measure label tags
        measure_labels = [
            # "ups_time_in_utc"
            "ups_input_voltage_in_volt",
            "ups_input_frequency_in_herz",
            "ups_bypass_voltage_in_volt",
            "ups_bypass_frequency_in_herz",
            "ups_output_voltage_in_volt",
            "ups_output_frequency_in_herz",
            "ups_output_current_in_ampere",
            "ups_output_apparent_power_in_voltampere",
            "ups_output_active_power_in_watt",
            "ups_output_power_factor",
            "ups_output_percent_load_in_percent",
            "ups_battery_voltage_in_volt",
            "ups_battery_capacity_in_percent",
            "ups_battery_remaining_time"
        ]

        label_tags = []
        label_vals = []
        if self.ups_id:
            label_tags.append('ups_id')
            label_vals.append(str(self.ups_id))
        if self.rack_id:
            label_tags.append('rack_id')
            label_vals.append(str(self.rack_id))

        for measure_label, value in zip(measure_labels, latest_measures[1:]):
            if not value.lower() == 'nan':
                g = GaugeMetricFamily(
                    measure_label,
                    'Measure collected from the ups device',
                    labels=label_tags
                )
                g.add_metric(label_vals, value)
                yield g

    def get_latest_measures(self) -> list:
        """
        Get last line (latest entry) of the measure csv output.

        :return: last entry row as list
        """
        _measures = self.ups_scraper.get_measures()
        measures = StringIO(_measures)
        reader = csv.reader(measures, dialect='excel')
        header = next(reader)
        if "SEP=" in ",".join(header):
            header = next(reader)
        rest = list(reader)

        # return latest entry
        return rest[-1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prometheus exporter for Eaton UPS measures"
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
        help="Listen to this port",
        default=8000
    )
    parser.add_argument(
        "--host-address",
        help="Address by what the prometheus metrics will be accessible",
        default="127.0.0.1"
    )
    # parser.add_argument(
    #     '-k', '--insecure',
    #     dest='insecure',
    #     required=False,
    #     action='store_true',
    #     help='allow a connection to an insecure raritan API',
    #     default=False
    # )

    return parser.parse_args()


if __name__ == '__main__':
    try:
        args = parse_args()
        pswd = getpass.getpass('Password:')
        port = int(args.port)
        ups_exporter = UPSExporter(
            args.address,
            args.username,
            pswd
        )

        REGISTRY.register(
            ups_exporter
        )

        # Start up the server to expose the metrics.
        start_http_server(port, addr=args.host_address)
        # Generate some requests.
        while True:
            time.sleep(1)
    except TypeError as err:
        print(err)

    except KeyboardInterrupt:
        exit(0)
