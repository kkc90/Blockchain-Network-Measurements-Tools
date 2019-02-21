from threading import Thread, Event
from MeasurementsException import *

import time
import queue
import traceback, sys
STOP_EVENT = Event()


class Measurements_Manager(Thread):

    def __init__(self, measurements):
        Thread.__init__(self)

        self.measurements = measurements
        self.measurements_queue = queue.Queue()
        self.measurements_storage_task_fail = False

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
                self.process_queue()


    def join(self):
        STOP_EVENT.set()
        Thread.join(self)

        while self.process_queue():
            continue

    def get_IP_to_read(self):
        return self.measurements.get_IP_to_read()

    def add_IP_readed(self, node_ip):
        return self.measurements.add_IP_readed(node_ip)

    def process_queue(self):
        try:
            measure = self.measurements_queue.get(block=False)
        except queue.Empty:
            return False

        type = measure["type"]

        if type == "process_stat":
            stat = measure["stat"]
            nb_query = measure["nb_query"]
            thread_nb = measure["thread_nb"]

            self.measurements.add_process_ip_stat(stat, nb_query, thread_nb)

        elif type == "bitcoin_handshake":
            ip = measure["ip"]
            handshake_duration = measure["handshake_duration"]

            self.measurements.add_peer_bitcoin_handshake_duration(ip, handshake_duration)

        elif type == "tcp_handshake":
            ip = measure["ip"]
            handshake_duration = measure["handshake_duration"]

            self.measurements.add_peer_tcp_handshake_duration(ip, handshake_duration)

        elif type == "peer_queried":
            ip = measure["ip"]
            nb = measure["nb_peer"]

            self.measurements.add_peer_queried(ip, nb)

        elif type == "active_peer":
            ip = measure["ip"]

            self.measurements.add_active_peer(ip)

        elif type == "connection_failed_stat":
            reason = measure["reason"]

            self.measurements.add_connection_failed_stat(reason)

        elif type == "IP_Service":
            ip = measure["ip"]
            service = measure["service"]

            self.measurements.add_IP_Service(ip, service)

        elif type == "version_stat":
            version = measure["version"]

            self.measurements.add_version_stat(version)

        elif type == "AddrPacket":
            rcv_msg = measure["rcv_msg"]

            self.measurements.treatAddrPacket(rcv_msg)

        else:
            raise UnknownMeasureException(("The Measure type " + str(type) + " is unknown"))

        self.measurements_queue.task_done()

        return True

    def add_process_ip_stat(self, stat, nb_query, thread_nb):
        self.measurements.add_process_ip_stat(stat, nb_query, thread_nb)
        return

        msg = dict()

        msg["type"] = "process_stat"

        msg["stat"] = stat
        msg["nb_query"] = nb_query
        msg["thread_nb"] = thread_nb

        self.measurements_queue.put(msg, block=True)

    def add_peer_bitcoin_handshake_duration(self, ip, handshake_duration):
        self.measurements.add_peer_bitcoin_handshake_duration(ip, handshake_duration)

        return
        msg = dict()

        msg["type"] = "bitcoin_handshake"

        msg["ip"] = ip
        msg["handshake_duration"] = handshake_duration

        self.measurements_queue.put(msg, block=True)

    def add_peer_tcp_handshake_duration(self, ip, handshake_duration):
        self.measurements.add_peer_tcp_handshake_duration(ip, handshake_duration)

        return
        msg = dict()

        msg["type"] = "tcp_handshake"

        msg["ip"] = ip
        msg["handshake_duration"] = handshake_duration

        self.measurements_queue.put(msg, block=True)

    def add_peer_queried(self, ip, nb):
        self.measurements.add_peer_queried(ip, nb)

        return
        msg = dict()

        msg["type"] = "peer_queried"

        msg["ip"] = ip
        msg["nb_peer"] = nb

        self.measurements_queue.put(msg, block=True)

    def add_active_peer(self, ip):
        self.measurements.add_active_peer(ip)

        return
        msg = dict()

        msg["type"] = "active_peer"

        msg["ip"] = ip

        self.measurements_queue.put(msg, block=True)

    def add_connection_failed_stat(self, reason):
        self.measurements.add_connection_failed_stat(reason)

        return
        msg = dict()

        msg["type"] = "connection_failed_stat"

        msg["reason"] = reason

        self.measurements_queue.put(msg, block=True)

    def add_IP_Service(self, ip, service):
        self.measurements.add_IP_Service(ip, service)

        return
        msg = dict()

        msg["type"] = "IP_Service"

        msg["ip"] = ip
        msg["service"] = service

        self.measurements_queue.put(msg, block=True)

    def add_version_stat(self, version):
        self.measurements.add_version_stat(version)

        return
        msg = dict()

        msg["type"] = "version_stat"

        msg["version"] = version

        self.measurements_queue.put(msg, block=True)

    def treatAddrPacket(self, rcv_msg):
        self.measurements.treatAddrPacket(rcv_msg)

        return
        msg = dict()

        msg["type"] = "AddrPacket"

        msg["rcv_msg"] = rcv_msg

        self.measurements_queue.put(msg, block=True)

    def measurements_storage_task_failed(self):
        return self.measurements_storage_task_fail

    def error_recording(self, msg):
        stdout = open("Log/log_Measurements_Manager.txt", "a")

        i = sys.exc_info()

        traceback.print_tb(i[2], file=stdout)

        stdout.write("\n" + (str(msg) + "\n"))

        stdout.close()
