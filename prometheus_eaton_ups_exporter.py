#!/usr/bin/env python3
"""Prometheus exporter for single or multiple Eaton UPSs."""
import sys
import time
import argparse

from argparse import HelpFormatter, SUPPRESS, OPTIONAL, ZERO_OR_MORE

from prometheus_client import start_http_server, REGISTRY
from prometheus_eaton_ups_exporter.exporter import UPSMultiExporter

# Free port according to
# https://github.com/prometheus/prometheus/wiki/Default-port-allocations
DEFAULT_PORT = 9790
DEFAULT_HOST = "127.0.0.1"


class CustomFormatter(HelpFormatter):
    """Custom argparse formatter to provide defaults and to split newlines."""

    def _split_lines(self, text, width):
        """
        Help message formatter which retains formatting of all help text.
        """
        return text.splitlines()

    def _get_help_string(self, action):
        """
        Help message formatter which adds default values to argument help.
        """
        help = action.help
        if '%(default)' not in action.help:
            if action.default is not SUPPRESS:
                defaulting_nargs = [OPTIONAL, ZERO_OR_MORE]
                if action.option_strings or action.nargs in defaulting_nargs:
                    help += ' (default: %(default)s)'
        return help


def parse_args():
    """Prepare command line arguments."""
    parser = argparse.ArgumentParser(
        description="Prometheus Exporter for Eaton UPSs.",
        formatter_class=CustomFormatter
    )
    parser.add_argument(
        '-w', '--web.listen-address',
        help='Interface and port to listen on, '
             'in the format of "ip_address:port".\n'
             'The IP can be omitted to listen on all interfaces.',
    )

    parser.add_argument(
        "-c", "--config",
        help="Configuration JSON file containing "
             "UPS addresses and login info",
        required=True
    )

    parser.add_argument(
        '-k', '--insecure',
        action='store_true',
        help='Allow the exporter to connect to UPSs '
             'with self-signed SSL certificates',
        default=False
    )

    parser.add_argument(
        '-t', '--threading',
        action='store_true',
        help='Whether to use multi-threading for scraping (faster)',
        default=False
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Be more verbose',
        default=False
    )

    return parser.parse_args()


def main():
    """Execute the Prometheus Eaton UPS Exporter"""
    try:
        args = parse_args()
        port = DEFAULT_PORT
        host_address = DEFAULT_HOST

        listen_address = args.__getattribute__('web.listen_address')
        if listen_address:
            if ':' in listen_address:
                host_address, port = tuple(listen_address.split(':'))
                if port == "":
                    port = DEFAULT_PORT
            else:
                host_address = listen_address

        REGISTRY.register(
            UPSMultiExporter(
                args.config,
                insecure=args.insecure,
                verbose=args.verbose,
                threading=args.threading
            )
        )

        # Start up the server to expose the metrics.
        start_http_server(int(port), addr=host_address)
        print(f"Starting Prometheus Eaton UPS Exporter on "
              f"{host_address}:{port}")
        while True:
            time.sleep(1)

    except OSError as err:
        print(err)

    except KeyboardInterrupt:
        print("Prometheus Eaton UPS Exporter shut down")
        sys.exit(0)


if __name__ == "__main__":
    main()
