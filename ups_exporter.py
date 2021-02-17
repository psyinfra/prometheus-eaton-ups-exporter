"""Starts an prometheus exporter for a single Eaton UPS device."""
import sys
import argparse
import getpass
import time

from prometheus_client import start_http_server, REGISTRY
from eaton_ups.exporter import UPSExporter

NORMAL_EXECUTION = 0


def parse_args() -> argparse.Namespace:
    """Prepare command line arguments."""
    parser = argparse.ArgumentParser(
        description="Prometheus prometheus_exporter for measures "
                    "of a single Eaton UPS device"
    )
    parser.add_argument(
        "address",
        help="Specify the address of the UPS device"
    )
    parser.add_argument(
        "-u", "--username",
        help="Specify a user name",
        required=True
    )
    parser.add_argument(
        "-p", "--port",
        help="Listen to this port",
        default=8000
    )
    parser.add_argument(
        "--host-address",
        help="Address by which the prometheus metrics will be accessible",
        default="127.0.0.1"
    )
    parser.add_argument(
        '-k', '--insecure',
        action='store_true',
        help='allow a connection to an insecure UPS API',
        default=False
    )

    return parser.parse_args()


if __name__ == "__main__":
    try:
        args = parse_args()
        pswd = getpass.getpass('Password:')
        port = int(args.port)
        ups_exporter = UPSExporter(
            args.address,
            (args.username, pswd),
            args.insecure
        )

        REGISTRY.register(
            ups_exporter
        )

        # Start up the server to expose the metrics.
        start_http_server(port, addr=args.host_address)
        print(f"Starting Prometheus exporter on "
              f"{args.host_address}:{port}")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Prometheus exporter shut down")
        sys.exit(NORMAL_EXECUTION)
