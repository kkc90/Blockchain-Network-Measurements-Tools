#!/usr/bin/python3.6

import os
import shutil
import sys
import termios
import time
import tty
from argparse import ArgumentParser

from DNS_Lookup import *

from Full_Manager_Implementation.Bitcoin_Crawler.Crawler import Crawler as full_manager_crawler
from IP_Manager_Implementation.Bitcoin_Crawler.Crawler import Crawler as ip_manager_crawler
from Measurements_Manager_Implementation.Bitcoin_Crawler.Crawler import Crawler as measurement_manager_crawler
from No_Manager_Implementation.Bitcoin_Crawler.Crawler import Crawler as no_manager_crawler

IMPLEMENTED_TESTS = ["Implementation", "Implementations Comparaison", "Thread Number"]

IMPLEMENTATIONS = {"No_Manager": no_manager_crawler, "Measurements_Manager": measurement_manager_crawler,
                   "IP_Manager": ip_manager_crawler, "Full_Manager": full_manager_crawler}


def main(args):
    global IMPLEMENTED_TESTS

    seed_file = args.seed_file

    if seed_file is None:
        dns_lookup = DNS_Lookup()
        seed_ips = dns_lookup.get_DNS_IP()
    else:
        seed_ips = get_ips_from_file(seed_file)

    # TODO Check for errors
    if args.test_type == IMPLEMENTED_TESTS[0]:
        test_implementations(seed_ips, args.nb_thread, args.nb_connection_per_thread, args.implementation,
                             args.network_to_crawl, args.time_to_crawl, args.display)

    elif args.test_type == IMPLEMENTED_TESTS[1]:
        compare_implementations(seed_ips, args.nb_thread, args.nb_connection_per_thread, args.network_to_crawl,
                                args.time_to_crawl)

    elif args.test_type == IMPLEMENTED_TESTS[2]:
        compare_nb_thread(seed_ips, args.implementation, args.nb_connection_per_thread, args.network_to_crawl,
                          args.time_to_crawl)

    else:
        print("Error: Unvalid Test", file=sys.stderr)


def test_implementations(seed_ips, nb_thread, nb_connection_per_thread, implementation, network_to_crawl,
                         time_to_crawl, display):
    global IMPLEMENTATIONS

    impl = IMPLEMENTATIONS[implementation]

    crawler = impl(seed_ips, time_to_crawl, network_to_crawl, nb_thread, nb_connection_per_thread, display)

    crawler.start()
    a = time.time()

    while True:
        if (time.time() - a) > 3:
            a = time.time()

            if not crawler.isAlive():
                break

        char = getch()

        if char == "q":

            if args.display is True:
                crawler.displayer.show_progression()

                crawler.displayer.display_message("User pressed the Exit key. Exiting ...")
            else:
                print("User pressed the Exit key. Exiting ...")

            crawler.kill()

            break
        if char == "r":

            if args.display is True:
                crawler.displayer.pause()

    crawler.join()

    crawler.measurements.store_measurements(end=True)

    crawler.measurements.display_measurements(args.network_to_crawl)

    check_for_error()


def compare_implementations(seed_ips, nb_thread, nb_connection_per_thread, network_to_crawl, time_to_crawl):
    global IMPLEMENTATIONS

    folder = "Implementations_Study_Measurements/"
    create_measurements_folder(folder)

    add_test_details(folder, seed_ips, nb_connection_per_thread, network_to_crawl, time_to_crawl,
                     nb_thread=nb_thread)

    for impl_name, impl in zip(IMPLEMENTATIONS.keys(), IMPLEMENTATIONS.values()):
        print("Test on ", str(impl_name), " implementation ...\n")

        crawler = impl(seed_ips, time_to_crawl, network_to_crawl, nb_thread, nb_connection_per_thread, display=False,
                       store=False)

        crawler.start()

        crawler.join()

        measurement_folder = (folder + impl_name + "_Measurements/")

        create_measurements_folder(measurement_folder)

        crawler.measurements.store_measurements(end=True, folder=measurement_folder)

        crawler.measurements.display_measurements(args.network_to_crawl, details=False)

        # check_for_error()

        print("")


def compare_nb_thread(seed_ips, implementation, nb_connection_per_thread, network_to_crawl, time_to_crawl):
    global IMPLEMENTATIONS

    impl = IMPLEMENTATIONS[implementation]

    nb_thread = 1
    thread_to_add = 10
    prev_nb_readed = 0

    best_crawler_measurements = None

    folder = "Thread_Study_Measurements/"
    create_measurements_folder(folder)

    folder = "Thread_Study_Measurements/" + implementation + "/"
    create_measurements_folder(folder)

    add_test_details(folder, seed_ips, nb_connection_per_thread, network_to_crawl, time_to_crawl,
                     implementation=implementation)

    while thread_to_add > 1:
        print("Test on ", str(implementation), " implementation with ", str(nb_thread), " thread ...\n")
        crawler = impl(seed_ips, time_to_crawl, network_to_crawl, nb_thread, nb_connection_per_thread, display=False,
                       store=False)

        crawler.start()

        crawler.join()

        crawler.measurements.display_measurements(args.network_to_crawl, details=False)
        print("\n")
        store_general_measurements(folder, (str(nb_thread) + "_thread_measurements"), crawler.measurements)

        nb_readed = crawler.measurements.get_nb_readed()

        if nb_readed < prev_nb_readed:
            nb_thread = nb_thread - thread_to_add
            thread_to_add = int(thread_to_add / 2)
        else:
            best_crawler_measurements = crawler.measurements

        # check_for_error()

        prev_nb_readed = nb_readed
        nb_thread = nb_thread + thread_to_add

    print("\n")
    print("The optimal number of thread is : ", str(nb_thread))
    store_general_measurements(folder, "optimal_nb_thread_measurements", best_crawler_measurements)


def check_for_error():
    if os.path.exists("Log/"):
        logs = os.listdir("Log/")

        if len(logs) > 0:
            raise Exception("Error: Log folder is not empty.")


def store_general_measurements(folder, file_name, measurements):
    stdout = open((folder + file_name), "w+")

    stdout.write(("Crawling began at : " + measurements.start_time.strftime("%Y-%m-%d %H:%M:%S") + "\n"))
    stdout.write(("Crawling done in " + str(
        (measurements.stop_time - measurements.start_time).total_seconds()) + " seconds." + "\n"))
    stdout.write("\n")

    stdout.write(("Measurements : " + "\n\n"))
    nb_readed = measurements.get_nb_readed()
    nb_active = measurements.get_nb_active_peers()
    nb_collected = measurements.get_nb_collected()

    if measurements.network_to_crawl == "ipv4":
        stdout.write((str(nb_readed) + " IPv4 Peers has been processed." + "\n"))
        stdout.write((str(nb_collected) + " Peers has been collected (IPv4 + IPv6)." + "\n"))
    elif measurements.network_to_crawl == "ipv6":
        stdout.write((str(nb_readed) + " IPv6 Peers has been processed."))
        stdout.write((str(nb_collected) + " Peers has been collected (IPv4 + IPv6)." + "\n"))
    else:
        stdout.write((str(nb_readed) + " Peers has been processed (IPv4 + IPv6)."))
        stdout.write((str(nb_collected) + " Peers has been collected (IPv4 + IPv6)." + "\n"))

    stdout.write((str(nb_active) + " Active peers has been detected." + "\n"))

    stdout.close()


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


def store_seed_ips(file_name, ips):
    stdout = open(file_name, "w+")

    for ip in ips:
        stdout.write((str(ip) + "\n"))

    stdout.close()


def add_test_details(directory, seed_ips, nb_connection_per_thread, network_to_crawl, time_to_crawl,
                    nb_thread=None, implementation=None):
    stdout = open((directory + "Test_Details"), "w+")

    if implementation is not None:
        stdout.write(("Implementation : " + str(implementation) + "\n"))

    if nb_thread is not None:
        stdout.write(("Number of Thread : " + str(nb_thread) + "\n"))

    stdout.write(("Number of Connetion per Thread : " + str(nb_connection_per_thread) + "\n"))

    stdout.write(("Network crawled : " + str(network_to_crawl) + "\n"))

    stdout.write(("Expected Crawling Time per tests: " + str(time_to_crawl) + " minutes\n"))

    stdout.write(("Number of Seed IPs : " + str(len(seed_ips)) + "\n"))

    stdout.write(("Seed Ips : " +str(seed_ips) + "\n"))

    stdout.close()


def create_measurements_folder(directory="Measurements/"):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        else:
            shutil.rmtree(directory)
            os.makedirs(directory)
    except OSError:
        raise OSError("Error: Failed to create directory: ", directory)


if __name__ == "__main__":
    usage = """
    USAGE:      python3 test.py <options>
    EXAMPLES:   (1) python test.py --test_type "Implementations"
                    - Launch a test comparing the different implementations of the crawler when each of them 
                    are crawling for 10 minutes.
                    
                (2) python test.py --test_type "Implementations" --time_to_crawl 60
                    - Launch a test comparing the different implementations of the crawler when each of them 
                    are crawling for 60 minutes.
                    
                (3) python test.py --test_type "Thread_Number"
                    - Launch a test studying the impact of the number of threads on the crawling for the "No_Manager" 
                    implementation.
                    
                (4) python test.py --test_type "Thread_Number" --implementation "IP_Manager"
                    - Launch a test studying the impact of the number of threads on the crawling for the first
                     "IP_Manager" implementation.
    """

    parser = ArgumentParser(usage)

    parser.add_argument(
        '--test_type',
        help="""Type of test that will be run.
        """,
        type=str,
        choices=IMPLEMENTED_TESTS,
        default="Implementations",
        required=True,
    )

    parser.add_argument(
        '--implementation',
        help="""Implementation that will be tested.
        """,
        type=str,
        choices=IMPLEMENTATIONS.keys(),
        required="Thread Number" in sys.argv or "Implementation" in sys.argv
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
        '--time_to_crawl',
        help="""Time to crawl of each crawlers (minutes).
        """,
        type=float,
        default=10,
    )

    parser.add_argument(
        '--nb_thread',
        help="""Number of threads used by the crawler.
        """,
        type=int,
        default=10
    )

    parser.add_argument(
        '--nb_connection_per_thread',
        help="""Number of connection per thread used by the crawler.
        """,
        type=int,
        default=1
    )

    parser.add_argument(
        '--seed_file',
        help="""Name of the file that contain the seed IPs that will be used for crawling.
        """,
        type=str,
        default=None,
    )

    parser.add_argument(
        '--no_display',
        help="""No display of the crawling progression.
        """,
        dest='display',
        action='store_false'
    )

    parser.set_defaults(display=True)

    args = parser.parse_args()

    main(args)
