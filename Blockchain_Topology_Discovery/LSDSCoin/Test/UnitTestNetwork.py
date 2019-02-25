from context import *

import unittest
import os

class UnitTestNetwork(unittest.TestCase):
    def setUp(self):
        pass

    def test_get_list(self):
        storage1 = Storage(bootstrap="useless", miner=False, difficulty=3, test=True)
        storage2 = Storage(bootstrap="useless", miner=False, difficulty=3, test=True)

        storage1.peers = [Peer("aaa", 4), Peer("bbbb", 5)]

        peers = storage2._get_list(storage1.my_peer)

        self.assertEqual(peers[0].__dict__, storage1.peers[0].__dict__)

'''
    def test_broadcast_block(self):
        storage1 = Storage(bootstrap="useless", miner=False, difficulty=3, test=True)
        storage2 = Storage(bootstrap="useless", miner=False, difficulty=3, test=True)
        storage3 = Storage(bootstrap="useless", miner=False, difficulty=3, test=True)
        storage4 = Storage(bootstrap="useless", miner=False, difficulty=3, test=True)

        storage1.peers = [storage2.my_peer, storage3.my_peer]
        storage2.peers = [storage1.my_peer, storage4.my_peer]
        storage3.peers = [storage1.my_peer, storage4.my_peer]
        storage4.peers = [storage2.my_peer, storage3.my_peer]

        block = Block(0, 0, [])

        storage1._broadcast_block(block)

        self.assertEqual(storage2.testBlock, block)
        self.assertEqual(storage3.testBlock, block)
        self.assertEqual(storage4.testblock, block)

    def test_broadcast_transaction(self):
        storage1 = Storage(bootstrap="useless", miner=False, difficulty=3, test=True)
        storage2 = Storage(bootstrap="useless", miner=False, difficulty=3, test=True)
        storage3 = Storage(bootstrap="useless", miner=False, difficulty=3, test=True)
        storage4 = Storage(bootstrap="useless", miner=False, difficulty=3, test=True)

        storage1.peers = [storage2.my_peer, storage3.my_peer]
        storage2.peers = [storage1.my_peer, storage4.my_peer]
        storage3.peers = [storage1.my_peer, storage4.my_peer]
        storage4.peers = [storage2.my_peer, storage3.my_peer]

        transaction = Transaction(0, 0, storage1.my_peer.get_id())

        storage1._broadcast_transaction(transaction)

        self.assertEqual(storage2.testTransaction.__dict__, storage3.testTransaction.__dict__)

    def test_join(self):
        storage1 = Storage(bootstrap="useless", miner=False, difficulty=3, test=True)
        storage2 = Storage(bootstrap="useless", miner=False, difficulty=3, test=True)

        storage1._join(storage2.my_peer)

        self.assertEqual(storage1.my_peer.__dict__, storage2.peers[0].__dict__, )

    def test_bootstrap(self):
        bootstrap_storage = Storage(bootstrap=None, miner=False, difficulty=3, test=False)

        storage1 = Storage(bootstrap=bootstrap_storage.my_peer.get_id(), miner=False, difficulty=3, test=False)
        self.assertTrue(len(storage1.peers) == 1)
        storage2 = Storage(bootstrap=bootstrap_storage.my_peer.get_id(), miner=False, difficulty=3, test=False)
        self.assertTrue(len(storage2.peers) == 2)
'''

if __name__ == '__main__':
    unittest.main()
