#!/usr/bin/python3.6

from argparse import ArgumentParser
from Test_No_Manager.Node_Discovery_Threaded.DNS_Lookup import *

IMPLEMENTED_TEST = ["Implementations", "Thread_Number"]
IMPLEMENTATIONS = ["No_Manager", "Measurements_Manager", "IP_Manager", "Full_Manager"]

def main():
    dns_lookup = DNS_Lookup()
    ips = dns_lookup.get_DNS_IP()

def store_seed_ips(self, file_name, ips):
    stdout = open(file_name, "w+")

    for i in ips:
        stdout.write(())

if __name__ == "__main__":
    usage = """
    USAGE:      python3 test.py <options>
    EXAMPLES:   (1) python test.py --test_type "Implementations"
                    - Launch a test comparing the different implementations of the crawler when each of them are crawling for 10 minutes.
                (2) python test.py --test_type "Implementations" --time 60
                    - Launch a test comparing the different implementations of the crawler when each of them are crawling for 60 minutes.
                (3) python test.py --test_type "Thread_Number"
                    - Launch a test studying the impact of the number of threads on the crawling for the "No_Manager" implementation.
                (4) python test.py --test_type "Thread_Number" --implementation "IP_Manager"
                    - Launch a test studying the impact of the number of threads on the crawling for the "IP_Manager" implementation.
    """

    # Using argparse to select the different setting for the run
    parser = ArgumentParser(usage)

    parser.add_argument(
        '--test_type',
        help="""Type of test that will be run.
        """,
        type=str,
        choices = IMPLEMENTED_TEST,
        default="Implementations",
        required=True,
    )

    parser.add_argument(
        '--implementation',
        help="""Implementation that will be tested.
        """,
        type=str,
        choices = IMPLEMENTATIONS,
        default="No_Manager"
    )

    parser.add_argument(
        '--time',
        help="""Time to crawl of each crawlers.
        """,
        type=float,
        default=10
    )

    TEST_TYPE = args.test_type
    IMPLEMENTATION = args.implementation
    CRAWLING_TIME = args.time

    main()
