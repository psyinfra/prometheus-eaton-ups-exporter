"""Multi Prometheus exporter for UPS measures."""
import argparse
import sys
import time

from eaton_ups_prometheus_exporter.exporter import UPSMultiExporter
from prometheus_client import start_http_server, REGISTRY

# Free slot according to
# https://github.com/prometheus/prometheus/wiki/Default-port-allocations
DEFAULT_PORT = 9790


def parse_args():
    """Prepare command line arguments."""
    parser = argparse.ArgumentParser(
        description="Prometheus prometheus_exporter for "
                    "Eaton UPS measures of multiple UPS devices "
    )
    parser.add_argument(
        "-p", "--port",
        help="Listen to this port",
        type=int,
        default=DEFAULT_PORT
    )

    parser.add_argument(
        "--host-address",
        help="Address by which the prometheus metrics will be accessible",
        default="127.0.0.1"
    )
    parser.add_argument(
        '-w', '--web.listen-address',
        help='Provide a host address in the form of "ip_address:port"'
    )

    parser.add_argument(
        "-c", "--config",
        help="Configuration json file containing UPS addresses and login info",
        required=True
    )

    parser.add_argument(
        '-k', '--insecure',
        action='store_true',
        help='Allow a connection to an insecure UPS API',
        default=False
    )

    return parser.parse_args()


if __name__ == "__main__":
    try:
        args = parse_args()
        port = args.port
        host_address = args.host_address

        listen_address = args.__getattribute__('web.listen_address')
        if listen_address:
            if ':' in listen_address:
                host_address, port = tuple(listen_address.split(':'))
            else:
                host_address = listen_address

        REGISTRY.register(
            UPSMultiExporter(
                args.config,
                insecure=args.insecure
            )
        )

        # Start up the server to expose the metrics.
        start_http_server(int(port), addr=host_address)
        print(f"Starting Prometheus prometheus_exporter on "
              f"{args.host_address}:{port}")
        while True:
            time.sleep(1)

    except OSError as err:
        print(err)

    except KeyboardInterrupt:
        print("Prometheus exporter shut down")
        sys.exit(0)
