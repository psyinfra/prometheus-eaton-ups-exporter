
import time
import argparse
import getpass

from eaton_ups.prometheus_exporter.api_exporter import UPSExporter, UPSMultiExporter
from prometheus_client import start_http_server, REGISTRY


def parse_single_args() -> argparse.Namespace:
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


def parse_multi_args():
    parser = argparse.ArgumentParser(
        description="Prometheus prometheus_exporter for "
                    "Eaton UPS measures of multiple UPS devices "
    )
    parser.add_argument(
        "-c", "--config",
        help="Provide a json like config for more than one ups device",
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


def single_exporter():
    try:
        args = parse_single_args()
        pswd = getpass.getpass('Password:')
        port = int(args.port)
        ups_exporter = UPSExporter(
            args.address,
            args.username,
            pswd,
            insecure=args.insecure
        )

        REGISTRY.register(
            ups_exporter
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
        print("Prometheus prometheus_exporter shut down")
        exit(0)


def multi_exporter():
    try:
        args = parse_multi_args()
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
        print("Prometheus prometheus_exporter shut down")
        exit(0)


if __name__ == "__main__":
   pass