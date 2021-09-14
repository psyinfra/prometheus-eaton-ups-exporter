"""
Testing the Exporter using the UPSMultiExporter.
The UPSMultiExporter inherits form the UPSExporter,
with additional functionalities.
Hence only the UPSMultiExporter is tested.
"""
import os
import pytest
import vcr
from . import CASSETTE_DIR, scrub_body
from prometheus_eaton_ups_exporter.exporter import UPSMultiExporter


# Create Multi Exporter
@pytest.fixture(scope="function")
def exporter(ups_scraper_conf):
    return UPSMultiExporter(
        ups_scraper_conf,
        insecure=True,
        verbose=True
    )


# Create Multi Exporter
@pytest.fixture(scope="function")
def threading_exporter(ups_scraper_conf):
    return UPSMultiExporter(
        ups_scraper_conf,
        insecure=True,
        verbose=True,
        threading=True
    )


def test_collect(ups_scraper_conf, exporter):
    names = [
        'eaton_ups_input_volts', 'eaton_ups_input_hertz',
        'eaton_ups_input_amperes', 'eaton_ups_output_volts',
        'eaton_ups_output_hertz', 'eaton_ups_output_amperes',
        'eaton_ups_output_voltamperes', 'eaton_ups_output_watts',
        'eaton_ups_output_power_factor', 'eaton_ups_output_load_ratio',
        'eaton_ups_battery_volts', 'eaton_ups_battery_capacity_ratio',
        'eaton_ups_battery_remaining_seconds', 'eaton_ups_battery_health'
    ]
    with vcr.use_cassette(
            os.path.join(CASSETTE_DIR, "exporter.yaml"),
            before_record_request=scrub_body()
    ):
        gauges = exporter.collect()
        for ups_name in ups_scraper_conf.keys():
            ups_gauges = [next(gauges) for _ in names]

            labels = [{'ups_id': ups_name} for _ in ups_gauges]
            gauge_names = [gauge.name for gauge in ups_gauges]
            gauge_labels = [gauge.samples[0].labels for gauge in ups_gauges]

            assert gauge_names == names
            assert gauge_labels == labels


def test_collect_threading(ups_scraper_conf, threading_exporter):
    names = [
        'eaton_ups_input_volts', 'eaton_ups_input_hertz',
        'eaton_ups_input_amperes', 'eaton_ups_output_volts',
        'eaton_ups_output_hertz', 'eaton_ups_output_amperes',
        'eaton_ups_output_voltamperes', 'eaton_ups_output_watts',
        'eaton_ups_output_power_factor', 'eaton_ups_output_load_ratio',
        'eaton_ups_battery_volts', 'eaton_ups_battery_capacity_ratio',
        'eaton_ups_battery_remaining_seconds', 'eaton_ups_battery_health'
    ]
    with vcr.use_cassette(
        os.path.join(CASSETTE_DIR, "threading_exporter.yaml"),
        before_record_request=scrub_body(),
        record_mode="new_episodes"
    ):
        gauges = threading_exporter.collect()
        while (gauge := next(gauges, None)) is not None:
            assert gauge.name in names
            assert gauge.samples[0].labels['ups_id'] \
                   in list(ups_scraper_conf.keys())



