"""
KeyChain key-value store (stub).

NB: Feel free to extend or modify.
"""
import shutil
import sys
import time
import traceback
import math
import datetime
from threading import Thread, Event

from .Blockchain import *
from .Network import *
from .Util import *

PRIVATE_KEY_FILE = "private_key.pem"

COLUMNS, ROWS = shutil.get_terminal_size(fallback=(80, 24))


def print_there(x, y, text):
    global COLUMNS, ROWS

    empty_line = ""
    for i in range(0, COLUMNS):
        empty_line += " "

    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x + 1, 0, empty_line))
    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x + 1, y + 1, text))
    sys.stdout.flush()


class Callback:
    def __init__(self, transaction, blockchain):
        self._transaction = transaction
        self._blockchain = blockchain

    def wait(self):
        """Wait until the transaction appears in the blockchain."""

        while True:
            if self._blockchain.containsTransaction(self._transaction):
                break

    def completed(self):
        """Polls the blockchain to check if the data is available."""

        if self._blockchain.containsTransaction(self._transaction):
            return True

        else:
            return False


class Storage(Thread):

    def __init__(self, src_ip, src_port, src_service, network, bootstrap, difficulty, private_key=None,
                 modify_topology=True):
        global PRIVATE_KEY_FILE
        """Allocate the backend storage of the high level API, i.e.,
        your blockchain. Depending whether or not the miner flag has
        been specified, you should allocate the mining process.
        """
        Thread.__init__(self)

        self._src_ip = src_ip

        os.system('clear')

        self._boostrap = list()

        for ip in bootstrap:
            self._boostrap.append((ip, 8000, Protocol.Protocol_Constant.NODE_NETWORK, time.time()))

        self._blockchain_manager = Blockchain_Manager.Blockchain_Manager(difficulty, private_key, False, True)

        self._network_manager = Monitor_Network_Manager.Monitor_Network_Manager(src_ip, src_port, src_service, network,
                                                                                self._boostrap,
                                                                                self._blockchain_manager, True,
                                                                                grow_peer_number=modify_topology)

        self.__stop_event = Event()

    def run(self):
        self.display_info("Peer is running...", 0)

        self._network_manager.start()

        # Connection to the boostrap nodes.
        self._network_manager.display_info("Connecting to the boostrap nodes.", 6)

        for node_ip, node_port, node_service, node_timestamp in self._boostrap.copy():
            self._network_manager.connect(node_ip, node_port, node_service, node_timestamp)

        while not self.__stop_event.is_set() and self._network_manager.is_alive():
            peers = self._network_manager.get_connected_peers()
            topology_information = self._network_manager.get_topology_monitoring_information()

            completed_broadcast_information = self.get_complete_broadcast_information(peers, topology_information)

        traceback_list = self._network_manager.get_tracebacks()

        for ex_type, ex, tb in traceback_list:
            traceback.print_exception(ex_type, ex, tb)

    def compute_minimum_spanning_trees(self, completed_broadcast_information):
        for info, peer_infos in completed_broadcast_information.items():
            origin, min_sent_time = self.compute_origin(peer_infos)

    def compute_origin(self, peer_infos):
        origin = None
        curr_min_sent_time = math.inf

        for ip, timestamp in peer_infos.items():
            sent_time = datetime.datetime.fromtimestamp(timestamp)

            if sent_time < curr_min_sent_time:
                origin = ip
                curr_min_sent_time = sent_time

        return origin, curr_min_sent_time

    def get_complete_broadcast_information(self, peers, topology_information):
        tmp = set(peers.copy())

        complete_broadcast_information = dict()

        for info, peer_info in topology_information.items():
            curr_peers = set(peer_info.keys())

            if len(tmp.difference(curr_peers)) == 0:
                complete_broadcast_information[info] = peer_info

        return complete_broadcast_information

    def kill(self):
        self.__stop_event.set()

        self._blockchain_manager.stop_mining()

        self._network_manager.kill()

    def is_alive(self) -> bool:
        return not self.__stop_event.is_set() and self._network_manager.is_alive()

    def join(self, **kwargs):
        self.__stop_event.set()

        Thread.join(self)

    def display_info(self, text, x):
        print_there(x, 0, text)

    def error_recording(self):
        directory = "Log/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        directory = "Log/Log_Peer_" + self._src_ip + "/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        stdout = open(("Log/Log_Peer_" + self._src_ip + "/Storage.txt"), "a")

        ex_type, ex, tb = sys.exc_info()
        traceback.print_exception(ex_type, ex, tb, file=stdout)
        stdout.write('\n\n')

        stdout.close()
