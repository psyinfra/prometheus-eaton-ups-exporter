import pytest
import getpass
import os
import sys
import json
import vcr
from prometheus_eaton_ups_exporter.exporter import UPSScraper

CASSETTE_DIR = os.path.join(
    os.getcwd(),
    "tests",
    "fixtures/cassettes"
)


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
        insecure=True
    )


def scrub_body():
    def before_record_request(request):
        try:
            body_json = json.loads(request.body.decode("utf-8").replace("'", '"'))
            body_json['username'] = 'username'
            body_json['password'] = 'password'
            request.body = str(body_json).replace("'", '"').encode('utf-8')
            return request
        except AttributeError:
            return request
    return before_record_request


def test_login(ups_scraper):
    with vcr.use_cassette(
            os.path.join(CASSETTE_DIR, "api_login.yaml"),
            before_record_request=scrub_body()
    ):
        token_type, access_token = ups_scraper.login()
        assert token_type == "Bearer"


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
        print(measures['ups_inputs'].keys())


# @pytest.mark.vcr(cassette_path)
# def test_ups_web_ui():
#     address = 'https://localhost:4430'
#     if not os.path.exists(cassette_path):
#         username = input('Username:')
#         password = getpass.getpass('Password:')
#         scraper = UPSScraper(
#             address,
#             username,
#             password,
#             insecure=True
#         )
#
#         measures = scraper.get_measures()
#     else:
#         scraper = UPSScraper(
#             address,
#             None,
#             None,
#             insecure=True
#         )
#         measures = scraper.get_measures()
#
#     assert measures.get('ups_id') == '1'
#
#     ups_inputs = measures.get('ups_inputs')
#     assert list(ups_inputs) == [
#         '@id', 'id', 'measures', 'status', 'phases'
#     ]
#     assert list(ups_inputs.get('measures')) == [
#         'realtime'
#     ]
#     assert list(ups_inputs.get('measures').get('realtime')) == [
#         'frequency', 'voltage', 'current'
#     ]
#
#     ups_outputs = measures.get('ups_outputs')
#     assert list(ups_outputs) == [
#         '@id', 'id', 'measures', 'status', 'phases'
#     ]
#     assert list(ups_outputs.get('measures')) == [
#         'realtime'
#     ]
#     assert list(ups_outputs.get('measures').get('realtime')) == [
#         'frequency', 'voltage', 'current', 'activePower',
#         'apparentPower', 'powerFactor', 'percentLoad'
#     ]
#
#     assert measures.get('ups_powerbank')
#     ups_powerbank = measures.get('ups_powerbank')
#     assert list(ups_powerbank) == [
#         '@id', 'specification', 'configuration',
#         'measures', 'status', 'test', 'lcm', 'entities'
#     ]
#     assert list(ups_powerbank.get('measures')) == [
#         'voltage', 'remainingChargeCapacity', 'remainingTime'
#     ]
#     assert ups_powerbank.get('measures').get('voltage')
#     assert ups_powerbank.get('measures').get('remainingChargeCapacity')
#     assert ups_powerbank.get('measures').get('remainingTime')
