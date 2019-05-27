import random
import shutil
import sys
import os


import math

from .Block import *
from .Blockchain import *
from .Blockchain_Constant import *
from .Transaction_Pool import *
from threading import Event


COLUMNS, ROWS = shutil.get_terminal_size(fallback=(80, 24))


def print_there(x, y, text):
    global COLUMNS, ROWS
    empty_line = ""
    for i in range(0, COLUMNS):
        empty_line += " "

    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x + 1, 0, empty_line))
    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x + 1, y + 1, text))
    sys.stdout.flush()


class Blockchain_Manager():
    def __init__(self, difficulty, private_key, mine=False, monitor=False):

        self._difficulty = difficulty

        self._monitor = monitor

        self._transaction_pool = Transaction_Pool()

        self._blockchain = Blockchain()

        if self._monitor is True:
            self.display_info("Blockchain Manager is starting ...", 3)

            self.display_info(("Blockchain contains " + str(self._blockchain.length())
                               + " blocks and Transaction Pool contains "
                               + str(self._transaction_pool.getNbTransactions())), 4)

        self._add_genesis_block()

        self._forked_blockchain = list()

        self._private_key = private_key

        self._mine = mine

        self.__stop_event = Event()

    def add_transaction(self, transaction):
        if self._monitor is True:
            self.display_info(("Adding Transaction to (" + str(transaction.getKey()) + str(transaction.getValue())
                               + ") transaction pool..."), 3)

        self._transaction_pool.add_transaction(transaction)

        if self._monitor is True:
            self.display_info(("Blockchain contains " + str(self._blockchain.length())
                               + " blocks and Transaction Pool contains "
                               + str(self._transaction_pool.getNbTransactions())), 4)

    def getBlockchain(self):
        return self._blockchain

    def getTransactionPool(self):
        return self._transaction_pool

    def getDifficulty(self):
        return self._difficulty

    def getLastHash(self):
        return self._blockchain.get_last_hash()

    def hasForked(self):
        return len(self._forked_blockchain) > 0

    def getPublicKey(self):
        return self._private_key.public_key()

    def _add_genesis_block(self):
        """Adds the genesis block to your blockchain."""

        if self._monitor is True:
            self.display_info("Genesis Block is added to the Blockchain ...", 3)

            self.display_info(("Blockchain contains " + str(self._blockchain.length())
                               + " blocks and Transaction Pool contains "
                               + str(self._transaction_pool.getNbTransactions())), 4)

        index = 0
        prev_block_hash = Blockchain_Constant.GENESIS_PREV_HASH
        transaction_list = []
        genesis_block = Block(index, prev_block_hash, transaction_list, self._difficulty, timestamp=0.0)

        genesis_block.setBlockNonce(5)

        hash = genesis_block.computeHash()

        genesis_block.setBlockHash(hash)

        self._blockchain.addBlock(genesis_block)

        if self._monitor is True:
            self.display_info("Genesis Block added.", 3)

            self.display_info(("Blockchain contains " + str(self._blockchain.length())
                               + " blocks and Transaction Pool contains "
                               + str(self._transaction_pool.getNbTransactions())), 4)

    def add_block(self, block):
        if self._monitor is True:
            self.display_info("A Block being added to the Blockchain ...", 3)

        last_block = self._blockchain.getLastBlock()

        hash = block.getBlockHash()

        if block.computeHash() != hash:
            if self._monitor is True:
                self.display_info("Invalid Block (Computed Hash != Block Hash)", 3)

            ret = "invalid block hash"

        elif (not self.hasForked() and block.getIndex() > last_block.getIndex() + 1) \
                or (self.hasForked() and block.getIndex() > self._forked_blockchain[-1].getIndex() + 1
                    and block.getIndex() > last_block.getIndex() + 1):

            ret = "invalid block index"

        elif block.getDifficulty() != self._difficulty or not self.is_proof_of_work_valid(block):
            if self._monitor is True:
                self.display_info("Invalid Block (Proof of work is not valid)", 3)

            ret = "invalid proof of work"

            # ---------------------------------- Basic case ------------------------------- #
            #                                                                               #
            #   1. No fork has been detected previously                                     #
            #   2. The block is valid with respect to the current blockchain                #
            #   3. The block has a correct proof of work                                    #
            #                                                                               #
            # ----------------------------------------------------------------------False------- #
        elif not self.hasForked() and block.getIndex() == last_block.getIndex() + 1 \
                and block.getPrevBlockHash() == last_block.getBlockHash():
            if self._monitor is True:
                self.display_info("Block is added.", 3)

            self._blockchain.addBlock(block)

            for i in block.getTransactions():
                self._transaction_pool.removeTransaction(i)

            ret = "ok"

        elif block.getIndex() == last_block.getIndex() and block.getBlockHash() == last_block.getBlockHash():
            ret = "already added"

            # -------------- Consensus is needed ------------- #
        elif self.hasForked() or block.getIndex() == last_block.getIndex():
            ret = self.consensus(block)

        else:
            ret = "invalid block"

        self.updateDifficulty()

        if self._monitor is True:
            self.display_info(("Blockchain contains " + str(self._blockchain.length())
                               + " blocks and Transaction Pool contains "
                               + str(self._transaction_pool.getNbTransactions())), 4)

        if self._monitor is True:
            self.display_info("Block " + str(block.getIndex()) + " added with (return = " + ret + ").", 3)

        return ret

    def consensus(self, block):

        last_block = self._blockchain.getLastBlock()
        prev_last_block = self._blockchain.getPrevLastBlock()

        # -------------------- Consider the case in which a consensus must be done --------------------- #
        # -------------------------- (two blockchains alive with one blocks forked --------------------- #
        if not self.hasForked() and block.getIndex() == last_block.getIndex() \
                and block.getPrevBlockHash() == prev_last_block.getBlockHash():

            # The block being considered has the same index has the last block you have in the blockchain.
            #                   You will store it in case it's the valid one.
            self._forked_blockchain.append(block)
            if self._monitor is True:
                self.display_info("Fork has been detected : 1 Block forked.", 3)
            ret = "1 block fork"

        # ------------------------------ Consider the intermediary state  ------------------------------ #
        # -------- when consensus need one more block to decide if you have the good blockchain -------- #
        elif self.hasForked() and block.getIndex() == self._forked_blockchain[-1].getIndex() + 1 \
                and block.getPrevBlockHash() == last_block.getBlockHash():

            # The Block considered is growing your blockchain and thus
            #          making it longer than the forked one.
            self._blockchain.addBlock(block)

            for i in block.getTransactions():
                self._transaction_pool.removeTransaction(i)

            if self._monitor is True:
                self.display_info("Fork has been detected : Consensus is being done.", 3)

            ret = "consensus being done"

        # ------------------------------- Consider the intermediary state  ------------------------------ #
        # ---- when consensus need one more block to decide the network has the good blockchain ---- #
        elif self.hasForked() and block.getIndex() == last_block.getIndex() + 1 \
                and block.getPrevBlockHash() == self._forked_blockchain[-1].getBlockHash():

            # The Block considered is growing the forked blockchain and thus
            #          making it longer your.
            self._forked_blockchain.append(block)

            if self._monitor is True:
                self.display_info("Fork has been detected : Consensus is being done.", 3)

            ret = "consensus being done"

        # -------------------- Consider the case in which a consensus must be done  --------------------- #
        # -------------------(two blockchains alive but with several blocks forked) --------------------- #
        elif self.hasForked() and block.getIndex() == last_block.getIndex() \
                and block.getPrevBlockHash() == self._forked_blockchain[-1].getBlockHash():

            # No consensus can be done as both blockchains are of the same size.
            self._forked_blockchain.append(block)

            if self._monitor is True:
                self.display_info(("Fork has been detected :" + str(len(self._forked_blockchain)) + "Block forked."), 3)

            ret = str(len(self._forked_blockchain)) + " block fork"

        # -------------------- Consider the case in which a consensus must be done  --------------------- #
        # -------------------(two blockchains alive but with several blocks forked) --------------------- #
        elif self.hasForked() and block.getIndex() == self._forked_blockchain[-1].getIndex() \
                and block.getPrevBlockHash() == last_block.getBlockHash():

            # No consensus can be done as both blockchains are of the same size.
            self._blockchain.addBlock(block)

            for i in block.getTransactions():
                self._transaction_pool.removeTransaction(i)

            if self._monitor is True:
                self.display_info(("Fork has been detected :" + str(len(self._forked_blockchain)) + "Block forked."), 3)

            ret = str(len(self._forked_blockchain)) + " block fork"

        # ------------------- Consider the case in which a consensus has been done and ------------------ #
        # ------------------------- you don't have the correct blockchain ------------------------------- #
        elif self.hasForked() and block.getIndex() == last_block.getIndex() + 2 \
                and block.getPrevBlockHash() == self._forked_blockchain[-1].getBlockHash():

            # The blockchain of the network is 2 blocks longer than yours and thus become the good blockchain.
            for i in self._forked_blockchain:
                # Replace the blocks that are wrong in the blockchain.
                if i.getIndex() < self._blockchain.length():

                    # Put back the transaction of the "wrong" blockchain in the transaction pool
                    for j in self._blockchain.getBlock(i.getIndex()).getTransactions():
                        self._transaction_pool.add_transaction(j)

                    self._blockchain.setBlock(i.getIndex(), i)

                    # Remove the transaction that are currently in the blockchain
                    for j in self._blockchain.getBlock(i.getIndex()).getTransactions():
                        self._transaction_pool.removeTransaction(j)

                # Add the additionnal block of the real blockchain
                else:
                    self._blockchain.addBlock(i)

                    # Remove the transaction that are currently in the blockchain
                    for j in i.getTransactions():
                        self._transaction_pool.removeTransaction(j)

            self._blockchain.addBlock(block)

            # Remove the transaction that are currently in the blockchain
            for j in block.getTransactions():
                self._transaction_pool.removeTransaction(j)

            self._forked_blockchain = []

            if self._monitor is True:
                self.display_info("Fork has been detected : Consensus done.", 3)

            ret = "consensus done"

        # ------------------- Consider the case in which a consensus has been done and ------------------ #
        # ------------------------- you have the correct blockchain ------------------------------- #
        elif self.hasForked() and block.getIndex() == self._forked_blockchain[-1].getIndex() + 2 \
                and block.getPrevBlockHash() == last_block.getBlockHash():

            # Your blockchain is 2 blocks longer than the one of the network and thus become the good blockchain.
            self._blockchain.addBlock(block)

            for i in block.getTransactions():
                self._transaction_pool.removeTransaction(i)

            self._forked_blockchain = []

            if self._monitor is True:
                self.display_info("Fork has been detected : Consensus done.", 3)

            ret = "consensus done"

        else:
            # Invalid block

            if self._monitor is True:
                self.display_info("Fork has been detected : Invalid Block.", 3)

            ret = "invalid block"

        return ret

    def is_proof_of_work_valid(self, block):

        hash = block.getBlockHash()

        difficulty = block.getDifficulty()

        return hash < math.pow(2, 256 - difficulty * Blockchain_Constant.DIFFICULTY_INCREASE)

    def proof_of_work(self, block):
        nonce_list = list()

        curr_nonce = random.randint(0, int(math.pow(2, 32)))

        while not self.__stop_event.is_set() and not (block.isMined() and self.is_proof_of_work_valid(block)):
            # Check if the peer didn't receive a block while mining.
            if self._blockchain.length() != 0 and block.getIndex() != self._blockchain.getLastBlock().getIndex() + 1:
                return "not mined"

            while curr_nonce in nonce_list:
                curr_nonce = random.randint(0, int(math.pow(2, 32)))

            block.setBlockNonce(curr_nonce)

            hash = block.computeHash()

            block.setBlockHash(hash)

            nonce_list.append(curr_nonce)

        if block.isMined():
            return "mined"
        else:
            return "not mined"

    def stop_mining(self):
        self.__stop_event.set()

    def get_good_difficulty(self, block, prev_block, curr_difficulty):

        a = datetime.datetime.fromtimestamp(block.getTimestamp())
        b = datetime.datetime.fromtimestamp(prev_block.getTimestamp())

        time_taken = a - b + datetime.timedelta(1e-6)

        if time_taken != Blockchain_Constant.MINING_TIME:
            return curr_difficulty * (
                    Blockchain_Constant.NB_BLOCK_BEFORE_DIFFICULTY_UPDATE * Blockchain_Constant.MINING_TIME) / time_taken
        else:
            return curr_difficulty

    def updateDifficulty(self):

        last_block = self._blockchain.getLastBlock()

        if last_block.getIndex() > 0 \
                and last_block.getIndex() % Blockchain_Constant.NB_BLOCK_BEFORE_DIFFICULTY_UPDATE == 0:
            prev_last_block = self._blockchain.getBlock(-Blockchain_Constant.NB_BLOCK_BEFORE_DIFFICULTY_UPDATE)
            self._difficulty = int(self.get_good_difficulty(last_block, prev_last_block, self._difficulty))

    def mine(self):

        """Implements the mining procedure."""

        last_block = self._blockchain.getLastBlock()

        transaction_list = self._transaction_pool.getTransactions(Blockchain_Constant.MAX_NB_TRANSACTION)

        if len(transaction_list) < Blockchain_Constant.MIN_NB_TRANSACTION:
            return 'not enough transaction in pool', None, None

        block = Block(index=last_block.getIndex() + 1, prev_block_hash=last_block.getBlockHash(),
                      transaction_list=transaction_list, difficulty=self._difficulty)

        ret1 = self.proof_of_work(block)

        if ret1 == "mined":
            ret2 = self.add_block(block)
        else:
            ret2 = None

        return ret1, ret2, block

    def mineBlock(self, block):
        return self.proof_of_work(block)

    def isTransactionHashKnown(self, transaction_hash):
        return self._transaction_pool.containsHash(transaction_hash) \
               or self._blockchain.containsTransaction(transaction_hash)

    def isBlockHashKnown(self, block_hash):
        return self._blockchain.containsBlock(block_hash)

    def getTransactionFromHash(self, transaction_hash):
        return self._transaction_pool.getTransactionFromHash(transaction_hash)

    def getBlockFromHash(self, block_hash):
        return self._blockchain.getBlockFromHash(block_hash)

    def valid_transaction_pool(self):
        blocks = self._blockchain.getBlocks()

        for block in blocks:
            transactions = block.getTransactions()

            for t in transactions:
                if self._transaction_pool.contains(t):
                    return False

        return True

    def display_info(self, text, x):
        print_there(x, 0, ("Blockchain Manager : " + str(text)))

    def log_transaction_pool(self, src_ip):
        directory = "Log/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        directory = "Log/Log_Peer_" + src_ip + "/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        stdout = open(("Log/Log_Peer_" + src_ip + "/transaction_pool.txt"), "a")

        stdout.write((str(datetime.datetime.now()) + " : Transaction Pool ("
                      + str(self._transaction_pool.getNbTransactions()) + " transactions) : \n"))

        stdout.write(str(self._transaction_pool))

        stdout.close()

    def log_blockchain(self, src_ip):
        directory = "Log/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        directory = "Log/Log_Peer_" + src_ip + "/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        stdout = open(("Log/Log_Peer_" + src_ip + "/blockchain.txt"), "a")

        stdout.write((str(datetime.datetime.now()) + " : Blockchain (" + str(self._blockchain.length())
                      + " blocks, difficulty=" + str(self._difficulty) + ") : \n"))

        stdout.write(str(self._blockchain) + "\n")

        if self.hasForked():
            stdout.write("Forked Blockchain : " + str(self._forked_blockchain) + "\n")

        stdout.close()
