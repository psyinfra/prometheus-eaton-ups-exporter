# UPS Prometheus Exporter
#### based on an API approach

## Description

Create an automated prometheus exporter for Eaton UPS measures, by scraping the UPS REST API.

Hardcoded API calls:
* POST *web_ui*/rest/mbdetnrs/1.0/oauth2/token   (for authentification)
* GET *web_ui*/rest/mbdetnrs/1.0/powerDistributions/1   (to receive current measure data)

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


### Supported Devices:
* Eaton 5P 1550iR ([user guide](https://www.eaton.com/content/dam/eaton/products/backup-power-ups-surge-it-power-distribution/power-management-software-connectivity/eaton-gigabit-network-card/eaton-network-m2-user-guide.pdf))
* Might work on other devices as well, with the same API

### Usage:
```
python3 prometheus_api_exporter.py [-h] -u USERNAME [-p PORT] [--host-address HOST_ADDRESS] [-k] address

positional arguments:
  address               Specify the address of the UPS device

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Specify a user name
  -p PORT, --port PORT  Listen to this port
  --host-address HOST_ADDRESS
                        Address by what the prometheus metrics will be accessible
  -k, --insecure        allow a connection to an insecure UPS API
```

### Requirements:
- requests
- urllib3
- json

