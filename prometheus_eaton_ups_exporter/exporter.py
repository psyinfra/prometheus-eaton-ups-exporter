"""Create and run a Prometheus Exporter for an Eaton UPS."""
import json

from prometheus_client.core import GaugeMetricFamily
from prometheus_eaton_ups_exporter.scraper import UPSScraper

from prometheus_eaton_ups_exporter import create_logger

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
            insecure=False,
            verbose=False
    ):
        self.ups_scraper = UPSScraper(
            ups_address,
            authentication,
            insecure=insecure,
            verbose=verbose
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

            gauge = GaugeMetricFamily(
                "ups_input_voltage_volts",
                'UPS input voltage (V)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], inputs_rm['voltage'])
            yield gauge

            gauge = GaugeMetricFamily(
                "ups_input_frequency_herz",
                'UPS input frequency (H)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id],  inputs_rm['frequency'])
            yield gauge

            gauge = GaugeMetricFamily(
                "ups_input_current_amperes",
                'UPS input current (A)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], inputs_rm['current'])
            yield gauge

            gauge = GaugeMetricFamily(
                "ups_output_voltage_volts",
                'UPS output voltage (V)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], outputs_rm['voltage'])
            yield gauge

            gauge = GaugeMetricFamily(
                "ups_output_frequency_herz",
                'UPS output frequency (H)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], outputs_rm['frequency'])
            yield gauge

            gauge = GaugeMetricFamily(
                "ups_output_current_amperes",
                'UPS output current (A)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], outputs_rm['current'])
            yield gauge

            gauge = GaugeMetricFamily(
                "ups_output_apparent_power_voltamperes",
                'UPS output apperent power (VA)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], outputs_rm['apparentPower'])
            yield gauge

            gauge = GaugeMetricFamily(
                "ups_output_active_power_watts",
                'UPS output active power (W)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], outputs_rm['activePower'])
            yield gauge

            gauge = GaugeMetricFamily(
                "ups_output_power_factor",
                'UPS output power factor',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], outputs_rm['powerFactor'])
            yield gauge

            gauge = GaugeMetricFamily(
                "ups_output_load_ratio",
                'UPS output load ratio',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], int(outputs_rm['percentLoad'])/100)
            yield gauge

            gauge = GaugeMetricFamily(
                "ups_battery_voltage_volts",
                'UPS battery voltage (V)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], powerbank_m['voltage'])
            yield gauge

            gauge = GaugeMetricFamily(
                "ups_battery_capacity_ratio",
                'UPS remaining battery charge capacity ratio',
                labels=['ups_id']
            )
            gauge.add_metric(
                [ups_id], int(powerbank_m['remainingChargeCapacity'])/100
            )
            yield gauge

            gauge = GaugeMetricFamily(
                "ups_battery_remaining_seconds",
                'UPS remaining battery time (s)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], powerbank_m['remainingTime'])
            yield gauge

            gauge = GaugeMetricFamily(
                "ups_battery_health",
                'UPS health status',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], powerbank_s['health'])
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
