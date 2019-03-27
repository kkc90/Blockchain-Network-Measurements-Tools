import time


class Block:
    def __init__(self, index, prev_block_hash, transaction_list, timestamp=None, nonce=None):
        """Describe the properties of a block."""
        self._index = index
        self._prev_block_hash = prev_block_hash

        self._hash = None

        if timestamp is not None:
            self._timestamp = timestamp
        else:
            self._timestamp = time.time()

        self._nonce = nonce

        if len(transaction_list) > 0 or index == 0:
            self._transaction_list = set(transaction_list)
        else:
            raise ZeroTransactionBlockException("Block initialized with no transactions")

    def getIndex(self):
        return self._index

    def getPrevBlockHash(self):
        return self._prev_block_hash

    def getTimestamp(self):
        return self._timestamp

    def computeHash(self):
        hasher = hashlib.sha256()
        hasher.update(repr(self._prev_block_hash).encode("utf-8"))
        hasher.update(repr(self._transaction_list).encode("utf-8"))
        hasher.update(repr(self._timestamp).encode("utf-8"))

        if self._nonce is None:
            raise UnminedBlockException("The block considered has not been mined yet.")
        else:
            hasher.update(repr(self._nonce).encode("utf-8"))

        return hasher.digest()

    def getBlockHash(self):
        if self._hash is None:
            raise UnminedBlockException("The block considered has not been mined yet.")

        return self._hash

    def setBlockHash(self, hash):
        self._hash = hash

    def setBlockNonce(self, nonce):
        self._nonce = nonce;

    def proof(self, nonce):
        """Return the proof of the current block."""
        hasher = hashlib.sha256()
        hasher.update(self._prev_block_hash)
        hasher.update(repr(self._transaction_list).encode("utf-8"))
        hasher.update(repr(self._timestamp).encode("utf-8"))
        hasher.update(repr(nonce).encode("utf-8"))

        return hasher.digest()

    def getTransactions(self):
        """Returns the list of transactions associated with this block."""
        return self._transaction_list

    def contains(self, transaction):
        if transaction in self._transaction_list:
            return

    def __hash__(self):
        hasher = hashlib.sha256()
        hasher.update(repr(self._prev_block_hash).encode("utf-8"))
        hasher.update(repr(self._transaction_list).encode("utf-8"))
        hasher.update(repr(self._timestamp).encode("utf-8"))

        if (self._nonce is None):
            raise UnminedBlockException("Error: The block considered has not been mined yet.")
        else:
            hasher.update(repr(self._nonce).encode("utf-8"))

        return int(hasher.hexdigest(), 16)
