"""Multi Prometheus exporter for UPS measures."""

import sys
import argparse
import time

from prometheus_client import start_http_server, REGISTRY
from eaton_ups.exporter import UPSMultiExporter


def parse_args():
    """Prepare command line arguments."""
    parser = argparse.ArgumentParser(
        description="Prometheus prometheus_exporter for "
                    "Eaton UPS measures of multiple UPS devices "
    )
    parser.add_argument(
        "-c", "--config",
        help="configuration json file containing UPS addresses and login info",
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
        port = int(args.port)

        REGISTRY.register(
            UPSMultiExporter(
                args.config,
                insecure=args.insecure
            )
        )

        # Start up the server to expose the metrics.
        start_http_server(port, addr=args.host_address)
        print(f"Starting Prometheus prometheus_exporter on "
              f"{args.host_address}:{port}")
        while True:
            time.sleep(1)

    except TypeError as err:
        print(err)

    except KeyboardInterrupt:
        print("Prometheus exporter shut down")
        sys.exit(0)
