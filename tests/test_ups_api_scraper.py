
import pytest
import getpass
import os
import sys
from exporter.ups_api_scraper import UPSScraper


@pytest.mark.vcr()
def test_ups_web_ui():
    if not os.path.exists(
            sys.prefix +
            '/ups-exporter/tests/cassettes/test_ups_web_ui.yaml'
    ):
        scraper = UPSScraper(
            'https://localhost:4430',
            input('Username:'),
            getpass.getpass('Password:'),
            insecure=bool(input('Insecure (true|false):'))
        )
        measures = scraper.get_measures()
    else:
        scraper = UPSScraper(
            'https://localhost:4430',
            None,
            None,
            insecure=True
        )
        measures = scraper.get_measures()

    assert measures.get('ups_id') == '1'

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

    assert measures.get('ups_powerbank')
    ups_powerbank = measures.get('ups_powerbank')
    assert list(ups_powerbank) == [
        '@id', 'specification', 'configuration',
        'measures', 'status', 'test', 'lcm', 'entities'
    ]
    assert list(ups_powerbank.get('measures')) == [
        'voltage', 'remainingChargeCapacity', 'remainingTime'
    ]
    assert ups_powerbank.get('measures').get('voltage')
    assert ups_powerbank.get('measures').get('remainingChargeCapacity')
    assert ups_powerbank.get('measures').get('remainingTime')
