from context import *

import unittest

class UnitTestBlockchain(unittest.TestCase):

    def test_bootstrap_blockchain(self):
        init_difficulty = 2
        blockchain = Blockchain(init_difficulty)
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 1)

    def test_add_blocks_blockchain(self):
        init_difficulty = 2
        blockchain = Blockchain(init_difficulty)
        for i in range(20):
            blockchain.add_transaction(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i))))

        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 1)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 2)
        self.assertTrue(blockchain.getNbTransactions() == 10)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 3)
        self.assertTrue(blockchain.getNbTransactions() == 0)

    def test_difficulty_update(self):
        init_difficulty = 10
        blockchain = Blockchain(init_difficulty)
        for i in range(600):
            blockchain.add_transaction(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i))))

        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 1)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 2)
        self.assertTrue(blockchain.getNbTransactions() == 590)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 3)
        self.assertTrue(blockchain.getNbTransactions() == 580)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 4)
        self.assertTrue(blockchain.getNbTransactions() == 570)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 5)
        self.assertTrue(blockchain.getNbTransactions() == 560)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 6)
        self.assertTrue(blockchain.getNbTransactions() == 550)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 7)
        self.assertTrue(blockchain.getNbTransactions() == 540)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 8)
        self.assertTrue(blockchain.getNbTransactions() == 530)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 9)
        self.assertTrue(blockchain.getNbTransactions() == 520)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 10)
        self.assertTrue(blockchain.getNbTransactions() == 510)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 11)
        self.assertTrue(blockchain.getNbTransactions() == 500)

    def test_1block_forked_consensus_win_by_us(self):
        init_difficulty = 2
        blockchain = Blockchain(init_difficulty)
        for i in range(50):
            blockchain.add_transaction(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i))))

        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 1)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 2)
        self.assertTrue(blockchain.getNbTransactions() == 40)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 3)
        self.assertTrue(blockchain.getNbTransactions() == 30)

        transaction_list = list()
        for i in range(25, 35):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i))))

        index = blockchain.length() - 1
        block = Block(index, blockchain.getBlock(index - 1).getBlockHash(), transaction_list)

        ret = blockchain.mineBlock(block)

        self.assertTrue(ret == "ok")

        # Simulate the reception of a block
        ret = blockchain.add_block(block)

        self.assertTrue(ret == "1 block fork")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 3)
        self.assertTrue(blockchain.getNbTransactions() == 30)

        ret = blockchain.mine()

        self.assertTrue(ret == "consensus being done")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 4)
        self.assertTrue(blockchain.getNbTransactions() == 20)

        ret = blockchain.mine()

        self.assertTrue(ret == "consensus done")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 5)
        self.assertTrue(blockchain.getNbTransactions() == 10)

    def test_1block_forked_consensus_win_by_them(self):
        init_difficulty = 2
        blockchain = Blockchain(init_difficulty)
        for i in range(60):
            blockchain.add_transaction(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i))))

        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 1)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 2)
        self.assertTrue(blockchain.getNbTransactions() == 50)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 3)
        self.assertTrue(blockchain.getNbTransactions() == 40)

        transaction_list = list()
        for i in range(25, 35):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i))))

        index = blockchain.length() - 1
        block1 = Block(index, blockchain.getBlock(index - 1).getBlockHash(), transaction_list)

        ret = blockchain.mineBlock(block1)
        self.assertTrue(ret == "ok")

        # Simulate the reception of a block
        ret = blockchain.add_block(block1)

        self.assertTrue(ret == "1 block fork")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 3)
        self.assertTrue(blockchain.getNbTransactions() == 40)

        transaction_list = list()
        for i in range(45, 55):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i))))

        index = index + 1
        block2 = Block(index, block1.getBlockHash(), transaction_list)

        ret = blockchain.mineBlock(block2)

        self.assertTrue(ret == "ok")

        # Simulate the reception of a block
        ret = blockchain.add_block(block2)

        self.assertTrue(ret == "consensus being done")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 3)
        self.assertTrue(blockchain.getNbTransactions() == 40)

        transaction_list = list()
        for i in range(35, 45):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i))))

        index = index + 1
        block3 = Block(index, block2.getBlockHash(), transaction_list)

        ret = blockchain.mineBlock(block3)

        self.assertTrue(ret == "ok")

        # Simulate the reception of a block
        ret = blockchain.add_block(block3)

        self.assertTrue(ret == "consensus done")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 5)
        self.assertTrue(blockchain.getNbTransactions() == 20)
        self.assertTrue(blockchain.getBlock(-1) == block3)
        self.assertTrue(blockchain.getBlock(-2) == block2)
        self.assertTrue(blockchain.getBlock(-3) == block1)

    def test_2block_forked_consensus_win_by_us(self):
        init_difficulty = 2
        blockchain = Blockchain(init_difficulty)
        for i in range(60):
            blockchain.add_transaction(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i))))

        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 1)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 2)
        self.assertTrue(blockchain.getNbTransactions() == 50)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 3)
        self.assertTrue(blockchain.getNbTransactions() == 40)

        transaction_list = list()
        for i in range(25, 35):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i))))

        index = blockchain.length() - 1
        block1 = Block(index, blockchain.getBlock(index - 1).getBlockHash(), transaction_list)

        ret = blockchain.mineBlock(block1)

        self.assertTrue(ret == "ok")

        # Simulate the reception of a block
        ret = blockchain.add_block(block1)

        self.assertTrue(ret == "1 block fork")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 3)
        self.assertTrue(blockchain.getNbTransactions() == 40)

        ret = blockchain.mine()

        self.assertTrue(ret == "consensus being done")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 4)
        self.assertTrue(blockchain.getNbTransactions() == 30)

        transaction_list = list()
        for i in range(45, 55):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i))))

        index = index + 1
        block2 = Block(index, block1.getBlockHash(), transaction_list)

        ret = blockchain.mineBlock(block2)

        self.assertTrue(ret == "ok")

        # Simulate the reception of a block
        ret = blockchain.add_block(block2)

        self.assertTrue(ret == "n block fork")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 4)
        self.assertTrue(blockchain.getNbTransactions() == 30)

        ret = blockchain.mine()

        self.assertTrue(ret == "consensus being done")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 5)
        self.assertTrue(blockchain.getNbTransactions() == 20)

        ret = blockchain.mine()

        self.assertTrue(ret == "consensus done")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 6)
        self.assertTrue(blockchain.getNbTransactions() == 10)

    def test_2block_forked_consensus_win_by_them(self):
        init_difficulty = 2
        blockchain = Blockchain(init_difficulty)
        for i in range(100):
            blockchain.add_transaction(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i))))

        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 1)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 2)
        self.assertTrue(blockchain.getNbTransactions() == 90)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 3)
        self.assertTrue(blockchain.getNbTransactions() == 80)

        transaction_list = list()
        for i in range(85, 95):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i))))

        index = blockchain.length() - 1
        block1 = Block(index, blockchain.getBlock(index - 1).getBlockHash(), transaction_list)

        ret = blockchain.mineBlock(block1)

        self.assertTrue(ret == "ok")

        # Simulate the reception of a block
        ret = blockchain.add_block(block1)

        self.assertTrue(ret == "1 block fork")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 3)
        self.assertTrue(blockchain.getNbTransactions() == 80)

        ret = blockchain.mine()

        self.assertTrue(ret == "consensus being done")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 4)
        self.assertTrue(blockchain.getNbTransactions() == 70)

        transaction_list = list()
        for i in range(45, 55):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i))))

        index = index + 1
        block2 = Block(index, block1.getBlockHash(), transaction_list)

        ret = blockchain.mineBlock(block2)

        self.assertTrue(ret == "ok")

        # Simulate the reception of a block
        ret = blockchain.add_block(block2)

        self.assertTrue(ret == "n block fork")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 4)
        self.assertTrue(blockchain.getNbTransactions() == 70)

        transaction_list = list()
        for i in range(35, 45):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i))))

        index = index + 1
        block3 = Block(index, block2.getBlockHash(), transaction_list)

        ret = blockchain.mineBlock(block3)

        self.assertTrue(ret == "ok")

        # Simulate the reception of a block
        ret = blockchain.add_block(block3)

        self.assertTrue(ret == "consensus being done")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 4)
        self.assertTrue(blockchain.getNbTransactions() == 70)

        transaction_list = list()
        for i in range(55, 65):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i))))

        index = index + 1
        block4 = Block(index, block3.getBlockHash(), transaction_list)

        ret = blockchain.mineBlock(block4)

        self.assertTrue(ret == "ok")

        # Simulate the reception of a block
        ret = blockchain.add_block(block4)

        self.assertTrue(ret == "consensus done")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 6)
        self.assertTrue(blockchain.getNbTransactions() == 50)

    def test_2block_forked_consensus_win_by_them_with_difficulty_change(self):
        init_difficulty = 2
        blockchain = Blockchain(init_difficulty)
        for i in range(600):
            blockchain.add_transaction(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i))))

        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 1)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 2)
        self.assertTrue(blockchain.getNbTransactions() == 590)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 3)
        self.assertTrue(blockchain.getNbTransactions() == 580)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 4)
        self.assertTrue(blockchain.getNbTransactions() == 570)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 5)
        self.assertTrue(blockchain.getNbTransactions() == 560)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 6)
        self.assertTrue(blockchain.getNbTransactions() == 550)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 7)
        self.assertTrue(blockchain.getNbTransactions() == 540)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 8)
        self.assertTrue(blockchain.getNbTransactions() == 530)

        ret = blockchain.mine()

        self.assertTrue(ret == "ok")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 9)
        self.assertTrue(blockchain.getNbTransactions() == 520)

        transaction_list = list()
        for i in range(85, 95):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i))))

        index = blockchain.length() - 1
        block1 = Block(index, blockchain.getBlock(index - 1).getBlockHash(), transaction_list)

        ret = blockchain.mineBlock(block1)

        self.assertTrue(ret == "ok")

        # Simulate the reception of a block
        ret = blockchain.add_block(block1)

        self.assertTrue(ret == "1 block fork")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 9)
        self.assertTrue(blockchain.getNbTransactions() == 520)

        ret = blockchain.mine()

        self.assertTrue(ret == "consensus being done")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 10)
        self.assertTrue(blockchain.getNbTransactions() == 510)

        transaction_list = list()
        for i in range(45, 55):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i))))

        index = index + 1
        block2 = Block(index, block1.getBlockHash(), transaction_list)

        ret = blockchain.mineBlock(block2)

        self.assertTrue(ret == "ok")

        # Simulate the reception of a block
        ret = blockchain.add_block(block2)

        self.assertTrue(ret == "n block fork")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 10)
        self.assertTrue(blockchain.getNbTransactions() == 510)

        transaction_list = list()
        for i in range(35, 45):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i))))

        index = index + 1
        block3 = Block(index, block2.getBlockHash(), transaction_list)

        ret = blockchain.mineBlock(block3)

        self.assertTrue(ret == "ok")

        # Simulate the reception of a block
        ret = blockchain.add_block(block3)

        self.assertTrue(ret == "consensus being done")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 10)
        self.assertTrue(blockchain.getNbTransactions() == 510)

        transaction_list = list()
        for i in range(55, 65):
            transaction_list.append(Transaction(("lol" + str(i)), ("xd" + str(i)), ("peer" + str(i))))

        index = index + 1
        block4 = Block(index, block3.getBlockHash(), transaction_list)

        ret = blockchain.mineBlock(block4)

        self.assertTrue(ret == "ok")

        # Simulate the reception of a block
        ret = blockchain.add_block(block4)

        self.assertTrue(ret == "consensus done")
        self.assertTrue(blockchain.is_valid())
        self.assertTrue(blockchain.length() == 12)
        self.assertTrue(blockchain.getNbTransactions() == 490)

if __name__ == '__main__':
    unittest.main()
