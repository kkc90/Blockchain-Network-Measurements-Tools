import time
import hashlib

from .BlockChainException import *


class Block:
    def __init__(self, index, prev_block_hash, transaction_list, difficulty, hash=None, timestamp=None, nonce=None):
        """Describe the properties of a block."""
        self._index = index
        self._prev_block_hash = prev_block_hash

        self._hash = hash

        if timestamp is not None:
            self._timestamp = int(timestamp)
        else:
            self._timestamp = int(time.time())

        self._nonce = nonce

        if len(transaction_list) > 0 or index == 0:
            self._transaction_list = transaction_list
            self._transaction_hashes = [transaction.__hash__() for transaction in transaction_list]
        else:
            raise ZeroTransactionBlockException("Block initialized with no transactions")

        self._difficulty = int(difficulty)

    def isMined(self):
        return self._nonce is not None

    def getIndex(self):
        return self._index

    def getPrevBlockHash(self):
        return self._prev_block_hash

    def getTimestamp(self):
        return self._timestamp

    def getMerkleRoot(self):
        # NOT IMPLEMENTED YET
        if self._hash is None:
            raise UnminedBlockException("Error: The block considered has not been mined yet.")
        else:
            return self._hash

    def getDifficulty(self):
        return self._difficulty

    def computeHash(self):
        hasher = hashlib.sha256()
        hasher.update(repr(self._prev_block_hash).encode("utf-8"))
        hasher.update(repr(self._transaction_hashes).encode("utf-8"))
        hasher.update(repr(self._timestamp).encode("utf-8"))
        hasher.update(repr(self._difficulty).encode("utf-8"))

        if self._nonce is None:
            raise UnminedBlockException("The block considered has not been mined yet.")
        else:
            hasher.update(repr(self._nonce).encode("utf-8"))

        return int(hasher.hexdigest(), 16)

    def getBlockHash(self):
        if self._hash is None:
            raise UnminedBlockException("The block considered has not been mined yet.")

        return self._hash

    def setBlockHash(self, hash):
        self._hash = hash

    def setBlockNonce(self, nonce):
        self._nonce = nonce;

    def getBlockNonce(self):
        return self._nonce

    def proof(self, nonce):
        """Return the proof of the current block."""
        hasher = hashlib.sha256()

        hasher.update(repr(self._prev_block_hash).encode("utf-8"))
        hasher.update(repr(self._transaction_hashes).encode("utf-8"))
        hasher.update(repr(self._timestamp).encode("utf-8"))
        hasher.update(repr(self._difficulty).encode("utf-8"))
        hasher.update(repr(nonce).encode("utf-8"))

        return int(hasher.hexdigest(), 16)

    def getTransactions(self):
        """Returns the list of transactions associated with this block."""
        return self._transaction_list

    def getTransactionsHashes(self):
        """Returns the list of transactions hashesassociated with this block."""
        return self._transaction_hashes

    def contains(self, transaction):
        if transaction in self._transaction_list:
            return True

        else:
            return False

    def containsHash(self, transaction_hash):
        if transaction_hash in self._transaction_hashes:
            return True

        else:
            return False

    def __hash__(self):
        hasher = hashlib.sha256()
        hasher.update(repr(self._prev_block_hash).encode("utf-8"))
        hasher.update(repr(self._transaction_hashes).encode("utf-8"))
        hasher.update(repr(self._timestamp).encode("utf-8"))
        hasher.update(repr(self._difficulty).encode("utf-8"))

        if self._nonce is None:
            raise UnminedBlockException("Error: The block considered has not been mined yet.")
        else:
            hasher.update(repr(self._nonce).encode("utf-8"))

        return int(hasher.hexdigest(), 16)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __str__(self):
        string = "Block " + str(self._index) + " : \n"

        for transaction in self._transaction_list:
            string += "\t\t" + str(transaction) + "\n"

        return string

    def __gt__(self, other):
        return self._index > other.getIndex()
