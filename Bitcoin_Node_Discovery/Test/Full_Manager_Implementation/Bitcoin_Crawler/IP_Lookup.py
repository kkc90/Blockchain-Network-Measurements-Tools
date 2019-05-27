import os
import sys
import traceback
import datetime
from threading import Thread, Event

from .CrawlingException import *
from .Crawler_Constant import *
from .Network import *


class IP_Lookup(Thread):
    def __init__(self, measurements_manager, network_to_crawl, src_ip, thread_nb, displayer, ip_manager,
                 nb_connection_per_thread, monitor_connections):
        Thread.__init__(self)

        self.src_ip = src_ip
        self.src_port = Network_Constant.Network_Constant.DEFAULT_PORT
        self.network_to_crawl = network_to_crawl

        self.thread_id = thread_id

        self.crawling_done = False

        self.measurements_manager = measurements_manager

        self.nb_connection_per_thread = nb_connection_per_thread

        self._network_manager = Network_Manager.Network_Manager(self.src_ip, self.src_port,
                                                                Protocol.Protocol_Constant.NODE_NONE,
                                                                Crawler_Constant.ORIGIN_NETWORK,
                                                                measurements_manager, displayer, thread_id,
                                                                nb_connection_per_thread,
                                                                monitor_connections)

        self.displayer = displayer

        self.ip_manager = ip_manager

        self.monitor_connections = monitor_connections

        self.__stop_event = Event()

    def run(self):
        self._network_manager.start()

        try:
            self.crawl()

            self.measurements_manager.measurements.set_stop_time(datetime.datetime.now())

        except Exception:
            self.error_recording()
            self._network_manager.kill()
            self.measurements_manager.measurements.set_stop_time(datetime.datetime.now())

        self._network_manager.join()

        if self.crawling_done:
            self.display_progression("No More Ip To Process : Crawling Done.")

        else:
            self.display_progression("Crawling End but still IP to process.")

    def kill(self):
        self.__stop_event.set()

    def hasFinish(self):
        return not ((not self.crawling_done) and (not self.__stop_event.isSet()))

    def get_ip_to_read_from_measurements(self):
        self.display_progression("Picking a Peer to query ...")

        while not self.__stop_event.isSet():
            peer_info = self.ip_manager.get_ip()

            if peer_info is not None:
                ip, port = peer_info

                if ip is not None and port is not None:
                    return ip, port

        return None

    def crawl(self):

        try:
            while not self.__stop_event.is_set():

                if self._network_manager.need_more_peer():
                    peer_info = self.get_ip_to_read_from_measurements()

                    if peer_info is None:
                        break

                    connection = self._network_manager.connect(
                        str(peer_info[0]), peer_info[1], Protocol.Protocol_Constant.NODE_NONE,
                        connection_timeout=Crawler_Constant.CONNECTION_TIMEOUT)

        except NoMoreIPToProcessException:
            self.crawling_done = True

        self._network_manager.kill()

    def error_recording(self):
        directory = "Log/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        directory = "Log/Thread_" + str(self.thread_id) + "/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        stdout = open((directory + "log.txt"), "a")

        stdout.write("Thread " + str(self.thread_id) + " failed unexpectedly.\n\n")

        ex_type, ex, tb = sys.exc_info()
        traceback.print_exception(ex_type, ex, tb, file=stdout)
        stdout.write('\n\n')

        stdout.close()

        self.display_error_message("An error occured (cfr. log for details). Press <q> to end.")

        self.display_progression("Error : Thread failed unexpectedly.")

    def display_error_message(self, string):
        if self.displayer is not None:
            self.displayer.display_error_message(string)
        else:
            print(string)

    def display_message(self, string):
        if self.displayer is not None:
            self.displayer.display_message(string)

    def display_progression(self, string):
        if self.displayer is not None:
            self.displayer.display_thread_progression(string, self.thread_id)
