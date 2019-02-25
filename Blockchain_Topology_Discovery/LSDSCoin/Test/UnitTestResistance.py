from context import *

import unittest

class UnitTestResistance(unittest.TestCase):
    def resistance_test(self):
        MODIFIED_VALUE_KEY = 3
        INITIAL_VALUE = 5
        MODIFIED_VALUE = 10
        malicious_node = Storage(bootstrap=None, miner=True, difficulty=1, test=False, debug=False)
        correct_node_1 = Storage(bootstrap=malicious_node.my_peer.get_id(), miner=True, difficulty=1, test=False,
                                 debug=False)
        correct_node_2 = Storage(bootstrap=malicious_node.my_peer.get_id(), miner=True, difficulty=1, test=False,
                                 debug=False)
        correct_node_3 = Storage(bootstrap=malicious_node.my_peer.get_id(), miner=True, difficulty=1, test=False,
                                 debug=False)
        correct_node_4 = Storage(bootstrap=malicious_node.my_peer.get_id(), miner=True, difficulty=1, test=False,
                                 debug=False)
        correct_node_5 = Storage(bootstrap=malicious_node.my_peer.get_id(), miner=True, difficulty=1, test=False,
                                 debug=False)

        # Put some transactions
        correct_node_1.put(MODIFIED_VALUE_KEY, INITIAL_VALUE, block=True)
        correct_node_1.put(4, 4, block=True)
        correct_node_1.put(5, 4, block=True)

        for block in malicious_blocks:
            for transaction in block.getTransactions():
                if transaction.getKey() == MODIFIED_VALUE_KEY:
                    transaction._value = MODIFIED_VALUE

        correct_node_1.put(6, 4, block=True)

        value = correct_node_1.retrieve(MODIFIED_VALUE_KEY)

        self.assertTrue(value == INITIAL_VALUE)


if __name__ == '__main__':
    unittest.main()
