import datetime
import time
from threading import Thread

from .Displayer import Displayer
from .Measurements import Measurements
from .Measurements_Manager import Measurements_Manager
from .Network import *
from .Crawler_Constant import *
from .Util import *
from .IP_Manager import *


class Crawler(Thread):

    def __init__(self, seed_ips, time_to_crawl, network_to_crawl, nb_thread, nb_connection_per_thread=1,
                 display=True, display_progression=False, monitor_connections=False, store=True):
        Thread.__init__(self)

        """
                    CRAWLING INFORMATION
        """

        self.seed_ips = seed_ips
        self.network_to_crawl = network_to_crawl

        self.src_ip = get_public_ip()

        """
                    THREADS MANAGEMENT
        """

        self.nb_thread = nb_thread
        self.nb_connection_per_thread = nb_connection_per_thread

        self.time_to_crawl = time_to_crawl * 60  # seconds
        self.is_killed = False

        self.monitor_connections = monitor_connections

        """
                    MEASUREMENTS MANAGEMENT    
        """

        self.measurements = Measurements(self.network_to_crawl, self.nb_thread)
        self.measurements.add_seed_ip_to_read(self.seed_ips)

        self.measurements_manager = Measurements_Manager(self.measurements, store)

        """
                    DISPLAY MANAGEMENT
        """

        if display:
            self.displayer = Displayer(self.measurements_manager, nb_thread, network_to_crawl, display_progression)
        else:
            self.displayer = None

        """
                    THREADS INITIALISATION
        """

        self.ip_manager = IP_Manager(self.measurements, self.measurements_manager, self.network_to_crawl, self.nb_thread)

        self.threads = []

        for thread_id in range(0, self.nb_thread):
            thread = Network_Manager.Network_Manager(self.src_ip, Network_Constant.Network_Constant.DEFAULT_PORT,
                                                     Protocol.Protocol_Constant.NODE_NONE,
                                                     Crawler_Constant.ORIGIN_NETWORK, self.measurements_manager,
                                                     self.displayer, thread_id, self.ip_manager,
                                                     self.nb_connection_per_thread, self.monitor_connections)

            # thread = IP_Lookup(self.measurements_manager, self.network_to_crawl, self.src_ip, i, self.displayer,
            #                    self.nb_connection_per_thread, self.monitor_connections)

            self.threads.append(thread)

    def has_been_killed(self):
        return self.is_killed

    def run(self):
        self.measurements.set_start_time(datetime.datetime.now())

        self.measurements_manager.start()

        if self.displayer is not None:
            self.displayer.start()

        self.ip_manager.start()

        for thread in self.threads:
            thread.start()

        # If a timeout has been given in argument => Kill after timeout has been reached
        if self.time_to_crawl > 0:
            self.kill_after_timeout(self.time_to_crawl)

        for thread in self.threads:
            thread.join()

        self.ip_manager.join()
        self.measurements_manager.join()

        if self.displayer is not None:
            self.displayer.join()

        if self.is_killed is False:
            print("Press a key to get crawling measurements.")

    def kill_after_timeout(self, timeout):
        start = time.time()

        while time.time() - start < timeout and not self.is_killed:
            continue

        if self.is_killed is not True:
            if self.displayer is not None:
                self.displayer.display_message("Crawling time_to_crawl is over. Exiting ...")

            else:
                print("Crawling time_to_crawl is over. Exiting ...")

            self.kill()

    def kill(self):
        if self.is_killed is False:
            self.is_killed = True

            i = 0
            while i < self.nb_thread:
                self.threads[i].kill()
                i = i + 1

            self.measurements_manager.kill()
