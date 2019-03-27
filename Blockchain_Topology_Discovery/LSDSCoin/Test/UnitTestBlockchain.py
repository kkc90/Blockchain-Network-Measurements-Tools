import unittest
import time

from context import *

PRIVATE_KEY = generate_key()


class UnitTestBlockchain(unittest.TestCase):

    def test_bootstrap_blockchain(self):
        global PRIVATE_KEY

        init_difficulty = 2

        peer = Blockchain_Manager(init_difficulty, PRIVATE_KEY)

        blockchain = peer.getBlockchain()
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 1)

    def test_add_blocks_blockchain(self):
        global PRIVATE_KEY

        init_difficulty = 2

        peer = Blockchain_Manager(init_difficulty, PRIVATE_KEY)

        blockchain = peer.getBlockchain()

        for i in range(20):
            transaction = Transaction(("lol" + str(i)), ("xd" + str(i)), PRIVATE_KEY.public_key(), time.time())
            transaction.sign(PRIVATE_KEY)
            peer.add_transaction(transaction)

        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 1)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")

        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 2)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")

        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 3)

    def test_difficulty_update(self):
        global PRIVATE_KEY

        init_difficulty = 10

        peer = Blockchain_Manager(init_difficulty, PRIVATE_KEY)

        blockchain = peer.getBlockchain()

        for i in range(600):
            transaction = Transaction(("lol" + str(i)), ("xd" + str(i)), PRIVATE_KEY.public_key(), time.time())
            transaction.sign(PRIVATE_KEY)
            peer.add_transaction(transaction)

        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 1)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 2)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 3)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 4)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 5)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 6)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 7)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 8)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 9)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 10)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 11)

    def test_1block_forked_consensus_win_by_us(self):
        global PRIVATE_KEY

        init_difficulty = 2

        peer = Blockchain_Manager(init_difficulty, PRIVATE_KEY)

        blockchain = peer.getBlockchain()

        for i in range(50):
            transaction = Transaction(("lol" + str(i)), ("xd" + str(i)), PRIVATE_KEY.public_key(), time.time())
            transaction.sign(PRIVATE_KEY)
            peer.add_transaction(transaction)

        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 1)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 2)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 3)

        transaction_list = list()
        for i in range(25, 35):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i)), time.time()))

        index = blockchain.length() - 1
        block = Block(index, blockchain.getBlock(index - 1).getBlockHash(), transaction_list)

        ret = peer.mineBlock(block)

        self.assertTrue(ret == "mined")

        # Simulate the reception of a block
        ret = peer.add_block(block)

        self.assertTrue(ret == "1 block fork")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 3)

        ret, _ = peer.mine()

        self.assertTrue(ret == "consensus being done")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 4)

        ret, _ = peer.mine()

        self.assertTrue(ret == "consensus done")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 5)

    def test_1block_forked_consensus_win_by_them(self):
        global PRIVATE_KEY

        init_difficulty = 2

        peer = Blockchain_Manager(init_difficulty, PRIVATE_KEY)

        blockchain = peer.getBlockchain()

        for i in range(100):
            transaction = Transaction(("lol" + str(i)), ("xd" + str(i)), PRIVATE_KEY.public_key(), time.time())
            transaction.sign(PRIVATE_KEY)
            peer.add_transaction(transaction)

        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 1)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 2)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 3)

        transaction_list = list()
        for i in range(25, 35):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i)), time.time()))

        index = blockchain.length() - 1
        block1 = Block(index, blockchain.getBlock(index - 1).getBlockHash(), transaction_list)

        ret = peer.mineBlock(block1)
        self.assertTrue(ret == "mined")

        # Simulate the reception of a block
        ret = peer.add_block(block1)

        self.assertTrue(ret == "1 block fork")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 3)

        transaction_list = list()
        for i in range(45, 55):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i)), time.time()))

        index = index + 1
        block2 = Block(index, block1.getBlockHash(), transaction_list)

        ret = peer.mineBlock(block2)

        self.assertTrue(ret == "mined")

        # Simulate the reception of a block
        ret = peer.add_block(block2)

        self.assertTrue(ret == "consensus being done")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 3)

        transaction_list = list()
        for i in range(65, 75):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i)), time.time()))

        index = index + 1
        block3 = Block(index, block2.getBlockHash(), transaction_list)

        ret = peer.mineBlock(block3)

        self.assertTrue(ret == "mined")

        # Simulate the reception of a block
        ret = peer.add_block(block3)

        self.assertTrue(ret == "consensus done")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 5)
        self.assertTrue(blockchain.getBlock(-1) == block3)
        self.assertTrue(blockchain.getBlock(-2) == block2)
        self.assertTrue(blockchain.getBlock(-3) == block1)

    def test_2block_forked_consensus_win_by_us(self):
        global PRIVATE_KEY

        init_difficulty = 2

        peer = Blockchain_Manager(init_difficulty, PRIVATE_KEY)

        blockchain = peer.getBlockchain()

        for i in range(60):
            transaction = Transaction(("lol" + str(i)), ("xd" + str(i)), PRIVATE_KEY.public_key(), time.time())
            transaction.sign(PRIVATE_KEY)
            peer.add_transaction(transaction)

        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 1)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 2)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 3)

        transaction_list = list()
        for i in range(25, 35):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i)), time.time()))

        index = blockchain.length() - 1
        block1 = Block(index, blockchain.getBlock(index - 1).getBlockHash(), transaction_list)

        ret = peer.mineBlock(block1)

        self.assertTrue(ret == "mined")

        # Simulate the reception of a block
        ret = peer.add_block(block1)

        self.assertTrue(ret == "1 block fork")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 3)

        ret, _ = peer.mine()

        self.assertTrue(ret == "consensus being done")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 4)

        transaction_list = list()
        for i in range(45, 55):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i)), time.time()))

        index = index + 1
        block2 = Block(index, block1.getBlockHash(), transaction_list)

        ret = peer.mineBlock(block2)

        self.assertTrue(ret == "mined")

        # Simulate the reception of a block
        ret = peer.add_block(block2)

        self.assertTrue(ret == "2 block fork")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 4)

        ret, _ = peer.mine()

        self.assertTrue(ret == "consensus being done")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 5)

        ret, _ = peer.mine()

        self.assertTrue(ret == "consensus done")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 6)

    def test_2block_forked_consensus_win_by_them(self):
        global PRIVATE_KEY

        init_difficulty = 2

        peer = Blockchain_Manager(init_difficulty, PRIVATE_KEY)

        blockchain = peer.getBlockchain()

        for i in range(100):
            transaction = Transaction(("lol" + str(i)), ("xd" + str(i)), PRIVATE_KEY.public_key(), time.time())
            transaction.sign(PRIVATE_KEY)
            peer.add_transaction(transaction)

        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 1)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 2)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 3)

        transaction_list = list()
        for i in range(85, 95):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i)), time.time()))

        index = blockchain.length() - 1
        block1 = Block(index, blockchain.getBlock(index - 1).getBlockHash(), transaction_list)

        ret = peer.mineBlock(block1)

        self.assertTrue(ret == "mined")

        # Simulate the reception of a block
        ret = peer.add_block(block1)

        self.assertTrue(ret == "1 block fork")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 3)

        ret, _ = peer.mine()

        self.assertTrue(ret == "consensus being done")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 4)

        transaction_list = list()
        for i in range(45, 55):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i)), time.time()))

        index = index + 1
        block2 = Block(index, block1.getBlockHash(), transaction_list)

        ret = peer.mineBlock(block2)

        self.assertTrue(ret == "mined")

        # Simulate the reception of a block
        ret = peer.add_block(block2)

        self.assertTrue(ret == "2 block fork")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 4)

        transaction_list = list()
        for i in range(35, 45):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i)), time.time()))

        index = index + 1
        block3 = Block(index, block2.getBlockHash(), transaction_list)

        ret = peer.mineBlock(block3)

        self.assertTrue(ret == "mined")

        # Simulate the reception of a block
        ret = peer.add_block(block3)

        self.assertTrue(ret == "consensus being done")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 4)

        transaction_list = list()
        for i in range(55, 65):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i)), time.time()))

        index = index + 1
        block4 = Block(index, block3.getBlockHash(), transaction_list)

        ret = peer.mineBlock(block4)

        self.assertTrue(ret == "mined")

        # Simulate the reception of a block
        ret = peer.add_block(block4)

        self.assertTrue(ret == "consensus done")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 6)

    def test_2block_forked_consensus_win_by_them_with_difficulty_change(self):
        global PRIVATE_KEY

        init_difficulty = 2

        peer = Blockchain_Manager(init_difficulty, PRIVATE_KEY)

        blockchain = peer.getBlockchain()

        for i in range(600):
            transaction = Transaction(("lol" + str(i)), ("xd" + str(i)), PRIVATE_KEY.public_key(), time.time())
            transaction.sign(PRIVATE_KEY)
            peer.add_transaction(transaction)

        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 1)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 2)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 3)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 4)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 5)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 6)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 7)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 8)

        ret, _ = peer.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 9)

        transaction_list = list()
        for i in range(85, 95):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i)), time.time()))

        index = blockchain.length() - 1
        block1 = Block(index, blockchain.getBlock(index - 1).getBlockHash(), transaction_list)

        ret = peer.mineBlock(block1)

        self.assertTrue(ret == "mined")

        # Simulate the reception of a block
        ret = peer.add_block(block1)

        self.assertTrue(ret == "1 block fork")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 9)

        ret, _ = peer.mine()

        self.assertTrue(ret == "consensus being done")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 10)

        transaction_list = list()
        for i in range(45, 55):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i)), time.time()))

        index = index + 1
        block2 = Block(index, block1.getBlockHash(), transaction_list)

        ret = peer.mineBlock(block2)

        self.assertTrue(ret == "mined")

        # Simulate the reception of a block
        ret = peer.add_block(block2)

        self.assertTrue(ret == "2 block fork")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 10)

        transaction_list = list()
        for i in range(35, 45):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i)), time.time()))

        index = index + 1
        block3 = Block(index, block2.getBlockHash(), transaction_list)

        ret = peer.mineBlock(block3)

        self.assertTrue(ret == "mined")

        # Simulate the reception of a block
        ret = peer.add_block(block3)

        self.assertTrue(ret == "consensus being done")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 10)

        transaction_list = list()
        for i in range(55, 65):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i)), time.time()))

        index = index + 1
        block4 = Block(index, block3.getBlockHash(), transaction_list)

        ret = peer.mineBlock(block4)

        self.assertTrue(ret == "mined")

        # Simulate the reception of a block
        ret = peer.add_block(block4)

        self.assertTrue(ret == "consensus done")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.has_duplicate())
        self.assertTrue(blockchain.length() == 12)


if __name__ == '__main__':
    unittest.main()
