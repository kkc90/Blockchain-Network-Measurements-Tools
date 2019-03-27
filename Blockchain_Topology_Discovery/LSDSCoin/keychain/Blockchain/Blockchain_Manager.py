import math
import random

from .Block import *
from .Blockchain import *
from .Blockchain_Constant import *
from .Transaction_Pool import *


class Blockchain_Manager():
    def __init__(self, difficulty, private_key, mine=False):

        self._difficulty = difficulty
        self._last_difficulty = difficulty

        self._transaction_pool = Transaction_Pool()

        self._blockchain = Blockchain()
        self._add_genesis_block()

        self._forked_blockchain = list()

        self._private_key = private_key

        self._mine = mine

    def add_transaction(self, transaction):
        self._transaction_pool.add_transaction(transaction)

    def getBlockchain(self):
        return self._blockchain

    def hasForked(self):
        return len(self._forked_blockchain) > 0

    def getPublicKey(self):
        return self._private_key.public_key()

    def _add_genesis_block(self):
        """Adds the genesis block to your blockchain."""
        index = 0
        prev_block_hash = Blockchain_Constant.GENESIS_PREV_HASH
        transaction_list = []
        genesis_block = Block(index, prev_block_hash, transaction_list)
        self.proof_of_work(genesis_block)

        self._blockchain.addBlock(genesis_block)

    def add_block(self, block):

        last_block = self._blockchain.getLasBlock()

        if not self.is_proof_of_work_valid(block):
            ret = "invalid block"

            # ---------------------------------- Basic case ------------------------------- #
            #                                                                               #
            #   1. No fork has been detected previously                                     #
            #   2. The block is valid with respect to the current blockchain                #
            #   3. The block has a correct proof of work                                    #
            #                                                                               #
            # ----------------------------------------------------------------------------- #

        elif not self.hasForked() and block.getIndex() == last_block.getIndex() + 1 and block.getPrevBlockHash() == last_block.getBlockHash():
            self._blockchain.addBlock(block)

            for i in block.getTransactions():
                self._transaction_pool.removeTransaction(i)

            ret = "ok"

        # -------------- Case in which the Blockchain you have is not correct anymore ---------- #
        elif block.getIndex() > last_block.getIndex() + 2:
            # You will ask your neighbours for the good blockchain #
            ret = "not implemented"

            # -------------- Consensus is needed ------------- #
        elif self.hasForked() or block.getIndex() == last_block.getIndex():
            ret = self.consensus(block)

        else:
            ret = "invalid block"

        self.updateDifficulty()

        return ret

    def consensus(self, block):

        last_block = self._blockchain.getLasBlock()
        prev_last_block = self._blockchain.getPrevLastBlock()

        # -------------------- Consider the case in which a consensus must be done --------------------- #
        # -------------------------- (two blockchains alive with one blocks forked --------------------- #
        if not self.hasForked() and block.getIndex() == last_block.getIndex() \
                and block.getPrevBlockHash() == prev_last_block.getBlockHash():

            # The block being considered has the same index has the last block you have in the blockchain.
            #                   You will store it in case it's the valid one.
            self._forked_blockchain.append(block)
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

            ret = "consensus being done"

        # ------------------------------- Consider the intermediary state  ------------------------------ #
        # ---- when consensus need one more block to decide the network you have the good blockchain ---- #
        elif self.hasForked() and block.getIndex() == last_block.getIndex() + 1 \
                and block.getPrevBlockHash() == self._forked_blockchain[-1].getBlockHash():

            # The Block considered is growing the forked blockchain and thus
            #          making it longer your.
            self._forked_blockchain.append(block)
            ret = "consensus being done"

        # -------------------- Consider the case in which a consensus must be done  --------------------- #
        # -------------------(two blockchains alive but with several blocks forked) --------------------- #
        elif self.hasForked() and block.getIndex() == last_block.getIndex() \
                and block.getPrevBlockHash() == self._forked_blockchain[-1].getBlockHash():

            # No consensus can be done as both blockchains are of the same size.
            self._forked_blockchain.append(block)
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

            ret = "consensus done"

        else:
            # Invalid block
            ret = "invalid block"

        return ret

    def is_proof_of_work_valid(self, block):

        hash = block.getBlockHash()

        if block.computeHash() != hash:
            return False

        # Difficulty has been updated
        if self._blockchain.length() > 0:
            last_block = self._blockchain.getLasBlock()
            last_block_index = last_block.getIndex()

            if last_block_index // Blockchain_Constant.NB_BLOCK_BEFORE_DIFFICULTY_UPDATE \
                    > block.getIndex() // Blockchain_Constant.NB_BLOCK_BEFORE_DIFFICULTY_UPDATE:
                difficulty = self._last_difficulty

            # Block is coming from a fork and difficulty has been updated
            elif self.hasForked() and last_block_index // Blockchain_Constant.NB_BLOCK_BEFORE_DIFFICULTY_UPDATE < \
                    self._forked_blockchain[
                        -1].getIndex() // Blockchain_Constant.NB_BLOCK_BEFORE_DIFFICULTY_UPDATE:
                nb_change_of_difficulty = self._forked_blockchain[
                                              -1].getIndex() // Blockchain_Constant.NB_BLOCK_BEFORE_DIFFICULTY_UPDATE \
                                          - last_block_index // Blockchain_Constant.NB_BLOCK_BEFORE_DIFFICULTY_UPDATE

                difficulty = self._difficulty

                i = 0
                while i > 0:
                    index_last_block = (last_block_index // Blockchain_Constant.NB_BLOCK_BEFORE_DIFFICULTY_UPDATE + i) \
                                       * Blockchain_Constant.NB_BLOCK_BEFORE_DIFFICULTY_UPDATE
                    index_prev_last_block = index_last_block - Blockchain_Constant.NB_BLOCK_BEFORE_DIFFICULTY_UPDATE

                    if index_last_block > self._forked_blockchain[0].getIndex():
                        last_block = self._forked_blockchain[index_last_block - self._forked_blockchain[0].getIndex()]
                    else:
                        last_block = self._blockchain.getBlock(index_last_block)

                    if index_prev_last_block > self._forked_blockchain[0].getIndex():
                        prev_last_block = self._forked_blockchain[
                            index_prev_last_block - self._forked_blockchain[0].getIndex()]
                    else:
                        prev_last_block = self._blockchain.getBlock(index_prev_last_block)

                    difficulty = self.get_good_difficulty(last_block, prev_last_block, difficulty)

                    i = i + 1
            # Difficulty has not been updated
            else:
                difficulty = self._difficulty


        # Difficulty has not been updated
        else:
            difficulty = self._difficulty

        return int.from_bytes(hash, byteorder="little") < math.pow(2,
                                                                   256 - difficulty * Blockchain_Constant.DIFFICULTY_INCREASE)

    def proof_of_work(self, block):
        nonce_list = list()

        curr_nonce = random.randint(0, int(math.pow(2, 32)))
        block.setBlockNonce(curr_nonce)
        hash = block.computeHash()
        block.setBlockHash(hash)

        while not self.is_proof_of_work_valid(block):
            if block.getIndex() != self._blockchain.getLasBlock().getIndex() + 1:
                return "not mined"

            nonce_list.append(curr_nonce)

            while True:
                curr_nonce = random.randint(0, int(math.pow(2, 32)))

                if curr_nonce not in nonce_list:
                    break

            block.setBlockNonce(curr_nonce)
            hash = block.computeHash()
            block.setBlockHash(hash)

        return "mined"

    def get_good_difficulty(self, block, prev_block, curr_difficulty):

        a = datetime.datetime.fromtimestamp(block.getTimestamp())
        b = datetime.datetime.fromtimestamp(prev_block.getTimestamp())

        time_taken = a - b

        if time_taken != Blockchain_Constant.MINING_TIME:
            return curr_difficulty * (
                    Blockchain_Constant.NB_BLOCK_BEFORE_DIFFICULTY_UPDATE * Blockchain_Constant.MINING_TIME) / time_taken
        else:
            return curr_difficulty

    def updateDifficulty(self):

        last_block = self._blockchain.getLasBlock()

        if last_block.getIndex() > 0 and last_block.getIndex() % Blockchain_Constant.NB_BLOCK_BEFORE_DIFFICULTY_UPDATE == 0:
            prev_last_block = self._blockchain.getBlock(-Blockchain_Constant.NB_BLOCK_BEFORE_DIFFICULTY_UPDATE)
            tmp = self._difficulty
            self._difficulty = self.get_good_difficulty(last_block, prev_last_block, self._difficulty)

            if self._difficulty != tmp:
                self._last_difficulty = tmp

    def mine(self):

        """Implements the mining procedure."""
        if self._transaction_pool.isEmpty():
            return "empty transaction pool"

        last_block = self._blockchain.getLasBlock()

        transaction_list = self._transaction_pool.get_transactions(Blockchain_Constant.MAX_NB_TRANSACTION)

        block = Block(index=last_block.getIndex() + 1, prev_block_hash=last_block.getBlockHash(),
                      transaction_list=transaction_list)

        ret = self.proof_of_work(block)

        if ret == "mined":
            ret = self.add_block(block)

        return ret, block

    def mineBlock(self, block):
        return self.proof_of_work(block)
