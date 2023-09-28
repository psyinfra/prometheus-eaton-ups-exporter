"""Create and run a Prometheus Exporter for an Eaton UPS."""
import json

from concurrent.futures import ThreadPoolExecutor, as_completed
from concurrent.futures._base import TimeoutError
from prometheus_client.core import GaugeMetricFamily

from prometheus_eaton_ups_exporter import create_logger
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
    :param verbose: bool
        Allow logging output for development.
    :param login_timeout: float
        Login timeout for authentication
    """
    def __init__(
            self,
            ups_address,
            authentication,
            name=None,
            insecure=False,
            verbose=False,
            login_timeout=3
    ):
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

    def collect(self):
        """Export UPS metrics on request"""
        ups_data = self.scrape_data()
        for measures in ups_data:
            if not measures:
                continue

            ups_id = measures.get('ups_id')
            inputs = measures.get('ups_inputs')
            outputs = measures.get('ups_outputs')
            powerbank_details = measures.get('ups_powerbank')
            inputs_measures = inputs['measures']
            outputs_measures = outputs['measures']
            inputs_status = inputs['status']
            outputs_status = outputs['status']
            inputs_spec = inputs['specifications']
            outputs_spec = outputs['specifications']
            powerbank_m = powerbank_details['measures']
            powerbank_s = powerbank_details['status']


            ## Input metrics
            gauge = GaugeMetricFamily(
                "eaton_ups_input_volts",
                'UPS input voltage (V)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], inputs_measures['voltage'])
            yield gauge

            gauge = GaugeMetricFamily(
                "eaton_ups_input_hertz",
                'UPS input frequency (Hz)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], inputs_measures['frequency'])
            yield gauge

            gauge = GaugeMetricFamily(
                "eaton_ups_input_volts_max",
                'UPS input voltage (V)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], inputs_spec['voltage']['maxReading'])
            yield gauge

            gauge = GaugeMetricFamily(
                "eaton_ups_input_volts_min",
                'UPS input voltage (V)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], inputs_spec['voltage']['minReading'])
            yield gauge

            gauge = GaugeMetricFamily(
                "eaton_ups_input_volts_nominal",
                'UPS input voltage (V)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], inputs_spec['voltage']['nominal'])
            yield gauge

            if inputs_status['health'] == 'ok':
                health_value = 0
            else:
                health_value = 1
            gauge = GaugeMetricFamily(
                "eaton_ups_input_health",
                'UPS input health status',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], health_value)
            yield gauge

            ## Output metrics
            gauge = GaugeMetricFamily(
                "eaton_ups_output_volts",
                'UPS output voltage (V)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], output_measures['voltage'])
            yield gauge

            gauge = GaugeMetricFamily(
                "eaton_ups_output_hertz",
                'UPS output frequency (Hz)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], output_measures['frequency'])
            yield gauge

            gauge = GaugeMetricFamily(
                "eaton_ups_output_amperes",
                'UPS output current (A)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], output_measures['current'])
            yield gauge

            gauge = GaugeMetricFamily(
                "eaton_ups_output_voltamperes",
                'UPS output apparent power (VA)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], output_measures['apparentPower'])
            yield gauge

            gauge = GaugeMetricFamily(
                "eaton_ups_output_watts",
                'UPS output active power (W)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], output_measures['activePower'])
            yield gauge

            gauge = GaugeMetricFamily(
                "eaton_ups_output_power_factor",
                'UPS output power factor',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], output_measures['powerFactor'])
            yield gauge

            gauge = GaugeMetricFamily(
                "eaton_ups_output_average_energy",
                'UPS output average energy',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], output_measures['averageEnergy'])
            yield gauge

            gauge = GaugeMetricFamily(
                "eaton_ups_output_cumulated_energy",
                'UPS output cumulated energy',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], output_measures['cumulatedEnergy'])
            yield gauge

            gauge = GaugeMetricFamily(
                "eaton_ups_output_efficiency",
                'UPS output efficiency',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], output_measures['efficiency'])
            yield gauge

            gauge = GaugeMetricFamily(
                "eaton_ups_output_load_ratio",
                "Ratio of the output apparent power vs. "
                "the UPS's capacity in VA.",
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], int(output_measures['percentLoad']) / 100)
            yield gauge

            if outputs_status['health'] == 'ok':
                health_value = 0
            else:
                health_value = 1
            gauge = GaugeMetricFamily(
                "eaton_ups_output_health",
                'UPS output health status',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], health_value)
            yield gauge


            # Battery
            gauge = GaugeMetricFamily(
                "eaton_ups_battery_volts",
                'UPS battery voltage (V)',
                labels=['ups_id']
            )
            gauge.add_metric([ups_id], powerbank_m['voltage'])
            yield gauge

            gauge = GaugeMetricFamily(
                "eaton_ups_battery_state_of_charge",
                'UPS battery state of charge (%)',
                labels=['ups_id']
            )
            gauge.add_metric( [ups_id], powerbank_m['stateOfCharge'])
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
                'UPS health status',
                labels=['ups_id']
            )

            if powerbank_s['health'] == 'ok':
                health_value = 0
            else:
                health_value = 1
            gauge.add_metric([ups_id], health_value)
            yield gauge

    def scrape_data(self):
        """
        Scrape measure data.

        :return: measures
        """
        yield self.ups_scraper.get_measures()


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
    :param threading: bool
        Whether to use multiple threads to scrape the data 'parallel'.
        This is surely the best way to increase the speed
    :param verbose: bool
        Allow logging output for development
    :param login_timeout: float
        Login timeout for authentication
    """

    def __init__(
            self,
            config,
            insecure=False,
            threading=False,
            verbose=False,
            login_timeout=3
    ):
        self.logger = create_logger(
            f"{__name__}.{self.__class__.__name__}", not verbose
        )
        self.insecure = insecure
        self.threading = threading
        self.verbose = verbose
        self.login_timeout = login_timeout
        self.ups_devices = self.get_ups_devices(config)

    @staticmethod
    def get_devices(config):
        """Take a config file path or config dict of UPSs."""
        if isinstance(config, str):
            with open(config) as json_file:
                devices = json.load(json_file)
        elif isinstance(config, dict):
            devices = config
        else:
            raise AttributeError("Only config path (str) or dict accepted")
        return devices

    def get_ups_devices(self, config) -> list:
        """
        Creates multiple UPSScraper.

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
        """
        Scrape measure data.

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
