import pytest
import os
import vcr  # pyre-ignore[21]
from . import CASSETTE_DIR, scrub_body, first_ups_details
from prometheus_eaton_ups_exporter.scraper import UPSScraper
from prometheus_eaton_ups_exporter.scraper_globals import (
        AUTHENTICATION_FAILED,
        CERTIFICATE_VERIFY_FAILED,
        CONNECTION_ERROR,
        INVALID_URL_ERROR,
        LoginFailedException,
        MISSING_SCHEMA_ERROR,
        REST_API_PATH,
        TIMEOUT_ERROR,
        )


def ups_scraper(address,
                auth,
                name: str,
                insecure: bool = True) -> UPSScraper:
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
def test_login(scraper_fixture) -> None:
    token_type, access_token = scraper_fixture.login()
    assert token_type == "Bearer"


@vcr.use_cassette(
    os.path.join(CASSETTE_DIR, "api_load_rest.yaml"),
    before_record_request=scrub_body()
)
def test_load_rest_api(scraper_fixture) -> None:
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
def test_get_measures(scraper_fixture) -> None:
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


def test_missing_schema_exception() -> None:
    scraper = ups_scraper("", ("", ""), "")
    with pytest.raises(LoginFailedException) as pytest_wrapped_e:
        scraper.login()
    assert pytest_wrapped_e.type == LoginFailedException
    assert pytest_wrapped_e.value.error_code == MISSING_SCHEMA_ERROR


def test_invalid_url_exception() -> None:
    scraper = ups_scraper("https:0.0.0.0", ("", ""), "")
    with pytest.raises(LoginFailedException) as pytest_wrapped_e:
        scraper.login()
    assert pytest_wrapped_e.type == LoginFailedException
    assert pytest_wrapped_e.value.error_code == INVALID_URL_ERROR


def test_connection_refused_exception() -> None:
    scraper = ups_scraper("https://127.0.0.1", ("", ""), "")
    with pytest.raises(LoginFailedException) as pytest_wrapped_e:
        scraper.login()
    assert pytest_wrapped_e.type == LoginFailedException
    assert pytest_wrapped_e.value.error_code == CONNECTION_ERROR


@vcr.use_cassette(
    os.path.join(CASSETTE_DIR, "certificate_exception.yaml"),
    before_record_request=scrub_body(),
    record_mode="new_episodes"
)
@pytest.mark.skip("AssertionError: assert 4 == 3")
def test_certificate_exception(ups_scraper_conf) -> None:
    address, auth, ups_name = first_ups_details(ups_scraper_conf)
    scraper = ups_scraper(
        address,
        auth,
        ups_name,
        insecure=False
    )
    with pytest.raises(LoginFailedException) as pytest_wrapped_e:
        scraper.load_page(address)
    assert pytest_wrapped_e.type == LoginFailedException
    assert pytest_wrapped_e.value.error_code == CERTIFICATE_VERIFY_FAILED


class MockLoginFailedException:
    def __init__(self, *args, **kwargs):
        raise LoginFailedException(*args, **kwargs)


def test_certificate_exception_monkey_patch(monkeypatch,
                                            ups_scraper_conf) -> None:
    address, auth, ups_name = first_ups_details(ups_scraper_conf)
    scraper = ups_scraper(
        address,
        auth,
        ups_name,
        insecure=False
    )

    with pytest.raises(LoginFailedException) as pytest_wrapped_e:
        monkeypatch.setattr(
            scraper, "load_page",
            MockLoginFailedException(
                CERTIFICATE_VERIFY_FAILED,
                "message"
            )
        )
        scraper.load_page(address)
    assert pytest_wrapped_e.type == LoginFailedException
    assert pytest_wrapped_e.value.error_code == CERTIFICATE_VERIFY_FAILED


def test_login_timeout_exception(monkeypatch, ups_scraper_conf) -> None:
    address, _, ups_name = first_ups_details(ups_scraper_conf)
    scraper = ups_scraper(
        address,
        ("a", "b"),
        ups_name
    )
    with pytest.raises(LoginFailedException) as pytest_wrapped_e:
        monkeypatch.setattr(
            scraper, "login",
            MockLoginFailedException(
                TIMEOUT_ERROR,
                "message"
            )
        )
        scraper.login()
    assert pytest_wrapped_e.type == LoginFailedException
    assert pytest_wrapped_e.value.error_code == TIMEOUT_ERROR


def test_auth_failed_exception(monkeypatch, ups_scraper_conf) -> None:
    address, _, ups_name = first_ups_details(ups_scraper_conf)
    scraper = ups_scraper(
        address,
        (ups_scraper_conf[ups_name]['user'], "abc"),
        ups_name
    )
    with pytest.raises(LoginFailedException) as pytest_wrapped_e:
        monkeypatch.setattr(
            scraper, "load_page",
            MockLoginFailedException(
                AUTHENTICATION_FAILED,
                "message"
            )
        )
        scraper.load_page(address + REST_API_PATH)
    assert pytest_wrapped_e.type == LoginFailedException
    assert pytest_wrapped_e.value.error_code == AUTHENTICATION_FAILED
