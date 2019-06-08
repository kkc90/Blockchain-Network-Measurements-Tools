import unittest
import time

from context import *

PRIVATE_KEY = generate_key()


class UnitTestBlockchain(unittest.TestCase):

    def test_bootstrap_blockchain1(self):
        global PRIVATE_KEY

        init_difficulty = 2

        peer1 = Blockchain_Manager(init_difficulty, PRIVATE_KEY)

        blockchain1 = peer1.getBlockchain()

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertTrue(blockchain1.length() == 1)

    def test_add_blocks_blockchain1(self):
        global PRIVATE_KEY

        init_difficulty = 2

        peer1 = Blockchain_Manager(init_difficulty, PRIVATE_KEY)

        blockchain1 = peer1.getBlockchain()

        for i in range(20):
            transaction = Transaction(("lol" + str(i)), ("xd" + str(i)), PRIVATE_KEY.public_key(), time.time())
            transaction.sign(PRIVATE_KEY)
            peer1.add_transaction(transaction)

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 1)

        ret1, ret2, _ = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 2)

        ret1, ret2, _ = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 3)

    def test_difficulty_update(self):
        global PRIVATE_KEY

        init_difficulty = 10

        peer1 = Blockchain_Manager(init_difficulty, PRIVATE_KEY)

        blockchain1 = peer1.getBlockchain()

        for i in range(600):
            transaction = Transaction(("lol" + str(i)), ("xd" + str(i)), PRIVATE_KEY.public_key(), time.time())
            transaction.sign(PRIVATE_KEY)
            peer1.add_transaction(transaction)

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 1)

        ret1, ret2, _ = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 2)

        ret1, ret2, _ = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 3)

        ret1, ret2, _ = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")
        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 4)

        ret1, ret2, _ = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")
        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 5)

        ret1, ret2, _ = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")
        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 6)

        ret1, ret2, _ = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")
        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 7)

        ret1, ret2, _ = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")
        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 8)

        ret1, ret2, _ = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")
        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 9)

        ret1, ret2, _ = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")
        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 10)

        ret1, ret2, _ = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")
        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 11)

    def test_1block_forked_consensus_win_by_them(self):
        global PRIVATE_KEY

        init_difficulty = 2

        peer1 = Blockchain_Manager(init_difficulty, PRIVATE_KEY)
        peer2 = Blockchain_Manager(init_difficulty, PRIVATE_KEY)

        blockchain1 = peer1.getBlockchain()
        blockchain2 = peer2.getBlockchain()

        for i in range(50):
            transaction = Transaction(("lol" + str(i)), ("xd" + str(i)), PRIVATE_KEY.public_key(), time.time())
            transaction.sign(PRIVATE_KEY)
            peer1.add_transaction(transaction)
            peer2.add_transaction(transaction)

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 1)
        self.assertTrue(blockchain2.length() == 1)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        ret3 = peer2.add_block(block)

        self.assertTrue(ret3 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 2)
        self.assertTrue(blockchain2.length() == 2)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        ret3 = peer2.add_block(block)

        self.assertTrue(ret3 == "ok")
        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 3)
        self.assertTrue(blockchain2.length() == 3)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 4)
        self.assertTrue(blockchain2.length() == 3)

        ret1, ret2, _ = peer2.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 4)
        self.assertTrue(blockchain2.length() == 4)

        # Simulate the reception of a block
        ret = peer2.add_block(block)

        self.assertTrue(ret == "1 block fork")
        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 4)
        self.assertTrue(blockchain2.length() == 4)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        ret3 = peer2.add_block(block)

        self.assertTrue(ret3 == "consensus being done")
        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 5)
        self.assertTrue(blockchain2.length() == 4)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        ret3 = peer2.add_block(block)

        self.assertTrue(ret3 == "consensus done")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 6)
        self.assertTrue(blockchain2.length() == 6)

    def test_1block_forked_consensus_win_by_us(self):
        global PRIVATE_KEY

        init_difficulty = 2

        peer1 = Blockchain_Manager(init_difficulty, PRIVATE_KEY)
        peer2 = Blockchain_Manager(init_difficulty, PRIVATE_KEY)

        blockchain1 = peer1.getBlockchain()
        blockchain2 = peer2.getBlockchain()

        for i in range(50):
            transaction = Transaction(("lol" + str(i)), ("xd" + str(i)), PRIVATE_KEY.public_key(), time.time())
            transaction.sign(PRIVATE_KEY)
            peer1.add_transaction(transaction)
            peer2.add_transaction(transaction)

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 1)
        self.assertTrue(blockchain2.length() == 1)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        ret2 = peer2.add_block(block)

        self.assertTrue(ret2 == "ok")
        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 2)
        self.assertTrue(blockchain2.length() == 2)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        ret2 = peer2.add_block(block)

        self.assertTrue(ret2 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 3)
        self.assertTrue(blockchain2.length() == 3)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 4)
        self.assertTrue(blockchain2.length() == 3)

        ret1, ret2, block = peer2.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 4)
        self.assertTrue(blockchain2.length() == 4)

        # Simulate the reception of a block
        ret = peer2.add_block(block)

        self.assertTrue(ret == "1 block fork")
        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 4)
        self.assertTrue(blockchain2.length() == 4)

        ret1, ret2, block = peer2.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "consensus being done")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 4)
        self.assertTrue(blockchain2.length() == 5)

        ret1, ret2, block = peer2.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "consensus done")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 4)
        self.assertTrue(blockchain2.length() == 6)

    def test_2block_forked_consensus_win_by_us(self):
        global PRIVATE_KEY

        init_difficulty = 2

        peer1 = Blockchain_Manager(init_difficulty, PRIVATE_KEY)
        peer2 = Blockchain_Manager(init_difficulty, PRIVATE_KEY)

        blockchain1 = peer1.getBlockchain()
        blockchain2 = peer2.getBlockchain()

        for i in range(60):
            transaction = Transaction(("lol" + str(i)), ("xd" + str(i)), PRIVATE_KEY.public_key(), time.time())
            transaction.sign(PRIVATE_KEY)
            peer1.add_transaction(transaction)
            peer2.add_transaction(transaction)

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 1)
        self.assertTrue(blockchain2.length() == 1)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        ret3 = peer2.add_block(block)

        self.assertTrue(ret3 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 2)
        self.assertTrue(blockchain2.length() == 2)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        ret3 = peer2.add_block(block)

        self.assertTrue(ret3 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 3)
        self.assertTrue(blockchain2.length() == 3)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 4)
        self.assertTrue(blockchain2.length() == 3)

        ret1, ret2, _ = peer2.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 4)
        self.assertTrue(blockchain2.length() == 4)

        # Simulate the reception of a block
        ret = peer2.add_block(block)

        self.assertTrue(ret == "1 block fork")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 4)
        self.assertTrue(blockchain2.length() == 4)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        ret3 = peer2.add_block(block)

        self.assertTrue(ret3 == "consensus being done")
        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 5)
        self.assertTrue(blockchain2.length() == 4)

        ret1, ret2, block = peer2.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "2 block fork")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 5)
        self.assertTrue(blockchain2.length() == 5)

        ret1, ret2, block = peer2.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "consensus being done")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 5)
        self.assertTrue(blockchain2.length() == 6)

        ret1, ret2, block = peer2.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "consensus done")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 5)
        self.assertTrue(blockchain2.length() == 7)

    def test_2block_forked_consensus_win_by_them(self):
        global PRIVATE_KEY

        init_difficulty = 2

        peer1 = Blockchain_Manager(init_difficulty, PRIVATE_KEY)
        peer2 = Blockchain_Manager(init_difficulty, PRIVATE_KEY)

        blockchain1 = peer1.getBlockchain()
        blockchain2 = peer2.getBlockchain()

        for i in range(60):
            transaction = Transaction(("lol" + str(i)), ("xd" + str(i)), PRIVATE_KEY.public_key(), time.time())
            transaction.sign(PRIVATE_KEY)
            peer1.add_transaction(transaction)
            peer2.add_transaction(transaction)

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 1)
        self.assertTrue(blockchain2.length() == 1)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        ret3 = peer2.add_block(block)

        self.assertTrue(ret3 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 2)
        self.assertTrue(blockchain2.length() == 2)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        ret3 = peer2.add_block(block)

        self.assertTrue(ret3 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 3)
        self.assertTrue(blockchain2.length() == 3)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 4)
        self.assertTrue(blockchain2.length() == 3)

        ret1, ret2, _ = peer2.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 4)
        self.assertTrue(blockchain2.length() == 4)

        # Simulate the reception of a block
        ret = peer2.add_block(block)

        self.assertTrue(ret == "1 block fork")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 4)
        self.assertTrue(blockchain2.length() == 4)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        ret3 = peer2.add_block(block)

        self.assertTrue(ret3 == "consensus being done")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 5)
        self.assertTrue(blockchain2.length() == 4)

        ret1, ret2, block = peer2.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "2 block fork")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 5)
        self.assertTrue(blockchain2.length() == 5)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        ret = peer2.add_block(block)

        self.assertTrue(ret == "consensus being done")
        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 6)
        self.assertTrue(blockchain2.length() == 5)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        ret = peer2.add_block(block)

        self.assertTrue(ret == "consensus done")
        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 7)
        self.assertTrue(blockchain2.length() == 7)

    def test_4block_forked_consensus_win_by_them_with_difficulty_change(self):
        global PRIVATE_KEY

        init_difficulty = 2

        peer1 = Blockchain_Manager(init_difficulty, PRIVATE_KEY)
        peer2 = Blockchain_Manager(init_difficulty, PRIVATE_KEY)

        blockchain1 = peer1.getBlockchain()
        blockchain2 = peer2.getBlockchain()

        for i in range(200):
            transaction = Transaction(("lol" + str(i)), ("xd" + str(i)), PRIVATE_KEY.public_key(), time.time())
            transaction.sign(PRIVATE_KEY)
            peer1.add_transaction(transaction)
            peer2.add_transaction(transaction)

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 1)
        self.assertTrue(blockchain2.length() == 1)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        ret3 = peer2.add_block(block)

        self.assertTrue(ret3 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 2)
        self.assertTrue(blockchain2.length() == 2)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        ret3 = peer2.add_block(block)

        self.assertTrue(ret3 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 3)
        self.assertTrue(blockchain2.length() == 3)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        ret3 = peer2.add_block(block)

        self.assertTrue(ret3 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 4)
        self.assertTrue(blockchain2.length() == 4)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        ret3 = peer2.add_block(block)

        self.assertTrue(ret3 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 5)
        self.assertTrue(blockchain2.length() == 5)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        ret3 = peer2.add_block(block)

        self.assertTrue(ret3 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 6)
        self.assertTrue(blockchain2.length() == 6)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        ret3 = peer2.add_block(block)

        self.assertTrue(ret3 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 7)
        self.assertTrue(blockchain2.length() == 7)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        ret3 = peer2.add_block(block)

        self.assertTrue(ret3 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 8)
        self.assertTrue(blockchain2.length() == 8)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        ret3 = peer2.add_block(block)

        self.assertTrue(ret3 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 9)
        self.assertTrue(blockchain2.length() == 9)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 10)
        self.assertTrue(blockchain2.length() == 9)

        ret1, ret2, _ = peer2.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 10)
        self.assertTrue(blockchain2.length() == 10)

        # Simulate the reception of a block
        ret = peer2.add_block(block)

        self.assertTrue(ret == "1 block fork")
        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 10)
        self.assertTrue(blockchain2.length() == 10)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        ret3 = peer2.add_block(block)

        self.assertTrue(ret3 == "consensus being done")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 11)
        self.assertTrue(blockchain2.length() == 10)

        ret1, ret2, block = peer2.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "2 block fork")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 11)
        self.assertTrue(blockchain2.length() == 11)

        ret1, ret2, block = peer2.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "consensus being done")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 11)
        self.assertTrue(blockchain2.length() == 12)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        ret3 = peer2.add_block(block)

        self.assertTrue(ret3 == "3 block fork")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 12)
        self.assertTrue(blockchain2.length() == 12)

        ret1, ret2, block = peer2.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "consensus being done")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 12)
        self.assertTrue(blockchain2.length() == 13)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        ret3 = peer2.add_block(block)

        self.assertTrue(ret3 == "4 block fork")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 13)
        self.assertTrue(blockchain2.length() == 13)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        ret3 = peer2.add_block(block)

        self.assertTrue(ret3 == "consensus being done")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 14)
        self.assertTrue(blockchain2.length() == 13)

        ret1, ret2, block = peer1.mine()

        self.assertTrue(ret1 == "mined")
        self.assertTrue(ret2 == "ok")

        ret3 = peer2.add_block(block)

        self.assertTrue(ret3 == "consensus done")

        self.assertTrue(blockchain1.is_valid())
        self.assertTrue(blockchain2.is_valid())
        self.assertTrue(peer1.valid_transaction_pool())
        self.assertFalse(blockchain1.hasDuplicateTransactions())
        self.assertFalse(blockchain2.hasDuplicateTransactions())
        self.assertTrue(blockchain1.length() == 15)
        self.assertTrue(blockchain2.length() == 15)


if __name__ == '__main__':
    unittest.main()
