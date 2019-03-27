import os
import sys
import time
import traceback
import shutil
from threading import Thread, Event

STOP_EVENT = Event()


def create_measurements_folder(directory="Measurements/"):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        else:
            shutil.rmtree(directory)
            os.makedirs(directory)
    except OSError:
        raise OSError("Error: Failed to create directory: ", directory)


def create_log_folder():
    directory = "Log/"
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
        else:
            shutil.rmtree(directory)
            os.makedirs(directory)
    except OSError:
        print("Error: Failed to create directory: ", directory)


class Measurements_Manager(Thread):

    def __init__(self, measurements):
        Thread.__init__(self)

        self.measurements = measurements
        self.measurements_storage_task_fail = False

        create_measurements_folder()
        create_log_folder()

    def run(self):
        try:
            self.measurements_storage_task()
        except Exception as err:
            self.measurements_storage_task_fail = True
            self.error_recording(str(err))

    def measurements_storage_task(self):
        global STOP_EVENT

        delay = 12

        start = time.time()

        while not (STOP_EVENT.isSet()) and not (self.measurements.get_nb_to_read(
                self.measurements.network_to_crawl) == 0 and self.measurements.get_nb_being_read() == 0):
            if time.time() - start > delay:
                self.measurements.store_measurements()
                start = time.time()
            else:
                time.sleep(5)

    def kill(self):
        STOP_EVENT.set()

    def join(self):
        STOP_EVENT.set()
        Thread.join(self)

    def get_IP_to_read(self):
        return self.measurements.get_IP_to_read()

    def add_IP_readed(self, node_ip):
        return self.measurements.add_IP_readed(node_ip)

    def add_process_ip_stat(self, stat, nb_query, thread_nb):
        self.measurements.add_process_ip_stat(stat, nb_query, thread_nb)
        return

    def add_peer_bitcoin_handshake_duration(self, ip, handshake_duration):
        self.measurements.add_peer_bitcoin_handshake_duration(ip, handshake_duration)

        return

    def add_peer_tcp_handshake_duration(self, ip, handshake_duration):
        self.measurements.add_peer_tcp_handshake_duration(ip, handshake_duration)

        return

    def add_peer_queried(self, ip, nb):
        self.measurements.add_peer_queried(ip, nb)

        return

    def add_active_peer(self, ip):
        self.measurements.add_active_peer(ip)

        return

    def add_connection_failed_stat(self, reason):
        self.measurements.add_connection_failed_stat(reason)

        return

    def add_IP_Service(self, ip, service):
        self.measurements.add_IP_Service(ip, service)

        return

    def add_version_stat(self, version):
        self.measurements.add_version_stat(version)

        return

    def treatAddrPacket(self, rcv_msg):
        self.measurements.treatAddrPacket(rcv_msg)

        return

    def measurements_storage_task_failed(self):
        return self.measurements_storage_task_fail

    def error_recording(self, msg):
        stdout = open("Log/log_Measurements_Manager.txt", "a")

        i = sys.exc_info()

        traceback.print_tb(i[2], file=stdout)

        stdout.write("\n" + (str(msg) + "\n"))

        stdout.close()
