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

## Supported Devices:
* Eaton 5P 1550iR ([user guide](https://www.eaton.com/content/dam/eaton/products/backup-power-ups-surge-it-power-distribution/power-management-software-connectivity/eaton-gigabit-network-card/eaton-network-m2-user-guide.pdf))
* Other models may also work if they use the same API

## Usage:
UPSs to monitor and their credentials are defined in a config file. See
`config.json` for an example.

```
./prometheus_eaton_ups_exporter.py [-h] -c CONFIG [--web.listen-address WEB.LISTEN_ADDRESS] [-k]

optional arguments:
  -h, --help            show this help message and exit
  -w WEB.LISTEN_ADDRESS, --web.listen-address WEB.LISTEN_ADDRESS
                        Interface and port to listen on, in the format of "ip_address:port".
                        The IP can be omitted to listen on all interfaces.
  -c CONFIG, --config CONFIG
                        Configuration JSON file containing UPS addresses and login info
  -k, --insecure        Allow the exporter to connect to UPSs with self-signed SSL certificates

```

## Defaults:
* Default host-address is localhost
* Default port is 9790 (a free port according to [Prometheus default port allocations](https://github.com/prometheus/prometheus/wiki/Default-port-allocations))
* Login timeout is set to 5 seconds
* Other request timeouts are set to 2 seconds
* Static values are described in `prometheus_eaton_ups_exporter/scraper_globals.py`

## Requirements:
- requests
- urllib3
- [prometheus_client](https://github.com/prometheus/client_python)
