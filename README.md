# Eaton UPS Prometheus Exporter

## Description

Create an automated prometheus exporter for Eaton UPS measures, 
by scraping the UPS REST API of one or more Eaton UPS devices,


### Conventions:
##### Hardcoded API calls:
* POST *web_ui*/rest/mbdetnrs/1.0/oauth2/token   (for authentification)
* GET *web_ui*/rest/mbdetnrs/1.0/powerDistributions/1   (to receive current measure data)

##### Defaults:
* Default host-address is *localhost* (*127.0.0.1*)
* Default port is  9790 (Free slot regarding [prometheus default port allocations](https://github.com/prometheus/prometheus/wiki/Default-port-allocations))
* Login timeout is set to 5 seconds
* other request timeouts are set to 2 seconds
* static values are described in *prometheus_eaton_ups_exporter/scraper_globals.py*

### Supported Devices:
* Eaton 5P 1550iR ([user guide](https://www.eaton.com/content/dam/eaton/products/backup-power-ups-surge-it-power-distribution/power-management-software-connectivity/eaton-gigabit-network-card/eaton-network-m2-user-guide.pdf))
* Might work on other devices as well, with the same API

Data scraped:
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


## Usage:
To provide measures of one or more ups devices on one exporter \
with a JSON file looking like the given *config.json* use this:

```
python3 ups_exporter.py [-h] -c CONFIG [-p PORT] [--host-address HOST_ADDRESS] [-k]

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        configuration json file containing UPS addresses and login info
  -p PORT, --port PORT  Listen to this port
  --host-address HOST_ADDRESS
                        Address by which the prometheus metrics will be accessible
  -k, --insecure        allow a connection to an insecure UPS API
```

### Requirements:
- requests
- urllib3
- [prometheus_client](https://github.com/prometheus/client_python)

