#!/usr/bin/python3.6

import sys
import termios
import time
import tty
from argparse import ArgumentParser

from .Crawler import Crawler
from .DNS_Lookup import DNS_Lookup


def main(args):
    seed_file = args.seed_file

    if seed_file is None:
        dns_lookup = DNS_Lookup()
        seed_ips = dns_lookup.get_DNS_IP()
    else:
        seed_ips = get_ips_from_file(seed_file)

    # TODO deal with example with no connectivity
    crawler = Crawler(seed_ips, args.time, args.network_to_crawl, args.nb_threads, args.display,
                      args.display_progression)

    crawler.start()
    a = time.time()

    while True:
        if (time.time() - a) > 3:
            a = time.time()
            if (not crawler.isAlive()):
                break

        # TODO Problem deal with no timeout and with printing and with killing if measurements_manager failed.
        char = getch()

        if char == "q":
            if args.display is True:
                crawler.displayer.display_message("You pressed the Exit key. Exiting ...")
                crawler.displayer.show_progression()
            else:
                print("You pressed the Exit key. Exiting ...")
            crawler.kill()
            break
        if char == "r":
            if args.display is True:
                crawler.displayer.pause()

    crawler.join()

    crawler.measurements.store_measurements(end=True)
    crawler.measurements.display_measurements(args.network_to_crawl)


def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def get_ips_from_file(file):
    stdout = open(file, "r")
    ips = list()

    for i in stdout:
        ips.append(i.split("\n")[0])

    stdout.close()
    return ips


if __name__ == "__main__":
    usage = """
    USAGE:      python3 main.py <options>
    EXAMPLES:   (1) python main.py
                    - Launch the bitcoin network crawler with 10 threads.
                (2) python main.py --nb_threads 20
                    - Launch the bitcoin network crawler with 20 threads.
                (3) python main.py --display False
                    - Launch the bitcoin network crawler with 10 threads and not displaying any progression.
                (4) python main.py --display_progression True
                    - Launch the bitcoin network crawler with 10 threads and displaying each thread's progression.
                (5) python main.py --time 10
                    - Launch the bitcoin network crawler with 10 threads for 10 minutes.
    """

    # Using argparse to select the different setting for the run
    parser = ArgumentParser(usage)

    parser.add_argument(
        '--nb_threads',
        help="""Number of threads used by the crawler.
        """,
        type=int,
        default=10
    )

    parser.add_argument(
        '--time',
        help="""Time to crawl.
        """,
        type=float,
        default=-1.0
    )

    parser.add_argument(
        '--no_display',
        help="""No display of the crawling progression.
        """,
        dest='display',
        action='store_false'
    )
    parser.set_defaults(display=True)

    parser.add_argument(
        '--display_progression',
        help="""Display each thread's progression while crawling.
        """,
        dest='display_progression',
        action='store_true'
    )

    parser.add_argument(
        '--network_to_crawl',
        help="""Network that will be crawl.
        """,
        type=str,
        choices=['ipv4', 'ipv6', 'any'],
        default="ipv4"
    )

    parser.add_argument(
        '--seed_file',
        help="""Name of the file that contain the seed IPs that will be used for crawling.
        """,
        type=str,
        default=None,
    )

    parser.set_defaults(display_progression=False)

    args = parser.parse_args()

    main(args)
