import pytest
import getpass
import os
import sys
import json
import vcr
from . import CASSETTE_DIR, scrub_body
from prometheus_eaton_ups_exporter.scraper import UPSScraper
from prometheus_eaton_ups_exporter.scraper_globals import REST_API_PATH


@pytest.fixture(scope="function")
def ups_scraper(ups_scraper_conf):
    ups_name = list(ups_scraper_conf.keys())[0]
    return UPSScraper(
        ups_scraper_conf[ups_name]['address'],
        (
            ups_scraper_conf[ups_name]['user'],
            ups_scraper_conf[ups_name]['password']
        ),
        ups_name,
        insecure=True,
        verbose=True
    )


def test_login(ups_scraper):
    with vcr.use_cassette(
            os.path.join(CASSETTE_DIR, "api_login.yaml"),
            before_record_request=scrub_body()
    ):
        token_type, access_token = ups_scraper.login()
        assert token_type == "Bearer"


def test_load_rest_api(ups_scraper):
    """Tests load_page function with rest api."""
    with vcr.use_cassette(
            os.path.join(CASSETTE_DIR, "api_load_rest.yaml"),
            before_record_request=scrub_body()
    ):
        request = ups_scraper.load_page(
            ups_scraper.ups_address + REST_API_PATH
        )
        # Todo
        json_response = request.json()
        respones_keys = [
            '@id', 'id', 'identification', 'specification',
            'configuration', 'ups', 'status', 'inputs',
            'avr', 'outputs', 'inverters', 'chargers',
            'backupSystem', 'bypass', 'rectifiers', 'outlets'
        ]
        assert respones_keys == list(json_response.keys())


def test_get_measures(ups_scraper):
    with vcr.use_cassette(
            os.path.join(CASSETTE_DIR, "api_measures.yaml"),
            before_record_request=scrub_body()
    ):
        measures = ups_scraper.get_measures()
        measures_keys = [
            'ups_id',
            'ups_inputs',
            'ups_outputs',
            'ups_powerbank'
        ]
        assert list(measures.keys()) == measures_keys
        assert measures['ups_id'] == ups_scraper.name

        ups_inputs = measures.get('ups_inputs')
        assert list(ups_inputs) == [
            '@id', 'id', 'measures', 'status', 'phases'
        ]
        assert list(ups_inputs.get('measures')) == [
            'realtime'
        ]
        assert list(ups_inputs.get('measures').get('realtime')) == [
            'frequency', 'voltage', 'current'
        ]

        ups_outputs = measures.get('ups_outputs')
        assert list(ups_outputs) == [
            '@id', 'id', 'measures', 'status', 'phases'
        ]
        assert list(ups_outputs.get('measures')) == [
            'realtime'
        ]
        assert list(ups_outputs.get('measures').get('realtime')) == [
            'frequency', 'voltage', 'current', 'activePower',
            'apparentPower', 'powerFactor', 'percentLoad'
        ]

        ups_powerbank = measures.get('ups_powerbank')
        assert list(ups_powerbank) == [
            '@id', 'specification', 'configuration',
            'measures', 'status', 'test', 'lcm', 'entities'
        ]
        assert list(ups_powerbank.get('measures')) == [
            'voltage', 'remainingChargeCapacity', 'remainingTime'
        ]
