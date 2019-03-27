"""
KeyChain key-value store (stub).

NB: Feel free to extend or modify.
"""
import time
from threading import Thread, Event

from .Blockchain import *
from .Network import *
from .Util import *

PRIVATE_KEY_FILE = "private_key.pem"


class Callback:
    def __init__(self, transaction, blockchain):
        self._transaction = transaction
        self._blockchain = blockchain

    def wait(self):
        """Wait until the transaction appears in the blockchain."""

        while True:
            blockchain = list(self._blockchain.getBlocks())

            for block in blockchain:
                if block.contains(self._transaction) is True:
                    return

    def completed(self):
        """Polls the blockchain to check if the data is available."""

        blockchain = list(self._blockchain.getBlocks())

        for block in blockchain:
            if block.contains(self._transaction) is True:
                return True

        return False


class Storage(Thread):
    def __init__(self, src_ip, src_port, src_service, network, bootstrap, miner, start_difficulty, private_key=None):
        global PRIVATE_KEY_FILE
        """Allocate the backend storage of the high level API, i.e.,
        your blockchain. Depending whether or not the miner flag has
        been specified, you should allocate the mining process.
        """
        Thread.__init__(self)

        if private_key is None:
            self._private_key = get_private_key(PRIVATE_KEY_FILE)
        else:
            self._private_key = private_key

        self._blockchain_manager = Blockchain_Manager(start_difficulty, private_key, miner)

        self._network_manager = Network_Manager(src_ip, src_port, src_service, network, bootstrap)

        self._mine = miner

        self.__stop_event = Event()

    def run(self):
        self._network_manager.start()

        while not self.__stop_event.isSet():
            if self._mine is True:
                self.mine()

        self._network_manager.join()

    def kill(self):
        self.__stop_event.set()

    def join(self, **kwargs):
        self.__stop_event.set()

        Thread.join(self)

    def put(self, key, value, block=True):
        """Puts the specified key and value on the Blockchain.

        The block flag indicates whether the call should block until the value
        has been put onto the blockchain, or if an error occurred.

        """
        transaction = Transaction(key, value, self._private_key.public_key(), time.time())

        transaction.sign(self._private_key)

        self._blockchain_manager.add_transaction(transaction)

        self._network_manager.broadcast_transactions([transaction])

        callback = Callback(transaction, self._blockchain_manager.getBlockchain())

        if block:
            callback.wait()

        return callback

    def retrieve(self, key):
        """Searches the most recent value of the specified key.

        -> Search the list of blocks in reverse order for the specified key,
        or implement some indexing schemes if you would like to do something
        more efficient.
        """
        blockchain = list(self._blockchain_manager.getBlockchain().getBlocks())
        for block in blockchain:
            transactions = block.getTransactions()

            for transaction in transactions:

                if key == transaction.getKey():
                    return transaction.getValue()

    def retrieve_all(self, key):
        """Retrieves all values associated with the specified key on the
        complete blockchain.
        """
        values = list()

        blockchain = list(self._blockchain_manager.getBlockchain().getBlocks())
        for block in blockchain:
            transactions = block.getTransactions()

            for transaction in transactions:

                if key == transaction.getKey():
                    values.append(transaction.getValue())

        return values

    def mine(self):
        ret, block = self._blockchain_manager.mine()

        if ret == "mined":
            self._network_manager.broadcast_blocks([block])


