import pytest
import getpass
import os
import sys
import vcr
from exporter.ups_api_scraper import UPSScraper

cassette_path = (
        sys.prefix +
        '/ups-prometheus_exporter/tests/cassettes/test_ups_web_ui.yaml'
)


def test_login():
    with vcr.use_cassette(
            cassette_path,
            filter_post_data_parameters=['client_secret']
    ) as cass:
        address = 'https://localhost:4430'
        username = input('Username:')
        password = getpass.getpass('Password:')
        scraper = UPSScraper(
            address,
            username,
            password,
            insecure=True
        )

        measures = scraper.get_measures()


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
