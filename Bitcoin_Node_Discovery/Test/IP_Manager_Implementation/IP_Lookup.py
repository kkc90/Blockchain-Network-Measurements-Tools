import os
import sys
import time
import traceback
import queue
import datetime
from threading import Thread, Event, Lock

from .CrawlingException import *
from .P2P_Connection import P2P_Connection
from .P2P_Receiver import P2P_Receiver
from .P2P_Sender import P2P_Sender

STOP_EVENT = Event()
PRINT_LOCK = Lock()


class IP_Lookup(Thread):
    ORIGIN_NETWORK = 'mainnet'

    def __init__(self, measurements_manager, network_to_crawl, src_ip, service, thread_nb, displayer, ip_manager):
        Thread.__init__(self)
        Thread.setName(self, name=("IP Lookup Thread " + str(thread_nb)))

        self.network_to_crawl = network_to_crawl
        self.src_port = 8333
        self.dst_port = 8333
        self.src_ip = src_ip
        self.target_service = service
        self.thread_nb = thread_nb
        self.crawling_done = False

        self.measurements_manager = measurements_manager
        self.displayer = displayer

        self.sender = P2P_Sender(None, self.ORIGIN_NETWORK)

        self.receiver = P2P_Receiver(None, self.ORIGIN_NETWORK)

        self.ip_manager = ip_manager

    def run(self):
        global STOP_EVENT

        self.sender.start()
        self.receiver.start()

        self.crawl()

        if self.crawling_done:
            if self.displayer is not None:
                self.display_msg("No More Ip To Process : Crawling Done.")
        else:
            if self.displayer is not None:
                self.display_msg("Crawling End but still IP to process.")

        self.measurements_manager.measurements.set_stop_time(datetime.datetime.now())

        self.sender.join()
        self.receiver.join()

    def display_msg(self, msg):
        if self.displayer is not None:
            self.displayer.display_thread_progression(msg, self.thread_nb)

    def get_IP_to_read(self):

        self.display_msg("Picking a Peer to query ...")

        result = None
        while not STOP_EVENT.isSet():
            try:
                result = self.ip_manager.get_ip()
                break
            except queue.Empty:
                continue

        return result

    def add_IP_readed(self, node_ip):
        while not STOP_EVENT.isSet():
            try:
                self.ip_manager.remove_ip(node_ip)
                break
            except queue.Full:
                continue

        self.display_msg(("Peer " + str(node_ip) + " has been processed."))

    def crawl(self):
        global STOP_EVENT
        global PRINT_LOCK

        node_ip = None

        while (not self.crawling_done) and (not STOP_EVENT.isSet()):
            co_to_peer = None
            try:
                try:
                    node_ip = self.get_IP_to_read()

                    if node_ip is None:
                        break
                except NoMoreIPToProcessException:
                    self.crawling_done = True
                    self.displayer.show_progression()
                    break
                co_to_peer = P2P_Connection(self.target_service, str(node_ip), self.dst_port, self.src_port, self.src_ip,
                                            self.measurements_manager, self.thread_nb, self.displayer,
                                            self.sender, self.receiver)
                start = time.time()
                nb_query = co_to_peer.crawl_ip()
                stop = time.time()

                self.measurements_manager.add_process_ip_stat(stop - start, nb_query, self.thread_nb)

                self.add_IP_readed(node_ip)

            except Exception:
                tracebacks = self.sender.get_tracebacks() + self.receiver.get_tracebacks()
                if(co_to_peer is not None):
                    tracebacks = tracebacks + co_to_peer.get_tracebacks()
                tracebacks.append(sys.exc_info())

                self.error_recording(self.thread_nb, tracebacks, node_ip)

                continue

    def kill(self):
        STOP_EVENT.set()

    def hasFinish(self):
        return not ((not self.crawling_done) and (not STOP_EVENT.isSet()))

    def create_log_node_folder(self, node_ip):
        directory = "Log/Log_" + str(node_ip) + "/"
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            self.displayer.display_message("Error: Failed to create directory: ", directory)

    def error_recording(self, thread_nb, tracebacks, node_ip=None):
        if (node_ip is not None):
            self.create_log_node_folder(node_ip)

            stdout = open(("Log/Log_" + str(node_ip) + "/log_" + str(node_ip) + ".txt"), "a")

            stdout.write("Thread " + str(thread_nb) + " failed unexpectedly while querying " + str(node_ip) + ".\n\n")

            for i in tracebacks:
                traceback.print_tb(i[2], file=stdout)
                stdout.write((str(i[1]) + "\n\n"))

            stdout.close()
        else:
            stdout = open("Log/log.txt", "a")

            stdout.write("Thread " + str(thread_nb) + " failed unexpectedly.\n\n")

            for i in tracebacks:
                traceback.print_tb(i[2], file=stdout)
                stdout.write((str(i[1]) + "\n\n"))

            stdout.close()
