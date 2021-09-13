import os
import json

import pytest


@pytest.fixture(scope='module')
def ups_scraper_conf():
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """

    config_file = (
        'tests/fixtures/config.json'
        if os.path.exists('tests/fixtures/config.json')
        else 'tests/fixtures/dummy_config.json'
    )

    try:
        with open(config_file) as json_file:
            config = json.load(json_file)
    except FileNotFoundError as err:
        print(err)

    return config
