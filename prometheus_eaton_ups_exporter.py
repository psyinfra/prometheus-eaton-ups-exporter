#!/usr/bin/env python3
"""Prometheus exporter for single or multiple Eaton UPSs."""
import sys
import time
import argparse

from argparse import HelpFormatter, SUPPRESS, OPTIONAL, ZERO_OR_MORE

from prometheus_client import start_http_server, REGISTRY
from prometheus_eaton_ups_exporter.scraper_globals import REQUEST_TIMEOUT
from prometheus_eaton_ups_exporter.exporter import UPSMultiExporter

DEFAULT_PORT = 9795
DEFAULT_HOST = "0.0.0.0"


class CustomFormatter(HelpFormatter):
    """Custom argparse formatter to provide defaults and to split newlines."""

    def _split_lines(self, text, width):
        """Help message formatter which retains formatting of all help text."""
        return text.splitlines()

    def _get_help_string(self, action):
        """Help message formatter which adds default values to
        argument help."""
        help = action.help
        if '%(default)' not in action.help:
            if action.default is not SUPPRESS:
                defaulting_nargs = [OPTIONAL, ZERO_OR_MORE]
                if action.option_strings or action.nargs in defaulting_nargs:
                    help += ' (default: %(default)s)'
        return help


class Range(object):

    def __init__(self, start, end):
        self.start = start
        self.end = end
        self._name_parser_map = {}

    def __eq__(self, other):
        return self.start <= other <= self.end

    def __repr__(self):
        return f"range {self.start} - {self.end}"


def create_parser():
    """Prepare command line arguments."""
    parser = argparse.ArgumentParser(
        description="Prometheus Exporter for Eaton UPSs.",
        formatter_class=CustomFormatter
    )
    parser.add_argument(
        '-w', '--web.listen-address',
        help='Interface and port to listen on, '
             'in the format of "ip_address:port".\n'
             'If the IP is omitted, the exporter listens on all interfaces.',
        default=f"{DEFAULT_HOST}:{DEFAULT_PORT}"
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

    parser.add_argument(
        '--login-timeout',
        type=float,
        help='The login timeout for the UPSs in seconds',
        choices=[Range(REQUEST_TIMEOUT, 10)],
        default=3
    )

    return parser


def split_listen_address(listen_address):
    """Split listen address into host and port."""
    if ':' in listen_address:
        host_address, port = listen_address.split(':')
    else:
        host_address = listen_address

    # if host_address or port were not specified, use default values
    if not host_address:
        host_address = DEFAULT_HOST
    if not port:
        port = DEFAULT_PORT

    return host_address, port


def run(args):
    """Execute the Prometheus Eaton UPS Exporter."""
    parser = create_parser()
    try:
        args = parser.parse_args(args)

        listen_address = args.__getattribute__('web.listen_address')
        host_address, port = split_listen_address(listen_address)

        REGISTRY.register(
            UPSMultiExporter(
                args.config,
                insecure=args.insecure,
                verbose=args.verbose,
                threading=args.threading,
                login_timeout=args.login_timeout
            )
        )

        # Start up the server to expose the metrics.
        start_http_server(int(port), addr=host_address)
        print(
            f"Starting Prometheus Eaton UPS Exporter on {host_address}:{port}"
        )
        # Run forever until an Error Event or Keyboard Interrupt
        while True:
            time.sleep(1)

    except OSError as err:
        print(err)

    except KeyboardInterrupt:
        print("Prometheus Eaton UPS Exporter shut down")
        sys.exit(0)


def main():
    run(sys.argv[1:])


if __name__ == "__main__":
    main()
