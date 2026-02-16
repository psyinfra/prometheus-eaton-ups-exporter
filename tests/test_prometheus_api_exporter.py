"""
Testing the Exporter using the UPSExporter and UPSMultiExporter.
"""
import pytest


@pytest.mark.vcr()
def test_single_collect(ups_scraper_conf, single_exporter) -> None:
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


@pytest.mark.vcr()
def test_multi_collect(ups_scraper_conf, multi_exporter) -> None:
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


@pytest.mark.vcr()
@pytest.mark.skip("TODO: test threading with pytest-vcr")
def test_collect_threading(ups_scraper_conf, threading_multi_exporter) -> None:
    names = [
        'eaton_ups_input_volts', 'eaton_ups_input_hertz',
        'eaton_ups_input_amperes', 'eaton_ups_output_volts',
        'eaton_ups_output_hertz', 'eaton_ups_output_amperes',
        'eaton_ups_output_voltamperes', 'eaton_ups_output_watts',
        'eaton_ups_output_power_factor', 'eaton_ups_output_load_ratio',
        'eaton_ups_battery_volts', 'eaton_ups_battery_capacity_ratio',
        'eaton_ups_battery_remaining_seconds', 'eaton_ups_battery_health'
    ]
    gauges = threading_multi_exporter.collect()
    while (gauge := next(gauges, None)) is not None:
        assert gauge.name in names
        assert gauge.samples[0].labels['ups_id'] in \
            list(ups_scraper_conf.keys())
