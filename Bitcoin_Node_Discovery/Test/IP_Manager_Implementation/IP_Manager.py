from threading import Thread
from threading import Event
from Protocol.ProtocolException import *
from CrawlingException import *

import traceback
import queue
import sys


class IP_Manager(Thread):
    def __init__(self, measurements, measurements_manager, network_to_crawl, nb_thread):
        Thread.__init__(self)
        Thread.setName(self, name="IP Manager")

        self.get_ip_queue = queue.Queue()
        self.remove_ip_queue = queue.Queue()

        self.measurements = measurements
        self.measurements_manager = measurements_manager
        self.__stop_event = Event()
        self.network_to_crawl = network_to_crawl
        self.nb_thread = nb_thread

        self.tracebacks = []

    def run(self):
        try:
            self.manage_ips()
        except Exception as err:
            i = 0
            self.error_recording(str(err))
            while i < self.nb_thread:
                while not self.__stop_event.isSet():
                    try:
                        self.get_ip_queue.put("Exception")
                        break
                    except queue.Full:
                        continue
                i = i + 1

    def manage_ips(self):
        while not self.__stop_event.isSet():
            if self.get_ip_queue.qsize() < 2 * self.nb_thread:
                try:
                    while self.get_ip_queue.qsize() < 5 * self.nb_thread:
                        ip = self.measurements.get_IP_to_read()

                        while not self.__stop_event.isSet():
                            try:
                                self.get_ip_queue.put(ip, block=False)
                                break
                            except queue.Full:
                                continue

                except NoMoreIPToProcessException:
                    i = 0
                    while i < self.nb_thread:
                        while not self.__stop_event.isSet():
                            try:
                                self.get_ip_queue.put("nomoreip", block=False)
                                break
                            except queue.Full:
                                continue
                        i = i + 1
                except LockTimeoutException:
                    continue
                except SemaphoreTimeoutException:
                    continue
                except UnknownIPAddressTypeException:
                    continue
            else:
                try:
                    node_ip = self.remove_ip_queue.get(block=False)
                    self.remove_ip_queue.task_done()
                    self.measurements.add_IP_readed(node_ip)
                except queue.Empty:
                    continue

    def get_ip(self):
        result = self.get_ip_queue.get(False)
        self.get_ip_queue.task_done()

        if result == "nomoreip":
            raise NoMoreIPToProcessException("NoMoreIPToProcess Exception: No more IP to process")
        elif result == "Exception":
            raise Exception("Exception: IP Manager process fail unexpectedly.")

        return result

    def remove_ip(self, node_ip):
        self.remove_ip_queue.put(node_ip, False)

    def kill(self):
        self.__stop_event.set()

    def join(self):
        self.__stop_event.set()
        Thread.join(self)

    def get_tracebacks(self):
        return self.tracebacks

    def error_recording(self, msg):
        stdout = open("Log/log_IP_Manager.txt", "a")

        i = sys.exc_info()

        traceback.print_tb(i[2], file=stdout)
        stdout.write("\n" + (str(msg) + "\n"))

        stdout.close()
