
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

    def __init__(self, ups_id=None, rack_id=None):
        self.ups_id = ups_id
        self.rack_id = rack_id
        pass

    def collect(self):
        """
        Prometheus will call this function in a specified cycle
        :return:
        """

        latest_measures = self.get_latest_measures(
            measure_file="../logMeasures.csv"
        )

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
        self.rack_id = 1
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

    @staticmethod
    def get_latest_measures(measures=None, measure_file=None) -> list:
        """
        Get last line (latest entry) of the measure csv output.

        :param measures: measures as str
        :param measure_file: measure file path as str
        :return: last entry row as list
        """
        if measures:
            _measures = StringIO(measures)
        elif measure_file:
            with open(measure_file) as readfile:
                content = readfile.read()
                _measures = StringIO(content)

        reader = csv.reader(_measures, dialect='excel')
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

        # ups_scraper = UPSScraper(
        #     args.address,
        #     args.username,
        #     pswd
        # )
        # measures = ups_scraper.get_measures()

        ups_exporter = UPSExporter()

        REGISTRY.register(
            UPSExporter()
        )

        # Start up the server to expose the metrics.
        start_http_server(port)
        # Generate some requests.
        while True:
            time.sleep(15)
    except TypeError as err:
        print(err.with_traceback())

    except KeyboardInterrupt:
        exit(0)

