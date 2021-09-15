import pytest
import os
import vcr
from . import CASSETTE_DIR, scrub_body
from prometheus_eaton_ups_exporter.scraper import UPSScraper
from prometheus_eaton_ups_exporter.scraper_globals import *


def ups_scraper(address, auth, name, insecure=True):
    return UPSScraper(
        address,
        auth,
        name,
        insecure=insecure,
        verbose=True
    )


@pytest.fixture(scope="function")
def scraper_fixture(ups_scraper_conf):
    ups_name = list(ups_scraper_conf.keys())[0]
    address = ups_scraper_conf[ups_name]['address']
    auth = (
        ups_scraper_conf[ups_name]['user'],
        ups_scraper_conf[ups_name]['password']
    )
    return ups_scraper(address, auth, ups_name)


@vcr.use_cassette(
    os.path.join(CASSETTE_DIR, "api_login.yaml"),
    before_record_request=scrub_body()
)
def test_login(scraper_fixture):
    token_type, access_token = scraper_fixture.login()
    assert token_type == "Bearer"


@vcr.use_cassette(
    os.path.join(CASSETTE_DIR, "api_load_rest.yaml"),
    before_record_request=scrub_body()
)
def test_load_rest_api(scraper_fixture):
    """Tests load_page function with rest api."""
    request = scraper_fixture.load_page(
        scraper_fixture.ups_address + REST_API_PATH
    )
    # Todo
    json_response = request.json()
    response_keys = [
        '@id', 'id', 'identification', 'specification',
        'configuration', 'ups', 'status', 'inputs',
        'avr', 'outputs', 'inverters', 'chargers',
        'backupSystem', 'bypass', 'rectifiers', 'outlets'
    ]
    assert response_keys == list(json_response.keys())


@vcr.use_cassette(
    os.path.join(CASSETTE_DIR, "api_measures.yaml"),
    before_record_request=scrub_body()
)
def test_get_measures(scraper_fixture):
    measures = scraper_fixture.get_measures()
    measures_keys = [
        'ups_id',
        'ups_inputs',
        'ups_outputs',
        'ups_powerbank'
    ]
    assert list(measures.keys()) == measures_keys
    assert measures['ups_id'] == scraper_fixture.name

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


def conf_details(conf):
    ups_name = list(conf.keys())[0]
    address = conf[ups_name]['address']
    auth = (
        conf[ups_name]['user'],
        conf[ups_name]['password']
    )
    return address, auth, ups_name


def test_missing_schema_exception():
    scraper = ups_scraper("", ("", ""), "")
    with pytest.raises(LoginFailedException) as pytest_wrapped_e:
        scraper.login()
    assert pytest_wrapped_e.type == LoginFailedException
    assert pytest_wrapped_e.value.error_code == MISSING_SCHEMA_ERROR


def test_invalid_url_exception():
    scraper = ups_scraper("https:0.0.0.0", ("", ""), "")
    with pytest.raises(LoginFailedException) as pytest_wrapped_e:
        scraper.login()
    assert pytest_wrapped_e.type == LoginFailedException
    assert pytest_wrapped_e.value.error_code == INVALID_URL_ERROR


def test_connection_refused_exception():
    scraper = ups_scraper("https://127.0.0.1", ("", ""), "")
    with pytest.raises(LoginFailedException) as pytest_wrapped_e:
        scraper.login()
    assert pytest_wrapped_e.type == LoginFailedException
    assert pytest_wrapped_e.value.error_code == CONNECTION_ERROR

#
# @vcr.use_cassette(
#     os.path.join(CASSETTE_DIR, "certificate_exception.yaml"),
#     before_record_request=scrub_body(),
#     record_mode="new_episodes"
# )
# def test_certificate_exception(ups_scraper_conf):
#     address, auth, ups_name = conf_details(ups_scraper_conf)
#     scraper = ups_scraper(
#         address,
#         auth,
#         ups_name,
#         insecure=False
#     )
#     with pytest.raises(LoginFailedException) as pytest_wrapped_e:
#         scraper.load_page(address)
#     assert pytest_wrapped_e.type == LoginFailedException
#     assert pytest_wrapped_e.value.error_code == CERTIFICATE_VERIFY_FAILED
#
#
# @vcr.use_cassette(
#     os.path.join(CASSETTE_DIR, "login_timeout_exception.yaml"),
#     record_mode="new_episodes"
# )
# def test_login_timeout_exception(ups_scraper_conf):
#     address, _, ups_name = conf_details(ups_scraper_conf)
#     scraper = ups_scraper(
#         address,
#         ("a", "b"),
#         ups_name
#     )
#     with pytest.raises(LoginFailedException) as pytest_wrapped_e:
#         scraper.login()
#     assert pytest_wrapped_e.type == LoginFailedException
#     assert pytest_wrapped_e.value.error_code == TIMEOUT_ERROR
#
#
# @vcr.use_cassette(
#     os.path.join(CASSETTE_DIR, "auth_failed_exception.yaml"),
#     before_record_request=scrub_body(),
#     record_mode="new_episodes"
# )
# def test_auth_failed_exception(ups_scraper_conf):
#     address, _, ups_name = conf_details(ups_scraper_conf)
#     scraper = ups_scraper(
#         address,
#         (ups_scraper_conf[ups_name]['user'], "abc"),
#         ups_name
#     )
#     with pytest.raises(LoginFailedException) as pytest_wrapped_e:
#         scraper.load_page(address + REST_API_PATH)
#     assert pytest_wrapped_e.type == LoginFailedException
#     assert pytest_wrapped_e.value.error_code == AUTHENTICATION_FAILED
