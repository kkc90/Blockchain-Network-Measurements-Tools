"""
KeyChain key-value store (stub).

NB: Feel free to extend or modify.
"""
import shutil
import sys
import time
import traceback
from threading import Thread, Event
import numpy as np

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

    def __init__(self, src_ip, src_port, src_service, network, bootstrap, miner, difficulty, monitor=False,
                 private_key=None, time_before_transaction_distribution=None, modify_topology=True):
        global PRIVATE_KEY_FILE
        """Allocate the backend storage of the high level API, i.e.,
        your blockchain. Depending whether or not the miner flag has
        been specified, you should allocate the mining process.
        """
        Thread.__init__(self)

        self._src_ip = src_ip

        self._mine = miner

        self._monitor = monitor

        self._time_before_transaction_distribution = time_before_transaction_distribution

        if private_key is None:
            self._private_key = get_private_key(PRIVATE_KEY_FILE)
        else:
            self._private_key = private_key

        if monitor is True:
            os.system('clear')

        self._boostrap = list()

        for ip in bootstrap:
            self._boostrap.append((ip, 8000, Protocol.Protocol_Constant.NODE_NETWORK, time.time()))

        self._blockchain_manager = Blockchain_Manager.Blockchain_Manager(difficulty, private_key, miner, monitor)

        self._network_manager = Network_Manager.Network_Manager(src_ip, src_port, src_service, network, self._boostrap,
                                                                self._blockchain_manager, monitor,
                                                                grow_peer_number=modify_topology)

        self.__stop_event = Event()

    def run(self):
        if self._monitor is True:
            self.display_info("Peer is running...", 0)

        self._network_manager.start()

        # Connection to the boostrap nodes.
        if self._monitor is True:
            self._network_manager.display_info("Connecting to the boostrap nodes.", 6)

        for node_ip, node_port, node_service, node_timestamp in self._boostrap.copy():
            self._network_manager.connect(node_ip, node_port, node_service, node_timestamp)

        self._network_manager.get_blockchain()

        self._network_manager.get_transaction_pool()

        start1 = time.time()
        start2 = time.time()
        time_before_transaction = None

        if self._time_before_transaction_distribution is not None:
            time_before_transaction = np.random.normal(self._time_before_transaction_distribution[0],
                                                          self._time_before_transaction_distribution[1])

        while not self.__stop_event.isSet() and self._network_manager.is_alive():

            if self._time_before_transaction_distribution is not None:
                if (time.time() - start1) > time_before_transaction:
                    self.put(("key" + str(time.time())), ("value" + str(time.time())), False)

                    time_before_transaction = np.random.normal(self._time_before_transaction_distribution[0],
                                                                  self._time_before_transaction_distribution[1])
                    start1 = time.time()

            if self._mine is True:
                ret1 = self.mine()

                if ret1 == 'not enough transaction in pool' and (time.time() - start2) > 10:
                    self._network_manager.get_transaction_pool()

                    start2 = time.time()

        self._blockchain_manager.stop_mining()

        self._network_manager.join()

        traceback_list = self._network_manager.get_tracebacks()

        for ex_type, ex, tb in traceback_list:
            traceback.print_exception(ex_type, ex, tb)

    def kill(self):
        self.__stop_event.set()

        self._blockchain_manager.stop_mining()

        self._network_manager.kill()

    def is_alive(self) -> bool:
        return not self.__stop_event.is_set() and self._network_manager.is_alive()

    def join(self, **kwargs):
        self.__stop_event.set()

        Thread.join(self)

    def put(self, key, value, block=True):
        """
            Puts the specified key and value on the Blockchain.

        The block flag indicates whether the call should block until the value
        has been put onto the blockchain, or if an error occurred.

        """

        try:

            if self._monitor is True:
                self.display_info("Pushing Transaction (" + str(key) + "," + str(value) + ") to the network ...", 1)

            transaction = Transaction.Transaction(key, value, self._private_key.public_key(), time.time())

            transaction.sign(self._private_key)

            self._network_manager.broadcast_transactions([transaction])

            self._blockchain_manager.add_transaction(transaction)

            if self._monitor is True:
                self._blockchain_manager.log_transaction_pool(self._src_ip)

            callback = Callback(transaction, self._blockchain_manager.getBlockchain())

            if block is True:
                callback.wait()

                if self._monitor is True:
                    self.display_info("Transaction Pushed ...", 1)

            return callback

        except Exception as err:
            self.display_info(("Unexpected Failure - " + str(err)), 1)
            traceback.print_exc()
            self.error_recording()

    def retrieve(self, key):
        """Searches the most recent value of the specified key.

        -> Search the list of blocks in reverse order for the specified key,
        or implement some indexing schemes if you would like to do something
        more efficient.
        """

        try:

            if self._monitor is True:
                self.display_info(("Retrieving " + key + " ..."), 1)

            blockchain = list(self._blockchain_manager.getBlockchain().getBlocks())
            for block in blockchain:
                transactions = block.getTransactions()

                for transaction in transactions:

                    if key == transaction.get_key():
                        if self._monitor is True:
                            self.display_info((key + " has been retreived : " + str(transaction.get_value()) + " ..."),
                                              1)

                        return transaction.get_value()

        except Exception as err:
            self.display_info(("Unexpected Failure - " + str(err)), 1)
            traceback.print_exc()
            self.error_recording()

    def retrieve_all(self, key):
        """Retrieves all values associated with the specified key on the
        complete blockchain.
        """

        if self._monitor is True:
            self.display_info(("Retrieving all " + key + " ..."), 1)
        try:
            values = list()

            blockchain = list(self._blockchain_manager.getBlockchain().getBlocks())
            for block in blockchain:
                transactions = block.getTransactions()

                for transaction in transactions:

                    if key == transaction.get_key():
                        values.append(transaction.get_value())

            if self._monitor is True:
                self.display_info(1, ("All " + key + " has been retreived : " + str(values) + " ..."))

            return values

        except Exception as err:
            self.display_info(("Unexpected Failure - " + str(err)), 1)
            traceback.print_exc()
            self.error_recording()

    def mine(self):
        try:
            if self._monitor is True:
                self.display_info("Mining ...", 0)

            ret1, ret2, block = self._blockchain_manager.mine()

            if ret1 == "mined":
                if self._monitor is True:
                    self._blockchain_manager.log_blockchain(self._src_ip)
                    self.display_info("Broadcast Mined Block ...", 0)

                self._network_manager.broadcast_blocks([block])

            return ret1

        except Exception as err:
            self.display_info(("Unexpected Failure - " + str(err)), 1)
            traceback.print_exc()
            self.error_recording()

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
