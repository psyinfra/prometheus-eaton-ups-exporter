"""
Testing the Exporter using the UPSExporter and UPSMultiExporter.
"""
import os
import pytest
import vcr
from . import CASSETTE_DIR, scrub_body, first_ups_details
from prometheus_eaton_ups_exporter.exporter import (
        UPSMultiExporter,
        UPSExporter,
        )


# Create Multi Exporter
@pytest.fixture(scope="function")
def single_exporter(ups_scraper_conf):
    address, auth, ups_name = first_ups_details(ups_scraper_conf)
    return UPSExporter(
        address,
        auth,
        ups_name,
        insecure=True,
        verbose=True
    )


# Create Multi Exporter
@pytest.fixture(scope="function")
def multi_exporter(ups_scraper_conf):
    return UPSMultiExporter(
        ups_scraper_conf,
        insecure=True,
        verbose=True
    )


# Create Multi Exporter
@pytest.fixture(scope="function")
def threading_multi_exporter(ups_scraper_conf):
    return UPSMultiExporter(
        ups_scraper_conf,
        insecure=True,
        verbose=True,
        threading=True
    )


@vcr.use_cassette(
    os.path.join(CASSETTE_DIR, "single_exporter.yaml"),
    before_record_request=scrub_body()
)
def test_single_collect(ups_scraper_conf, single_exporter):
    names = [
        'eaton_ups_input_volts', 'eaton_ups_input_hertz',
        'eaton_ups_input_amperes', 'eaton_ups_output_volts',
        'eaton_ups_output_hertz', 'eaton_ups_output_amperes',
        'eaton_ups_output_voltamperes', 'eaton_ups_output_watts',
        'eaton_ups_output_power_factor', 'eaton_ups_output_load_ratio',
        'eaton_ups_battery_volts', 'eaton_ups_battery_capacity_ratio',
        'eaton_ups_battery_remaining_seconds', 'eaton_ups_battery_health'
    ]
    gauges = single_exporter.collect()
    ups_gauges = [next(gauges) for _ in names]
    ups_name = single_exporter.ups_scraper.name
    labels = [{'ups_id': ups_name} for _ in ups_gauges]
    gauge_names = [gauge.name for gauge in ups_gauges]
    gauge_labels = [gauge.samples[0].labels for gauge in ups_gauges]

    assert gauge_names == names
    assert gauge_labels == labels


@vcr.use_cassette(
    os.path.join(CASSETTE_DIR, "multi_exporter.yaml"),
    before_record_request=scrub_body()
)
def test_multi_collect(ups_scraper_conf, multi_exporter):
    names = [
        'eaton_ups_input_volts', 'eaton_ups_input_hertz',
        'eaton_ups_input_amperes', 'eaton_ups_output_volts',
        'eaton_ups_output_hertz', 'eaton_ups_output_amperes',
        'eaton_ups_output_voltamperes', 'eaton_ups_output_watts',
        'eaton_ups_output_power_factor', 'eaton_ups_output_load_ratio',
        'eaton_ups_battery_volts', 'eaton_ups_battery_capacity_ratio',
        'eaton_ups_battery_remaining_seconds', 'eaton_ups_battery_health'
    ]
    gauges = multi_exporter.collect()
    for ups_name in ups_scraper_conf.keys():
        ups_gauges = [next(gauges) for _ in names]

        labels = [{'ups_id': ups_name} for _ in ups_gauges]
        gauge_names = [gauge.name for gauge in ups_gauges]
        gauge_labels = [gauge.samples[0].labels for gauge in ups_gauges]

        assert gauge_names == names
        assert gauge_labels == labels


def test_collect_threading(ups_scraper_conf, threading_multi_exporter):
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
        os.path.join(CASSETTE_DIR, "threading_multi_exporter.yaml"),
        before_record_request=scrub_body(),
        record_mode="new_episodes"
    ):
        gauges = threading_multi_exporter.collect()
        while (gauge := next(gauges, None)) is not None:
            assert gauge.name in names
            assert gauge.samples[0].labels['ups_id'] \
                   in list(ups_scraper_conf.keys())
