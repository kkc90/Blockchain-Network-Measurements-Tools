#!/usr/bin/python3.6

import datetime
import os
import sys
import termios
import time
import tty
from argparse import ArgumentParser

from Crawler import Crawler
from DNS_Lookup import DNS_Lookup
from Displayer import Displayer
from Measurements import Measurements
from Measurements_Manager import Measurements_Manager


def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def main():
    global NETWORK_TO_CRAWL
    global NB_THREAD

    start = time.time()
    now = datetime.datetime.now()
    create_measurements_folder()
    create_log_folder()

    measurements = Measurements(NETWORK_TO_CRAWL, NB_THREAD, now)

    if SEED_FILE is None:
        dns_lookup = DNS_Lookup()
        measurements.add_dns_list_IP_to_read(dns_lookup.get_DNS_IP())
    else:
        measurements.add_seed_IP_to_read(SEED_FILE)

    # TODO deal with example with no connectivity

    measurements_manager = Measurements_Manager(measurements)

    init_crawling(measurements, measurements_manager)
    stop = time.time()

    measurements.store_measurements()

    print("")

    print(("Crawling began at : " + now.strftime("%Y-%m-%d %H:%M:%S")))
    print(("Crawling done in " + str(stop - start) + " seconds."))
    print("")

    os.system("clear")
    display_measurements(measurements)


def init_crawling(measurements, measurements_manager):
    global NETWORK_TO_CRAWL
    global NB_THREAD
    global DISPLAY
    global DISPLAY_PROGRESSION

    if DISPLAY:
        displayer = Displayer(measurements, measurements_manager, NB_THREAD, NETWORK_TO_CRAWL, DISPLAY_PROGRESSION)
    else:
        displayer = None

    crawler = Crawler(measurements, measurements_manager, NETWORK_TO_CRAWL, NB_THREAD, displayer)

    if DISPLAY:
        displayer.start()

    measurements_manager.start()

    crawler.start()
    a = time.time()

    while True:
        if (time.time() - a) > 3:
            a = time.time()
            if (crawler.isFinish()):
                break

        # TODO Problem deal with no timeout and with printing and with killing if measurements_manager failed.
        char = getch()

        if char == "q":
            if (DISPLAY):
                displayer.display_message("You pressed the Exit key. Exiting ...")
                displayer.show_progression()
            else:
                print("You pressed the Exit key. Exiting ...")
            crawler.kill()
            break
        if char == "r":
            if (DISPLAY):
                displayer.pause()

    crawler.join()

    if DISPLAY and displayer.isAlive():
        displayer.join()

    measurements_manager.join()


def create_measurements_folder():
    directory = "Measurements/"
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        raise OSError("Error: Failed to create directory: ", directory)


def create_log_folder():
    directory = "Log/"
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print("Error: Failed to create directory: ", directory)


def display_measurements(measurements):
    global NETWORK_TO_CRAWL

    print("Measurements : ")
    nb_readed = measurements.get_nb_readed()
    nb_active = measurements.get_nb_active_peers()
    if NETWORK_TO_CRAWL == "ipv4":
        print(str(nb_readed) + " IPv4 Peers has been processed.")
        nb_to_read = measurements.get_nb_to_read()
        print(str(nb_to_read) + " Peers has been collected (IPv4 + IPv6).")
    elif NETWORK_TO_CRAWL == "ipv6":
        print(str(nb_readed) + " IPv6 Peers has been processed.")
        nb_to_read = measurements.get_nb_to_read()
        print(str(nb_to_read) + " Peers has been collected (IPv4 + IPv6).")
    else:
        print(str(nb_readed) + " Peers has been processed and collected (IPv4 + IPv6).")

    print((str(nb_active) + " Active peers."))
    print("\n")
    display_failed_connection_stat(measurements)
    print("\n")
    display_version_table(measurements)
    print("\n")
    display_service_table(measurements)


def display_failed_connection_stat(measurements):
    failed_connection_stat = measurements.get_failed_connection_stat()

    for i in failed_connection_stat.items():
        print(("Number of connection failed because of \"" + str(i[0]) + "\" = " + str(i[1]) + " peers"))


def display_version_table(measurements):
    print("Version Statistics :")
    for i in measurements.get_version_stat().items():
        print(("Version " + str(i[0]) + " : " + str(i[1]) + " peers"))


def display_service_table(measurements):
    print("Service Statistics :")
    for i in measurements.get_service_stat().items():
        print(("Service " + str(i[0]) + " : " + str(i[1]) + " peers"))


def string_to_bool(string):
    if string == "True":
        return True
    elif string == "False":
        return False
    else:
        return None


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
    )

    parser.set_defaults(display_progression=False)

    args = parser.parse_args()

    NB_THREAD = args.nb_threads
    DISPLAY = args.display
    DISPLAY_PROGRESSION = args.display_progression
    NETWORK_TO_CRAWL = args.network_to_crawl
    SEED_FILE = args.seed_file

    main()
