from threading import Thread
from threading import Event
from .CrawlingException import *

import traceback
import queue
import sys
import os


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

    def run(self):
        try:
            self.manage_ips()

        except Exception:
            self.error_recording()
            self.notify_message_to_threads("Exception")

    def manage_ips(self):
        while not self.__stop_event.isSet():
                try:
                    if self.get_ip_queue.qsize() < 2 * self.nb_thread:
                        while self.get_ip_queue.qsize() < 5 * self.nb_thread:
                            result = self.measurements_manager.get_ip_to_read()
                            self.put_message_in_queue(self.get_ip_queue, result)
                    else:
                        try:
                            node_ip = self.remove_ip_queue.get(block=False)
                            self.remove_ip_queue.task_done()
                            self.measurements_manager.add_ip_readed(node_ip)
                        except queue.Empty:
                            continue

                except NoMoreIPToProcessException:
                    self.notify_message_to_threads("nomoreip")
                    self.__stop_event.set()
                    break

                except LockTimeoutException:
                    continue
                except SemaphoreTimeoutException:
                    continue
                except UnknownIPAddressTypeException:
                    continue

    def get_ip(self):
        try:
            result = self.get_ip_queue.get(False)

            self.get_ip_queue.task_done()

        except queue.Empty:
            result = None

        if result == "nomoreip":
            raise NoMoreIPToProcessException("NoMoreIPToProcess Exception: No more IP to process")

        elif result == "Exception":
            raise Exception("Exception: IP Manager process fail unexpectedly.")

        return result

    def remove_ip(self, node_ip):
        self.put_message_in_queue(self.remove_ip_queue, node_ip)

    def kill(self):
        self.__stop_event.set()

    def join(self, **kwargs):
        self.__stop_event.set()
        Thread.join(self)

    def error_recording(self):
        directory = "Log/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        stdout = open("Log/IP_Manager_log.txt", "a")

        stdout.write("IP Manager failed unexpectedly.\n\n")

        ex_type, ex, tb = sys.exc_info()
        traceback.print_exception(ex_type, ex, tb, file=stdout)
        stdout.write('\n\n')

        stdout.close()

    def notify_message_to_threads(self, msg):
        i = 0
        while i < self.nb_thread:
            while not self.__stop_event.isSet():
                try:
                    self.get_ip_queue.put(msg)
                    break

                except queue.Full:
                    continue
            i = i + 1

    def put_message_in_queue(self, queue1, msg):
        while not self.__stop_event.isSet():

            try:
                queue1.put(msg, block=False)
                break

            except queue.Full:
                continue
