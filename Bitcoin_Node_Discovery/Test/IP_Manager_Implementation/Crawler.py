import datetime
import time
from threading import Thread
import getip

from .Displayer import Displayer
from .Measurements import Measurements
from .Measurements_Manager import Measurements_Manager
from .Protocol import Protocol
from .IP_Lookup import IP_Lookup
from .IP_Manager import *


class Crawler(Thread):
    def __init__(self, seed_ips, time, network_to_crawl, nb_thread, display, display_progression):
        Thread.__init__(self)
        self.seed_ips = seed_ips
        self.network_to_crawl = network_to_crawl
        self.src_port = 8333
        self.dst_port = 8333

        self.src_ip = getip.get()

        self.target_service = Protocol.NODE_NETWORK
        self.nb_thread = nb_thread
        self.threads = []

        self.measurements = Measurements(self.network_to_crawl, self.nb_thread)
        self.measurements.add_seed_IP_to_read(self.seed_ips)

        self.measurements_manager = Measurements_Manager(self.measurements)

        self.time = time * 60  # seconds
        self.killed_by_user = False
        self.killed_by_timeout = False

        if display:
            self.displayer = Displayer(self.measurements_manager, nb_thread, network_to_crawl, display_progression)
        else:
            self.displayer = None

        self.ip_manager = IP_Manager(self.measurements, self.measurements_manager, self.network_to_crawl, self.nb_thread)

    def run(self):
        self.measurements.set_start_time(datetime.datetime.now())

        self.measurements_manager.start()

        if self.displayer is not None:
            self.displayer.start()

        i = 0

        self.ip_manager.start()

        while i < self.nb_thread:
            thread = IP_Lookup(self.measurements_manager, self.network_to_crawl, self.src_ip, self.target_service, i,
                               self.displayer, self.ip_manager)
            thread.start()
            self.threads.append(thread)
            i = i + 1

        if (self.time > 0):
            self.kill_after_timeout(self.time)

        i = 0
        while i < self.nb_thread:
            self.threads[i].join()
            i = i + 1

        self.ip_manager.join()
        self.measurements_manager.join()

        if self.displayer is not None:
            self.displayer.join()

        if self.killed_by_timeout is not True:
            print("Crawling end. Press key to get crawling statistics")

    def kill_after_timeout(self, timeout):
        start = time.time()

        while (time.time() - start < timeout and not self.killed_by_user):
            continue

        if self.killed_by_user is not True:
            self.killed_by_timeout = True
            self.kill()

    def kill(self):
        if self.displayer is not None:
            if self.killed_by_timeout is True:
                self.displayer.display_message("Crawling time is over. Exiting ...")
            else:
                self.displayer.display_message("User pressed the Exit key. Exiting ...")

            self.displayer.show_progression()
        else:
            if self.killed_by_timeout is True:
                print("Crawling time is over. Exiting ...")
            else:
                print("User pressed the Exit key. Exiting ...")

        self.killed_by_user = True

        i = 0
        while i < self.nb_thread:
            self.threads[i].kill()
            i = i + 1
