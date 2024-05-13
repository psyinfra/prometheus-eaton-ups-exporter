"""Create and run a Prometheus Exporter for an Eaton UPS."""
import json

from concurrent.futures import ThreadPoolExecutor, as_completed
from concurrent.futures._base import TimeoutError
from prometheus_client.core import GaugeMetricFamily

from prometheus_eaton_ups_exporter import create_logger
from prometheus_eaton_ups_exporter.scraper import UPSScraper

from typing import Generator, Tuple

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
            ups_address: str,
            authentication: Tuple[str, str],
            name: str | None = None,
            insecure: bool = False,
            verbose: bool = False,
            login_timeout: int = 3
    ) -> None:
        self.logger = create_logger(
            f"{__name__}.{self.__class__.__name__}", not verbose
        )
        self.ups_scraper = UPSScraper(
            ups_address,
            authentication,
            name,
            insecure=insecure,
            verbose=verbose,
            login_timeout=login_timeout
        )

    def collect(self) -> Generator[GaugeMetricFamily, None, None]:
        """Export UPS metrics on request."""
        ups_data = self.scrape_data()
        for measures in ups_data:
            if not measures:
                continue

            ups_id = measures.get('ups_id')
            inputs = measures.get('ups_inputs')
            outputs = measures.get('ups_outputs')
            powerbank_details = measures.get('ups_powerbank')
            inputs_rm = inputs['measures']['realtime']
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
            gauge.add_metric([ups_id], inputs_rm['current'])
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
                [ups_id], int(powerbank_m['remainingChargeCapacity']) / 100
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
            gauge.add_metric([ups_id], powerbank_s['health'])
            yield gauge

    def scrape_data(self):
        """Scrape measure data.

        :return: measures
        """
        yield self.ups_scraper.get_measures()


class UPSMultiExporter(UPSExporter):
    """Prometheus exporter for multiple UPSs.

    Collects metrics from multiple UPSs at the same time. If threading is
    enabled, multiple threads will be used to collect sensor readings which is
    considerably faster.

    :param config: str
        Path to the configuration file, containing UPS ip/hostname, username,
        and password combinations for all UPSs to be monitored
    :param insecure: bool
        Whether to connect to UPSs with self-signed SSL certificates
    :param threading: bool
        Whether to use multiple threads to scrape the data 'parallel'.
        This is surely the best way to increase the speed
    :param verbose: bool
        Allow logging output for development
    :param login_timeout: int
        Login timeout for authentication
    """

    def __init__(
            self,
            config: str,
            insecure: bool = False,
            threading: bool = False,
            verbose: bool = False,
            login_timeout: int = 3
    ) -> None:
        self.logger = create_logger(
            f"{__name__}.{self.__class__.__name__}", not verbose
        )
        self.insecure = insecure
        self.threading = threading
        self.verbose = verbose
        self.login_timeout = login_timeout
        self.ups_devices = self.get_ups_devices(config)

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

    def scrape_data(self):
        """Scrape measure data.

        :return: measures
        """
        if self.threading:
            with ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(ups.get_measures)
                    for ups in self.ups_devices
                ]
                try:
                    for future in as_completed(futures, self.login_timeout+1):
                        yield future.result()
                except TimeoutError as err:
                    self.logger.exception(err)
                    yield None

        else:
            for ups in self.ups_devices:
                yield ups.get_measures()
