"""Create and run a Prometheus Exporter for an Eaton UPS."""
import asyncio
import json

from prometheus_client.core import GaugeMetricFamily

from prometheus_eaton_ups_exporter import create_logger
from prometheus_eaton_ups_exporter.scraper import UPSScraper

from typing import Generator

NORMAL_EXECUTION = 0


class UPSExporter:
    """Prometheus single exporter.

    :param ups_address: str
        Address to a UPS, either an IP address or a DNS hostname
    :param authentication: (username: str, password: str)
        Username and password for the web UI of the UPS
    :param insecure: bool
        Whether to connect to UPSs with self-signed SSL certificates
    :param verbose: bool
        Allow logging output for development.
    :param login_timeout: int
        Login timeout for authentication
    """
    def __init__(
            self,
            config: str,
            insecure: bool = False,
            verbose: bool = False,
            login_timeout: int = 3
    ) -> None:
        self.logger = create_logger(
            f"{__name__}.{self.__class__.__name__}", not verbose
        )
        self.insecure = insecure
        self.verbose = verbose
        self.login_timeout = login_timeout
        self.upss = self.get_ups_devices(config)

    def collect(self) -> Generator[GaugeMetricFamily, None, None]:
        """Export UPS metrics on request."""
        ups_data = asyncio.run(self.scrape_data())
        for measures in ups_data:
            if not measures:
                continue

            ups_id = measures.get('ups_id')
            inputs = measures.get('ups_inputs')
            outputs = measures.get('ups_outputs')
            powerbank_details = measures.get('ups_powerbank')

            inputs_rm = inputs['measures']
            if 'realtime' in inputs['measures']:
                inputs_rm = inputs['measures']['realtime']

            outputs_rm = outputs['measures']
            if 'realtime' in outputs['measures']:
                outputs_rm = outputs['measures']['realtime']

            powerbank_m = powerbank_details['measures']
            powerbank_s = powerbank_details['status']

            gauge = GaugeMetricFamily(
                "eaton_ups_input_volts",
                'UPS input voltage (V)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], inputs_rm['voltage'])
            yield gauge

            gauge = GaugeMetricFamily(
                "eaton_ups_input_hertz",
                'UPS input frequency (Hz)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], inputs_rm['frequency'])
            yield gauge

            gauge = GaugeMetricFamily(
                "eaton_ups_input_amperes",
                'UPS input current (A)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], inputs_rm.get('current', 0))
            yield gauge

            gauge = GaugeMetricFamily(
                "eaton_ups_output_volts",
                'UPS output voltage (V)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], outputs_rm['voltage'])
            yield gauge

            gauge = GaugeMetricFamily(
                "eaton_ups_output_hertz",
                'UPS output frequency (Hz)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], outputs_rm['frequency'])
            yield gauge

            gauge = GaugeMetricFamily(
                "eaton_ups_output_amperes",
                'UPS output current (A)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], outputs_rm['current'])
            yield gauge

            gauge = GaugeMetricFamily(
                "eaton_ups_output_voltamperes",
                'UPS output apparent power (VA)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], outputs_rm['apparentPower'])
            yield gauge

            gauge = GaugeMetricFamily(
                "eaton_ups_output_watts",
                'UPS output active power (W)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], outputs_rm['activePower'])
            yield gauge

            gauge = GaugeMetricFamily(
                "eaton_ups_output_power_factor",
                'UPS output power factor',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], outputs_rm['powerFactor'])
            yield gauge

            gauge = GaugeMetricFamily(
                "eaton_ups_output_load_ratio",
                "Ratio of the output apparent power vs. "
                "the UPS's capacity in VA.",
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], int(outputs_rm['percentLoad']) / 100)
            yield gauge

            gauge = GaugeMetricFamily(
                "eaton_ups_battery_volts",
                'UPS battery voltage (V)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], powerbank_m['voltage'])
            yield gauge

            gauge = GaugeMetricFamily(
                "eaton_ups_battery_capacity_ratio",
                'Ratio of the remaining charge vs the total battery capacity',
                labels=['ups_id']
            )
            gauge.add_metric(
                [ups_id],
                int(powerbank_m.get('remainingChargeCapacity', 0)) / 100
            )
            yield gauge

            gauge = GaugeMetricFamily(
                "eaton_ups_battery_remaining_seconds",
                'UPS remaining battery time (s)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], powerbank_m['remainingTime'])
            yield gauge

            gauge = GaugeMetricFamily(
                "eaton_ups_battery_health",
                'UPS health status given as the '
                'remaining lifetime (years) [uncertain]',
                labels=['ups_id']
            )
            health_val = powerbank_s['health']
            health = 0
            if isinstance(health_val, int):
                health = health_val
            gauge.add_metric([ups_id], health)
            yield gauge

    @staticmethod
    def get_devices(config: str | dict) -> dict:
        """Take a config file path or config dict of UPSs."""
        if isinstance(config, str):
            with open(config) as json_file:
                devices = json.load(json_file)
        elif isinstance(config, dict):
            devices = config
        else:
            raise AttributeError("Only config path (str) or dict accepted")
        return devices

    def get_ups_devices(self,
                        config: str | dict) -> list:
        """Creates multiple UPSScraper.

        :param config: str | dict
            Path to a JSON-based config file or a config dict
        :return: list
            List of UPSScrapers
        """
        devices = self.get_devices(config)
        return [
            UPSScraper(
                value['address'],
                (value['user'], value['password']),
                key,
                insecure=self.insecure,
                verbose=self.verbose,
                login_timeout=self.login_timeout
            )
            for key, value in devices.items()
        ]

    async def scrape_data(self):
        """Scrape measure data.

        :return: measures
        """
        return await asyncio.gather(*[ups.get_measures() for ups in self.upss])
