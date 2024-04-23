# Eaton UPS Prometheus Exporter

## Description

A Prometheus exporter for Eaton UPSs. Data is collected from the REST API of the
web UI of Eaton UPSs and is made available for Prometheus to scrape.

The exporter can monitor multiple UPSs.

## Information Exported
- Input Voltage (V)
- Input Frequency (Hz)
- Output Voltage (V)
- Output Frequency (Hz)
- Output Current (A)
- Output Apparent Power (VA)
- Output Active Power (W)
- Output Power Factor
- Output Percent Load (%)
- Battery Voltage (V)
- Battery Capacity (%)
- Battery Remaining Time (s)
- Battery Health Status (given as the remaining lifetime in years [uncertain, contribute to [#19](https://github.com/psyinfra/prometheus-eaton-ups-exporter/issues/19)])

## Supported Devices:
* Eaton 5P 1550iR ([user guide](https://www.eaton.com/content/dam/eaton/products/backup-power-ups-surge-it-power-distribution/power-management-software-connectivity/eaton-gigabit-network-card/eaton-network-m2-user-guide.pdf))
* Other models may also work if they use the same API

## Usage:
UPSs to monitor and their credentials are defined in a config file. See
`config.json` for an example.

```
./prometheus_eaton_ups_exporter.py [-h] [-w WEB.LISTEN_ADDRESS] -c CONFIG [-k] [-t] [-v] [--login-timeout {range 2 - 10}]


optional arguments:
  -h, --help            show this help message and exit
  -w WEB.LISTEN_ADDRESS, --web.listen-address WEB.LISTEN_ADDRESS
                        Interface and port to listen on, in the format of "ip_address:port".
                        If the IP is omitted, the exporter listens on all interfaces. (default: 0.0.0.0:9795)
  -c CONFIG, --config CONFIG
                        Configuration JSON file containing UPS addresses and login info (default: None)
  -k, --insecure        Allow the exporter to connect to UPSs with self-signed SSL certificates (default: False)
  -t, --threading       Whether to use multi-threading for scraping (faster) (default: False)
  -v, --verbose         Be more verbose (default: False)
  --login-timeout {range 2 - 10}
                        The login timeout for the UPSs in seconds (default: 3)

```

## Defaults:
* Default host-address is `0.0.0.0`
* Default port is 9795 (see also: [Prometheus default port allocations](https://github.com/prometheus/prometheus/wiki/Default-port-allocations))
* Login timeout is set to 3 seconds
* Other request timeouts are set to 2 seconds
* Static values are described in `prometheus_eaton_ups_exporter/scraper_globals.py`

## Requirements:
- requests
- [prometheus_client](https://github.com/prometheus/client_python)

# Installation:
    git clone https://github.com/psyinfra/prometheus-eaton-ups-exporter.git
    cd prometheus-eaton-ups-exporter
    pip install -r requirements.txt

# Testing:

Install requirements with

    pip install -r test-requirements.txt

Runt tests with

    pytest tests

#### Test-Requirements:
- [vcrpy](https://vcrpy.readthedocs.io/)
- pytest