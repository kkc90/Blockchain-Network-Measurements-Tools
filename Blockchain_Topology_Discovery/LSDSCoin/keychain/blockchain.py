import hashlib
import time
import math
from random import randint
import datetime

from keychain.BlockChainException import *

"""
Blockchain (stub).

NB: Feel free to extend or modify.
"""

DIFFICULTY_INCREASE = 0
GENESIS_PREV_HASH = bytes(0)
NB_BLOCK_BEFORE_DIFFICULTY_UPDATE = 10
MINING_TIME = datetime.timedelta(0, 1, 0)  # Mining NB_BLOCK_BEFORE_DIFFICULTY_UPDATE blocks should take around 10 minutes --> otherwise update of the difficulty
MAX_NB_TRANSACTION = 10


class Block:
    def __init__(self, index, prev_block_hash, transaction_list, timestamp=time.time(), nonce=None):
        """Describe the properties of a block."""
        self._index = index
        self._prev_block_hash = prev_block_hash
        self._timestamp = timestamp
        self._nonce = nonce

        if len(transaction_list) > 0 or index == 0:
            self._transaction_list = transaction_list
        else:
            raise ZeroTransactionBlockException("Error: Block initialized with no transactions");

    def getTransactions(self):
        return self._transaction_list

    def getIndex(self):
        return self._index

    def getPrevBlockHash(self):
        return self._prev_block_hash

    def getTimestamp(self):
        return self._timestamp

    def getBlockHash(self):
        hasher = hashlib.sha256()
        hasher.update(repr(self._prev_block_hash).encode("utf-8"))
        hasher.update(repr(self._transaction_list).encode("utf-8"))
        hasher.update(repr(self._timestamp).encode("utf-8"))

        if (self._nonce is None):
            raise UnminedBlockException("Error: The block considered has not been mined yet.")
        else:
            hasher.update(repr(self._nonce).encode("utf-8"))

        return hasher.digest()

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


class Transaction:
    def __init__(self, key, value, origin):
        """A transaction, in our KV setting. A transaction typically involves
        some key, value and an origin (the one who put it onto the storage).
        """
        self._key = key
        self._value = value
        self._origin = origin

    def getValue(self):
        return self._value

    def getOrigin(self):
        return self._origin

    def getKey(self):
        return self._key

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._value == other.getValue() and self._key == other.getKey() and self._origin == other.getOrigin()
        else:
            return False


class Blockchain:

    def __init__(self, difficulty):
        """The bootstrap address serves as the initial entry point of
        the bootstrapping procedure. In principle it will contact the specified
        addres, download the peerlist, and start the bootstrapping procedure.
        """
        # Initialize the properties.
        self._blocks = []
        self._fork = []
        self._peers = []
        self._difficulty = difficulty
        self._transaction_pool = []

        # Initialize the chain with the Genesis block.
        self._add_genesis_block()

    def getBlock(self, index):
        return self._blocks[index]

    def getBlocks(self):
        return self._blocks

    def getTransactionPool(self):
        return self._transaction_pool

    def getNbTransactions(self):
        return len(self._transaction_pool)

    def hasForked(self):
        return len(self._fork) > 0


    def add_block(self, block):

        last_block = self._blocks[-1]

        # -------------- Basic case ------------ #
        if (not self.hasForked() and block.getIndex() == last_block.getIndex() + 1 and block.getPrevBlockHash() == last_block.getBlockHash()
                and self.is_hash_valid(block.getBlockHash(), self.getDifficulty())):
            self._blocks.append(block)

            for i in block.getTransactions():
                if (i in self._transaction_pool):
                    self._transaction_pool.remove(i)

            ret = "ok"

        # -------------- Case in which the Blockchain you have is not correct anymore ---------- #
        elif (block.getIndex() > last_block.getIndex() + 2):
            # You will ask your neighbours for the good blockchain #
            ret = "not implemented"

        # -------------- Consensus is needed ------------- #
        elif (self.hasForked() or block.getIndex() == last_block.getIndex()):
            ret = self.consensus(block)

        else:
            ret = "invalid block"

        self.updateDifficulty()

        return ret

    def consensus(self, block):
        global NB_BLOCK_BEFORE_DIFFICULTY_UPDATE

        last_block = self._blocks[-1]

        # -------- Consider the case in which a consensus must be done (two blockchains alive with one blocks forked) ------- #
        if (len(self._fork) == 0 and block.getIndex() == last_block.getIndex()):
            # The block being considered has the same index has the last block you have in the blockchain --> Which one is in the valid blockchain ?
            # You will store it in case it's the valid one.
            if (len(self._blocks) > 2):
                prev_last_block = self._blocks[-2]

                # Check if the block is based on the good blockchain
                if (block.getPrevBlockHash() == prev_last_block.getBlockHash()):
                    difficulty = self.getDifficulty()

                    # Check if Difficulty has changed while fork #
                    if (block.getIndex() % NB_BLOCK_BEFORE_DIFFICULTY_UPDATE == 0):
                        prev_last_block = self._blocks[NB_BLOCK_BEFORE_DIFFICULTY_UPDATE]
                        a = datetime.datetime.fromtimestamp(block.getTimestamp())
                        b = datetime.datetime.fromtimestamp(prev_last_block.getTimestamp())
                        time_taken = a - b
                        # Difficulty has been updated #
                        if (time_taken != MINING_TIME):
                            difficulty = difficulty * (NB_BLOCK_BEFORE_DIFFICULTY_UPDATE * MINING_TIME) / time_taken

                    # Check if the block is valid #
                    if (self.is_hash_valid(block.getBlockHash(), difficulty)):
                        self._fork.append((block, difficulty))
                        ret = "1 block fork"
                    else:
                        # Invalid block
                        ret = "invalid block"
                else:
                    # Invalid block
                    ret = "invalid block"
            else:
                # Check if the block is valid #
                if (self.is_hash_valid(block.getBlockHash(), self._difficulty)):
                    self._fork.append((block, self._difficulty))
                    ret = "1 block fork"
                else:
                    # Invalid block
                    ret = "invalid block"

        # ------- Consider the intermediary state when consensus need one more block to decide if you have the good blockchain ------- #
        elif (len(self._fork) > 0 and block.getIndex() == self._fork[-1][
            0].getIndex() + 1 and block.getPrevBlockHash() == last_block.getBlockHash()):
            if (self.is_hash_valid(block.getBlockHash(), self.getDifficulty())):
                self._blocks.append(block)

                for i in block.getTransactions():
                    if (i in self._transaction_pool):
                        self._transaction_pool.remove(i)

                ret = "consensus being done"
            else:
                ret = "invalid block"

        # ------- Consider the intermediary state when consensus need one more block to decide if they have the good blockchain ------- #
        elif (len(self._fork) > 0 and block.getIndex() == last_block.getIndex() + 1 and block.getPrevBlockHash() ==
              self._fork[-1][0].getBlockHash()):
            difficulty = self.getDifficulty()

            # Check if Difficulty has changed while fork #
            if (block.getIndex() % NB_BLOCK_BEFORE_DIFFICULTY_UPDATE == 0):
                prev_last_block = self._blocks[NB_BLOCK_BEFORE_DIFFICULTY_UPDATE]
                a = datetime.datetime.fromtimestamp(block.getTimestamp())
                b = datetime.datetime.fromtimestamp(prev_last_block.getTimestamp())
                time_taken = a - b
                # Difficulty has been updated #
                if (time_taken != MINING_TIME):
                    difficulty = difficulty * (NB_BLOCK_BEFORE_DIFFICULTY_UPDATE * MINING_TIME) / time_taken

            # Check if the block is valid #
            if (self.is_hash_valid(block.getBlockHash(), difficulty)):
                self._fork.append((block, difficulty))
                ret = "consensus being done"
            else:
                # Invalid block
                ret = "invalid block1"

        # -------- Consider the case in which a consensus must be done (two blockchains alive but with several blocks forked) ------ #
        elif (len(self._fork) > 0 and block.getIndex() == last_block.getIndex()
              and block.getPrevBlockHash() == self._fork[-1][0].getBlockHash()):
            difficulty = self._fork[-1][1]
            # ---- Check if Difficulty has changed while fork -----#
            if (block.getIndex() % NB_BLOCK_BEFORE_DIFFICULTY_UPDATE == 0):

                if (NB_BLOCK_BEFORE_DIFFICULTY_UPDATE > len(self._fork)):
                    prev_last_block = self._blocks[- NB_BLOCK_BEFORE_DIFFICULTY_UPDATE + len(self._fork)]
                else:
                    prev_last_block = self._fork[- NB_BLOCK_BEFORE_DIFFICULTY_UPDATE]

                a = datetime.datetime.fromtimestamp(block.getTimestamp())
                b = datetime.datetime.fromtimestamp(prev_last_block.getTimestamp())
                time_taken = a - b

                # Difficulty has been updated #
                if (time_taken != MINING_TIME):
                    difficulty = difficulty * (NB_BLOCK_BEFORE_DIFFICULTY_UPDATE * MINING_TIME) / time_taken

            if (self.is_hash_valid(block.getBlockHash(), difficulty)):
                self._fork.append((block, difficulty))
                ret = "n block fork"
            else:
                # Invalid block
                ret = "invalid block"

        # -------- Consider the case in which a consensus has been done and you don't have the correct blockchain ------- #
        elif (len(self._fork) > 0 and block.getIndex() == last_block.getIndex() + 2 and block.getPrevBlockHash() ==
              self._fork[-1][0].getBlockHash()):
            difficulty = self._fork[-1][1]
            if (block.getIndex() == self._fork[-1][0].getIndex() + 1 and block.getPrevBlockHash() == self._fork[-1][
                0].getBlockHash() and self.is_hash_valid(block.getBlockHash(), difficulty)):
                for i in self._fork:
                    # Replace the blocks that are wrong in the blockchain
                    if (i[0].getIndex() < len(self._blocks)):
                        # Put back the transaction of the "wrong" blockchain in the transaction pool
                        for j in self._blocks[i[0].getIndex()].getTransactions():
                            self._transaction_pool.append(j)

                        self._blocks[i[0].getIndex()] = i[0]

                        # Remove the transaction that are currently in the blockchain
                        for j in self._blocks[i[0].getIndex()].getTransactions():
                            if (j in self._transaction_pool):
                                self._transaction_pool.remove(j)


                    # Add the additionnal block of the real blockchain
                    else:
                        self._blocks.append(i[0])

                        # Remove the transaction that are currently in the blockchain
                        for j in i[0].getTransactions():
                            if (j in self._transaction_pool):
                                self._transaction_pool.remove(j)

                self._blocks.append(block)

                # Remove the transaction that are currently in the blockchain
                for j in block.getTransactions():
                    if (j in self._transaction_pool):
                        self._transaction_pool.remove(j)

                self._fork = []

                ret = "consensus done"
            else:
                # Invalid block
                ret = "invalid block"

        # -------- Consider the case in which a consensus has been done and you have the correct blockchain ------- #
        elif (len(self._fork) > 0 and block.getIndex() == self._fork[-1][
            0].getIndex() + 2 and block.getPrevBlockHash() == last_block.getBlockHash()):
            self._blocks.append(block)

            for i in block.getTransactions():
                if (i in self._transaction_pool):
                    self._transaction_pool.remove(i)

            self._fork = []

            ret = "consensus done"

        else:
            # Invalid block
            ret = "invalid block"

        return ret

    def get_last_hash(self):
        return self._blocks[-1].getBlockHash()

    def length(self):
        return self._blocks[-1].getIndex() + 1

    def _add_genesis_block(self):
        """Adds the genesis block to your blockchain."""
        index = 0
        prev_block_hash = GENESIS_PREV_HASH
        transaction_list = []
        genesis_block = Block(index, prev_block_hash, transaction_list)
        self.proof_of_work(genesis_block)

        self._blocks.append(genesis_block)

    def getDifficulty(self):
        """Returns the difficulty level."""
        return self._difficulty

    def add_transaction(self, transaction):
        """Adds a transaction to your current list of transactions,
        and broadcasts it to your Blockchain network.

        If the `mine` method is called, it will collect the current list
        of transactions, and attempt to mine a block with those.
        """
        self._transaction_pool.append(transaction)

    def is_hash_valid(self, hash, difficulty):
        global DIFFICULTY_INCREASE

        return int.from_bytes(hash, byteorder="little") < math.pow(2, 256 - difficulty * DIFFICULTY_INCREASE)

    def proof_of_work(self, block):
        nonce_list = list()

        curr_nonce = randint(0, int(math.pow(2, 32)))
        block.setBlockNonce(curr_nonce)

        hash = block.getBlockHash()

        while not self.is_hash_valid(hash, self.getDifficulty()):
            if (block.getIndex() != self._blocks[-1].getIndex() + 1):
                return "not mined"

            nonce_list.append(curr_nonce)
            while (True):
                curr_nonce = randint(0, int(math.pow(2, 32)))
                if (curr_nonce not in nonce_list):
                    break
            block.setBlockNonce(curr_nonce)
            hash = block.getBlockHash()

        return "mined"

    def updateDifficulty(self):
        global NB_BLOCK_BEFORE_DIFFICULTY_UPDATE
        global MINING_TIME

        last_block = self._blocks[-1]

        if (last_block.getIndex() > 0 and last_block.getIndex() % NB_BLOCK_BEFORE_DIFFICULTY_UPDATE == 0):
            prev_last_block = self._blocks[-NB_BLOCK_BEFORE_DIFFICULTY_UPDATE]
            a = datetime.datetime.fromtimestamp(last_block.getTimestamp())
            b = datetime.datetime.fromtimestamp(prev_last_block.getTimestamp())

            time_taken = a - b
            print(time_taken)

            if (time_taken != MINING_TIME):
                self._difficulty = self._difficulty * (NB_BLOCK_BEFORE_DIFFICULTY_UPDATE * MINING_TIME) / time_taken

    def mine(self):
        global MAX_NB_TRANSACTION

        """Implements the mining procedure."""
        if not self._transaction_pool:
            return "empty transaction pool"

        last_block = self._blocks[-1]

        transaction_list = list()
        i = 0
        while (len(transaction_list) < MAX_NB_TRANSACTION and len(self._transaction_pool) > 0):
            transaction_list.append(self._transaction_pool[i])
            i = i + 1

        block = Block(index=last_block.getIndex() + 1, prev_block_hash=last_block.getBlockHash(),
                      transaction_list=transaction_list)

        ret = self.proof_of_work(block)

        if (ret == "mined"):
            ret = self.add_block(block)
        return ret

    def mineBlock(self, block):

        ret = self.proof_of_work(block)
        if (ret == "mined"):
            ret = "ok"
        else:
            ret = "not mined"

        return ret

    def is_valid(self):
        global GENESIS_PREV_HASH
        """Checks if the current state of the blockchain is valid.

        Meaning, are the sequence of hashes, and the proofs of the
        blocks correct?
        """
        previous_hash = GENESIS_PREV_HASH
        for block in self._blocks:
            hash = block.getBlockHash()
            if block.getPrevBlockHash() != previous_hash:
                return False

            previous_hash = hash

        return True
