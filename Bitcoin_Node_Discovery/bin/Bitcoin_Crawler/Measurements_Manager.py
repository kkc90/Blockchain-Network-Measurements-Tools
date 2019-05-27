import os
import sys
import time
import traceback
from threading import Thread, Event

from .CrawlingException import *


class Measurements_Manager(Thread):

    def __init__(self, measurements, store=True):
        Thread.__init__(self)

        self.measurements = measurements
        
        self.measurements_storage_task_fail = False

        self.store = store

        self.__stop_event = Event()

    def run(self):
        try:
            self.measurements_storage_task()

        except Exception:
            self.measurements_storage_task_fail = True
            self.error_recording()

    def measurements_storage_task(self):
        delay = 12

        start = time.time()

        while not (self.__stop_event.isSet()) and not (self.measurements.get_nb_to_read(
                self.measurements.network_to_crawl) == 0 and self.measurements.get_nb_being_read() == 0):

            if self.store is True and time.time() - start > delay:
                self.measurements.store_measurements()
                start = time.time()

            else:
                time.sleep(5)

    def kill(self):
        self.__stop_event.set()

    def get_ip_to_read(self):
        while not self.__stop_event.is_set():
            try:
                result = self.measurements.get_ip_to_read()

                return result

            except LockTimeoutException:
                continue

    def add_ip_readed(self, node_ip):
        while not self.__stop_event.is_set():
            try:
                result = self.measurements.add_ip_readed(node_ip)

                return result

            except LockTimeoutException:
                continue

    def add_process_ip_stat(self, stat, nb_query, thread_nb):
        while not self.__stop_event.is_set():
            try:
                result = self.measurements.add_process_ip_stat(stat, nb_query, thread_nb)

                return result

            except LockTimeoutException:
                continue

    def add_peer_bitcoin_handshake_duration(self, ip, handshake_duration):
        while not self.__stop_event.is_set():
            try:
                result = self.measurements.add_peer_bitcoin_handshake_duration(ip, handshake_duration)

                return result

            except LockTimeoutException:
                continue

    def add_peer_tcp_handshake_duration(self, ip, handshake_duration):
        while not self.__stop_event.is_set():
            try:
                result = self.measurements.add_peer_tcp_handshake_duration(ip, handshake_duration)

                return result

            except LockTimeoutException:
                continue

    def add_peer_queried(self, ip, nb):
        while not self.__stop_event.is_set():
            try:
                result = self.measurements.add_peer_queried(ip, nb)

                return result

            except LockTimeoutException:
                continue

    def add_active_peer(self, ip):
        while not self.__stop_event.is_set():
            try:
                result = self.measurements.add_active_peer(ip)

                return result

            except LockTimeoutException:
                continue

    def add_connection_failed_stat(self, reason):
        while not self.__stop_event.is_set():
            try:
                result = self.measurements.add_connection_failed_stat(reason)

                return result

            except LockTimeoutException:
                continue

    def add_ip_service(self, ip, service):
        while not self.__stop_event.is_set():
            try:
                result = self.measurements.add_ip_service(ip, service)

                return result

            except LockTimeoutException:
                continue

    def add_version_stat(self, version):
        while not self.__stop_event.is_set():
            try:
                result = self.measurements.add_version_stat(version)

                return result

            except LockTimeoutException:
                continue

    def add_ip_to_read(self, ips):
        while not self.__stop_event.is_set():
            try:
                result = self.measurements.add_ip_to_read(ips)

                return result

            except LockTimeoutException:
                continue

            except UnknownIPAddressTypeException:
                self.error_recording()

    def measurements_storage_task_failed(self):
        return self.measurements_storage_task_fail

    def error_recording(self):
        directory = "Log/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        stdout = open("Log/Measurements_Manager_log.txt", "a")

        stdout.write("Measurements Manager failed unexpectedly.\n\n")

        ex_type, ex, tb = sys.exc_info()
        traceback.print_exception(ex_type, ex, tb, file=stdout)
        stdout.write('\n\n')

        stdout.close()
