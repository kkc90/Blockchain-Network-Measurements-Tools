import socket
import time
import unittest

from context import *

PRIVATE_KEY = generate_key()


class UnitTestNetwork(unittest.TestCase):

    # def test_connection(self):
    #     src_ip = socket.gethostbyname(socket.gethostname())
    #     tmp = src_ip.split(".")
    #     prefix = tmp[0] + "." + tmp[1] + "." + tmp[2] + "."
    #
    #     ip1 = prefix + "1"
    #     ip2 = prefix + "2"
    #
    #     port = 8333
    #
    #     peer_1 = (ip1, port, Protocol_Constant.NODE_NETWORK, time_to_crawl.time_to_crawl())
    #
    #     a = Network_Manager(ip1, port, Protocol_Constant.NODE_NONE, "mainnet", [], None)
    #     b = Network_Manager(ip2, port, Protocol_Constant.NODE_NONE, "mainnet", [peer_1], None)
    #
    #     a.start_listener_thread()
    #     b.start_listener_thread()
    #
    #     b.connect(peer_1[0], peer_1[1], peer_1[2], peer_1[3])
    #
    #     time_to_crawl.sleep(Network_Constant.HANDSHAKE_TIMEOUT + 1)
    #
    #     test_1 = b.get_nb_connection()
    #     test_2 = a.get_nb_connection()
    #
    #     a.join_listener_thread()
    #     b.join_listener_thread()
    #
    #     a.join_connections()
    #     b.join_connections()
    #
    #     self.assertTrue(test_1 == 1)
    #     self.assertTrue(test_2 == 1)
    #
    # def test_connection_to_peer_down(self):
    #     src_ip = socket.gethostbyname(socket.gethostname())
    #     tmp = src_ip.split(".")
    #     prefix = tmp[0] + "." + tmp[1] + "." + tmp[2] + "."
    #
    #     ip1 = prefix + "1"
    #     ip2 = prefix + "2"
    #     ip3 = prefix + "3"
    #
    #     port = 8333
    #
    #     peer_3 = (ip3, port, Protocol_Constant.NODE_NETWORK, time_to_crawl.time_to_crawl())
    #
    #     a = Network_Manager(ip1, port, Protocol_Constant.NODE_NONE, "mainnet", [], None)
    #     b = Network_Manager(ip2, port, Protocol_Constant.NODE_NONE, "mainnet", [peer_3], None)
    #
    #     a.start_listener_thread()
    #     b.start_listener_thread()
    #
    #     b.connect(peer_3[0], peer_3[1], peer_3[2], peer_3[3])
    #
    #     time_to_crawl.sleep(Network_Constant.HANDSHAKE_TIMEOUT + 1)
    #
    #     test_1 = b.get_nb_connection()
    #     test_2 = a.get_nb_connection()
    #
    #     a.join_listener_thread()
    #     b.join_listener_thread()
    #
    #     a.join_connections()
    #     b.join_connections()
    #
    #     self.assertTrue(test_1 == 0)
    #     self.assertTrue(test_2 == 0)
    #
    # def test_peer_down(self):
    #     src_ip = socket.gethostbyname(socket.gethostname())
    #     tmp = src_ip.split(".")
    #     prefix = tmp[0] + "." + tmp[1] + "." + tmp[2] + "."
    #
    #     ip1 = prefix + "1"
    #     ip2 = prefix + "2"
    #
    #     port = 8333
    #
    #     peer_1 = (ip1, port, Protocol_Constant.NODE_NETWORK, time_to_crawl.time_to_crawl())
    #
    #     a = Network_Manager(ip1, port, Protocol_Constant.NODE_NONE, "mainnet", [], None)
    #     b = Network_Manager(ip2, port, Protocol_Constant.NODE_NONE, "mainnet", [peer_1], None)
    #
    #     a.start_listener_thread()
    #     b.start_listener_thread()
    #
    #     b.connect(peer_1[0], peer_1[1], peer_1[2], peer_1[3])
    #
    #     time_to_crawl.sleep(Network_Constant.HANDSHAKE_TIMEOUT + 1)
    #
    #     test_1 = b.get_nb_connection()
    #     test_2 = a.get_nb_connection()
    #
    #     b.kill_connections()
    #
    #     time_to_crawl.sleep(Network_Constant.SOCKET_TIMEOUT * 3 + Network_Constant.PING_TIMEOUT + 1)
    #
    #     a.remove_dead_connection()
    #     b.remove_dead_connection()
    #
    #     test_3 = b.get_nb_connection()
    #     test_4 = a.get_nb_connection()
    #
    #     a.kill_connections()
    #
    #     a.join_listener_thread()
    #     b.join_listener_thread()
    #
    #     a.join_connections()
    #     b.join_connections()
    #
    #     self.assertTrue(test_1 == 1)
    #     self.assertTrue(test_2 == 1)
    #
    #     self.assertTrue(test_3 == 0)
    #     self.assertTrue(test_4 == 0)
    #
    # def test_getaddr_exchange(self):
    #     src_ip = socket.gethostbyname(socket.gethostname())
    #     tmp = src_ip.split(".")
    #     prefix = tmp[0] + "." + tmp[1] + "." + tmp[2] + "."
    #
    #     ip1 = prefix + "1"
    #     ip2 = prefix + "2"
    #     ip3 = prefix + "3"
    #     ip4 = prefix + "4"
    #     ip5 = prefix + "5"
    #
    #     port = 8333
    #
    #     peer_1 = (ip1, port, Protocol_Constant.NODE_NETWORK, time_to_crawl.time_to_crawl())
    #     peer_3 = (ip3, port, Protocol_Constant.NODE_NETWORK, time_to_crawl.time_to_crawl())
    #     peer_4 = (ip4, port, Protocol_Constant.NODE_NETWORK, time_to_crawl.time_to_crawl())
    #     peer_5 = (ip5, port, Protocol_Constant.NODE_NETWORK, time_to_crawl.time_to_crawl())
    #
    #     a = Network_Manager(ip1, port, Protocol_Constant.NODE_NONE, "mainnet", [], None)
    #     b = Network_Manager(ip2, port, Protocol_Constant.NODE_NONE, "mainnet", [peer_1, peer_3, peer_4, peer_5], None)
    #
    #     a.start_listener_thread()
    #     b.start_listener_thread()
    #
    #     b.connect(peer_1[0], peer_1[1], peer_1[2], peer_1[3])
    #
    #     time_to_crawl.sleep(Network_Constant.HANDSHAKE_TIMEOUT + 1)
    #
    #     test_1 = b.get_nb_connection()
    #     test_2 = a.get_nb_connection()
    #
    #     test_3 = b.get_nb_peer_in_pool()
    #     test_4 = a.get_nb_peer_in_pool()
    #
    #     a.get_peers()
    #
    #     time_to_crawl.sleep(Network_Constant.SOCKET_TIMEOUT * 3 + Network_Constant.ADDR_TIMEOUT + 1)
    #
    #     test_5 = b.get_nb_connection()
    #     test_6 = a.get_nb_connection()
    #
    #     test_7 = b.get_nb_peer_in_pool()
    #     test_8 = a.get_nb_peer_in_pool()
    #
    #     a.join_listener_thread()
    #     b.join_listener_thread()
    #
    #     a.join_connections()
    #     b.join_connections()
    #
    #     self.assertTrue(test_1 == 1)
    #     self.assertTrue(test_2 == 1)
    #
    #     self.assertTrue(test_3 == 3)
    #     self.assertTrue(test_4 == 0)
    #
    #     self.assertTrue(test_5 == 1)
    #     self.assertTrue(test_6 == 1)
    #
    #     self.assertTrue(test_7 == 3)
    #     self.assertTrue(test_8 == 1)
    #
    # def test_tx_broadcast_neighbour(self):
    #     global PRIVATE_KEY
    #
    #     init_difficulty = 2
    #
    #     src_ip = socket.gethostbyname(socket.gethostname())
    #     tmp = src_ip.split(".")
    #     prefix = tmp[0] + "." + tmp[1] + "." + tmp[2] + "."
    #
    #     ip1 = prefix + "1"
    #     ip2 = prefix + "2"
    #     ip3 = prefix + "3"
    #     ip4 = prefix + "4"
    #     ip5 = prefix + "5"
    #
    #     port = 8333
    #
    #     peer_1 = (ip1, port, Protocol_Constant.NODE_NETWORK, time_to_crawl.time_to_crawl())
    #     peer_2 = (ip2, port, Protocol_Constant.NODE_NETWORK, time_to_crawl.time_to_crawl())
    #     peer_3 = (ip3, port, Protocol_Constant.NODE_NETWORK, time_to_crawl.time_to_crawl())
    #     peer_4 = (ip4, port, Protocol_Constant.NODE_NETWORK, time_to_crawl.time_to_crawl())
    #     peer_5 = (ip5, port, Protocol_Constant.NODE_NETWORK, time_to_crawl.time_to_crawl())
    #
    #     a_blockchain = Blockchain_Manager(init_difficulty, PRIVATE_KEY)
    #     b_blockchain = Blockchain_Manager(init_difficulty, PRIVATE_KEY)
    #     c_blockchain = Blockchain_Manager(init_difficulty, PRIVATE_KEY)
    #
    #     a = Network_Manager(ip1, port, Protocol_Constant.NODE_NONE, "mainnet", [], a_blockchain)
    #
    #     b = Network_Manager(ip2, port, Protocol_Constant.NODE_NONE, "mainnet", [peer_1, peer_3, peer_4, peer_5],
    #                         b_blockchain)
    #
    #     c = Network_Manager(ip3, port, Protocol_Constant.NODE_NONE, "mainnet", [peer_1, peer_2, peer_4, peer_5],
    #                         c_blockchain)
    #
    #     a.start_listener_thread()
    #     b.start_listener_thread()
    #     c.start_listener_thread()
    #
    #     b.connect(peer_1[0], peer_1[1], peer_1[2], peer_1[3])
    #     c.connect(peer_2[0], peer_2[1], peer_2[2], peer_2[3])
    #
    #     start = time_to_crawl.time_to_crawl()
    #
    #     while time_to_crawl.time_to_crawl() - start < Network_Constant.HANDSHAKE_TIMEOUT + 1 \
    #             and not (a.get_nb_connection() != 1 and b.get_nb_connection() != 1 and c.get_nb_connection() != 1):
    #         continue
    #
    #     transaction = Transaction(("lol" + str(1)), "lol" + str(1 + 1), PRIVATE_KEY.public_key(), time_to_crawl.time_to_crawl())
    #     transaction.sign(PRIVATE_KEY)
    #     b_blockchain.add_transaction(transaction)
    #
    #     b.broadcast_transactions([transaction])
    #
    #     time_to_crawl.sleep(5)
    #
    #     a.join_listener_thread()
    #     b.join_listener_thread()
    #     c.join_listener_thread()
    #
    #     a.join_connections()
    #     b.join_connections()
    #     c.join_connections()
    #
    #     self.assertTrue(a_blockchain.getTransactionPool() == b_blockchain.getTransactionPool())
    #     self.assertTrue(b_blockchain.getTransactionPool() == c_blockchain.getTransactionPool())
    #
    # def test_tx_broadcast_relay(self):
    #     global PRIVATE_KEY
    #
    #     init_difficulty = 2
    #
    #     src_ip = socket.gethostbyname(socket.gethostname())
    #     tmp = src_ip.split(".")
    #     prefix = tmp[0] + "." + tmp[1] + "." + tmp[2] + "."
    #
    #     ip1 = prefix + "1"
    #     ip2 = prefix + "2"
    #     ip3 = prefix + "3"
    #     ip4 = prefix + "4"
    #     ip5 = prefix + "5"
    #
    #     port = 8333
    #
    #     peer_1 = (ip1, port, Protocol_Constant.NODE_NETWORK, time_to_crawl.time_to_crawl())
    #     peer_2 = (ip2, port, Protocol_Constant.NODE_NETWORK, time_to_crawl.time_to_crawl())
    #     peer_3 = (ip3, port, Protocol_Constant.NODE_NETWORK, time_to_crawl.time_to_crawl())
    #     peer_4 = (ip4, port, Protocol_Constant.NODE_NETWORK, time_to_crawl.time_to_crawl())
    #     peer_5 = (ip5, port, Protocol_Constant.NODE_NETWORK, time_to_crawl.time_to_crawl())
    #
    #     a_blockchain = Blockchain_Manager(init_difficulty, PRIVATE_KEY)
    #     b_blockchain = Blockchain_Manager(init_difficulty, PRIVATE_KEY)
    #     c_blockchain = Blockchain_Manager(init_difficulty, PRIVATE_KEY)
    #     d_blockchain = Blockchain_Manager(init_difficulty, PRIVATE_KEY)
    #
    #     a = Network_Manager(ip1, port, Protocol_Constant.NODE_NONE, "mainnet", [], a_blockchain)
    #
    #     b = Network_Manager(ip2, port, Protocol_Constant.NODE_NONE, "mainnet", [peer_1, peer_3, peer_4, peer_5],
    #                         b_blockchain)
    #
    #     c = Network_Manager(ip3, port, Protocol_Constant.NODE_NONE, "mainnet", [peer_1, peer_2, peer_4, peer_5],
    #                         c_blockchain)
    #
    #     d = Network_Manager(ip4, port, Protocol_Constant.NODE_NONE, "mainnet", [peer_1, peer_2],
    #                         d_blockchain)
    #
    #     a.start_listener_thread()
    #     b.start_listener_thread()
    #     c.start_listener_thread()
    #     d.start_listener_thread()
    #
    #     b.connect(peer_1[0], peer_1[1], peer_1[2], peer_1[3])
    #     c.connect(peer_2[0], peer_2[1], peer_2[2], peer_2[3])
    #     d.connect(peer_1[0], peer_1[1], peer_1[2], peer_1[3])
    #     d.connect(peer_2[0], peer_2[1], peer_2[2], peer_2[3])
    #
    #     start = time_to_crawl.time_to_crawl()
    #
    #     while time_to_crawl.time_to_crawl() - start < Network_Constant.HANDSHAKE_TIMEOUT + 1 \
    #             and not (a.get_nb_connection() != 1 and b.get_nb_connection() != 1 and c.get_nb_connection() != 1 and d.get_nb_connection() != 2):
    #         continue
    #
    #     transaction = Transaction(("lol" + str(1)), "lol" + str(1 + 1), PRIVATE_KEY.public_key(), time_to_crawl.time_to_crawl())
    #     transaction.sign(PRIVATE_KEY)
    #     c_blockchain.add_transaction(transaction)
    #
    #     c.broadcast_transactions([transaction])
    #
    #     time_to_crawl.sleep(5)
    #
    #     a.join_listener_thread()
    #     b.join_listener_thread()
    #     c.join_listener_thread()
    #     d.join_listener_thread()
    #
    #     a.join_connections()
    #     b.join_connections()
    #     c.join_connections()
    #     d.join_connections()
    #
    #     self.assertTrue(a_blockchain.getTransactionPool() == b_blockchain.getTransactionPool())
    #     self.assertTrue(b_blockchain.getTransactionPool() == c_blockchain.getTransactionPool())
    #     self.assertTrue(b_blockchain.getTransactionPool() == d_blockchain.getTransactionPool())
    #
    # def test_block_broadcast_neighbour(self):
    #     global PRIVATE_KEY
    #
    #     init_difficulty = 2
    #
    #     src_ip = socket.gethostbyname(socket.gethostname())
    #     tmp = src_ip.split(".")
    #     prefix = tmp[0] + "." + tmp[1] + "." + tmp[2] + "."
    #
    #     ip1 = prefix + "1"
    #     ip2 = prefix + "2"
    #     ip3 = prefix + "3"
    #     ip4 = prefix + "4"
    #     ip5 = prefix + "5"
    #
    #     port = 8333
    #
    #     peer_1 = (ip1, port, Protocol_Constant.NODE_NETWORK, time_to_crawl.time_to_crawl())
    #     peer_2 = (ip2, port, Protocol_Constant.NODE_NETWORK, time_to_crawl.time_to_crawl())
    #     peer_3 = (ip3, port, Protocol_Constant.NODE_NETWORK, time_to_crawl.time_to_crawl())
    #     peer_4 = (ip4, port, Protocol_Constant.NODE_NETWORK, time_to_crawl.time_to_crawl())
    #     peer_5 = (ip5, port, Protocol_Constant.NODE_NETWORK, time_to_crawl.time_to_crawl())
    #
    #     a_blockchain = Blockchain_Manager(init_difficulty, PRIVATE_KEY)
    #     b_blockchain = Blockchain_Manager(init_difficulty, PRIVATE_KEY)
    #     c_blockchain = Blockchain_Manager(init_difficulty, PRIVATE_KEY)
    #
    #     a = Network_Manager(ip1, port, Protocol_Constant.NODE_NONE, "mainnet", [], a_blockchain)
    #
    #     b = Network_Manager(ip2, port, Protocol_Constant.NODE_NONE, "mainnet", [peer_1, peer_3, peer_4, peer_5],
    #                         b_blockchain)
    #
    #     c = Network_Manager(ip3, port, Protocol_Constant.NODE_NONE, "mainnet", [peer_1, peer_2, peer_4, peer_5],
    #                         c_blockchain)
    #
    #     a.start_listener_thread()
    #     b.start_listener_thread()
    #     c.start_listener_thread()
    #
    #     b.connect(peer_1[0], peer_1[1], peer_1[2], peer_1[3])
    #     c.connect(peer_2[0], peer_2[1], peer_2[2], peer_2[3])
    #
    #     for i in range(20):
    #         transaction = Transaction(("lol" + str(i)), "lol" + str(i + 1), PRIVATE_KEY.public_key(), time_to_crawl.time_to_crawl())
    #         transaction.sign(PRIVATE_KEY)
    #         b_blockchain.add_transaction(transaction)
    #
    #     test_1, test_2, block1 = b_blockchain.mine()
    #
    #     if test_1 == "mined" and test_2 == "ok":
    #         start = time_to_crawl.time_to_crawl()
    #
    #         while time_to_crawl.time_to_crawl() - start < Network_Constant.HANDSHAKE_TIMEOUT + 1 \
    #                 and not (a.get_nb_connection() != 1 and b.get_nb_connection() != 1 \
    #                 and c.get_nb_connection() != 1):
    #             continue
    #
    #         b.broadcast_blocks([block1])
    #
    #         time_to_crawl.sleep(5)
    #
    #     a.join_listener_thread()
    #     b.join_listener_thread()
    #     c.join_listener_thread()
    #
    #     a.join_connections()
    #     b.join_connections()
    #     c.join_connections()
    #
    #     self.assertTrue(test_1 == "mined")
    #     self.assertTrue(test_2 == "ok")
    #
    #     self.assertTrue(a_blockchain.getBlockchain() == b_blockchain.getBlockchain())
    #     self.assertTrue(b_blockchain.getBlockchain() == c_blockchain.getBlockchain())
    #
    # def test_block_broadcast_relay(self):
    #     global PRIVATE_KEY
    #
    #     init_difficulty = 2
    #
    #     src_ip = socket.gethostbyname(socket.gethostname())
    #     tmp = src_ip.split(".")
    #     prefix = tmp[0] + "." + tmp[1] + "." + tmp[2] + "."
    #
    #     ip1 = prefix + "1"
    #     ip2 = prefix + "2"
    #     ip3 = prefix + "3"
    #     ip4 = prefix + "4"
    #     ip5 = prefix + "5"
    #
    #     port = 8333
    #
    #     peer_1 = (ip1, port, Protocol_Constant.NODE_NETWORK, time_to_crawl.time_to_crawl())
    #     peer_2 = (ip2, port, Protocol_Constant.NODE_NETWORK, time_to_crawl.time_to_crawl())
    #     peer_3 = (ip3, port, Protocol_Constant.NODE_NETWORK, time_to_crawl.time_to_crawl())
    #     peer_4 = (ip4, port, Protocol_Constant.NODE_NETWORK, time_to_crawl.time_to_crawl())
    #     peer_5 = (ip5, port, Protocol_Constant.NODE_NETWORK, time_to_crawl.time_to_crawl())
    #
    #     a_blockchain = Blockchain_Manager(init_difficulty, PRIVATE_KEY)
    #     b_blockchain = Blockchain_Manager(init_difficulty, PRIVATE_KEY)
    #     c_blockchain = Blockchain_Manager(init_difficulty, PRIVATE_KEY)
    #     d_blockchain = Blockchain_Manager(init_difficulty, PRIVATE_KEY)
    #
    #
    #     a = Network_Manager(ip1, port, Protocol_Constant.NODE_NONE, "mainnet", [], a_blockchain)
    #
    #     b = Network_Manager(ip2, port, Protocol_Constant.NODE_NONE, "mainnet", [peer_1, peer_3, peer_4, peer_5],
    #                         b_blockchain)
    #
    #     c = Network_Manager(ip3, port, Protocol_Constant.NODE_NONE, "mainnet", [peer_1, peer_2, peer_4, peer_5],
    #                         c_blockchain)
    #
    #     d = Network_Manager(ip4, port, Protocol_Constant.NODE_NONE, "mainnet", [peer_1, peer_2, peer_5],
    #                         d_blockchain)
    #
    #     a.start_listener_thread()
    #     b.start_listener_thread()
    #     c.start_listener_thread()
    #     d.start_listener_thread()
    #
    #     b.connect(peer_1[0], peer_1[1], peer_1[2], peer_1[3])
    #     c.connect(peer_2[0], peer_2[1], peer_2[2], peer_2[3])
    #     d.connect(peer_1[0], peer_1[1], peer_1[2], peer_1[3])
    #     d.connect(peer_2[0], peer_2[1], peer_2[2], peer_2[3])
    #
    #     for i in range(20):
    #         transaction = Transaction(("lol" + str(i)), "lol" + str(i + 1), PRIVATE_KEY.public_key(), time_to_crawl.time_to_crawl())
    #         transaction.sign(PRIVATE_KEY)
    #         c_blockchain.add_transaction(transaction)
    #
    #     test_1, test_2, block1 = c_blockchain.mine()
    #
    #     if test_1 == "mined" and test_2 == "ok":
    #         start = time_to_crawl.time_to_crawl()
    #
    #         while time_to_crawl.time_to_crawl() - start < Network_Constant.HANDSHAKE_TIMEOUT + 1 \
    #                 and not (a.get_nb_connection() != 1 and b.get_nb_connection() != 1 \
    #                 and c.get_nb_connection() != 1):
    #             continue
    #
    #         c.broadcast_blocks([block1])
    #
    #         time_to_crawl.sleep(5)
    #
    #     a.join_listener_thread()
    #     b.join_listener_thread()
    #     c.join_listener_thread()
    #     d.join_listener_thread()
    #
    #     a.join_connections()
    #     b.join_connections()
    #     c.join_connections()
    #     d.join_connections()
    #
    #     self.assertTrue(test_1 == "mined")
    #     self.assertTrue(test_2 == "ok")
    #
    #     self.assertTrue(a_blockchain.getBlockchain() == b_blockchain.getBlockchain())
    #     self.assertTrue(b_blockchain.getBlockchain() == c_blockchain.getBlockchain())
    #     self.assertTrue(b_blockchain.getTransactionPool() == d_blockchain.getTransactionPool())

    def test_getblockchain(self):
        global PRIVATE_KEY

        init_difficulty = 2

        src_ip = socket.gethostbyname(socket.gethostname())
        tmp = src_ip.split(".")
        prefix = tmp[0] + "." + tmp[1] + "." + tmp[2] + "."

        ip1 = prefix + "1"
        ip2 = prefix + "2"
        ip3 = prefix + "3"
        ip4 = prefix + "4"
        ip5 = prefix + "5"

        port = 8333

        peer_1 = (ip1, port, Protocol_Constant.NODE_NETWORK, time.time())
        peer_2 = (ip2, port, Protocol_Constant.NODE_NETWORK, time.time())
        peer_3 = (ip3, port, Protocol_Constant.NODE_NETWORK, time.time())
        peer_4 = (ip4, port, Protocol_Constant.NODE_NETWORK, time.time())
        peer_5 = (ip5, port, Protocol_Constant.NODE_NETWORK, time.time())

        a_blockchain = Blockchain_Manager(init_difficulty, PRIVATE_KEY)
        b_blockchain = Blockchain_Manager(init_difficulty, PRIVATE_KEY)
        c_blockchain = Blockchain_Manager(init_difficulty, PRIVATE_KEY)

        a = Network_Manager(ip1, port, Protocol_Constant.NODE_NONE, "mainnet", [], a_blockchain)

        b = Network_Manager(ip2, port, Protocol_Constant.NODE_NONE, "mainnet", [peer_1, peer_3, peer_4, peer_5],
                            b_blockchain)

        c = Network_Manager(ip3, port, Protocol_Constant.NODE_NONE, "mainnet", [peer_1, peer_2, peer_4, peer_5],
                            c_blockchain)

        a.start_listener_thread()
        b.start_listener_thread()

        b.connect(peer_1[0], peer_1[1], peer_1[2], peer_1[3])
        c.connect(peer_2[0], peer_2[1], peer_2[2], peer_2[3])

        for i in range(200):
            transaction = Transaction(("lol" + str(i)), "lol" + str(i + 1), PRIVATE_KEY.public_key(), time.time())
            transaction.sign(PRIVATE_KEY)

            c_blockchain.add_transaction(transaction)

        i = 0
        while i < 10:
            test_1, test_2, block1 = c_blockchain.mine()
            if not (test_1 == "mined" and test_2 == "ok"):
                break

            i = i + 1

        if i == 10:
            start = time.time()

            while time.time() - start < Network_Constant.HANDSHAKE_TIMEOUT + 1 \
                    and not (a.get_nb_connection() != 1 and b.get_nb_connection() != 1 and c.get_nb_connection() != 1):
                continue

            b.get_blockchain()

            time.sleep(10)

            a.get_blockchain()

            time.sleep(10)

        a.join_listener_thread()
        b.join_listener_thread()

        a.join_connections()
        b.join_connections()

        self.assertTrue(i == 10)

        self.assertTrue(a_blockchain.getBlockchain() == b_blockchain.getBlockchain())
        self.assertTrue(b_blockchain.getBlockchain() == c_blockchain.getBlockchain())

    def test_getTransactionPool(self):
        global PRIVATE_KEY

        init_difficulty = 2

        src_ip = socket.gethostbyname(socket.gethostname())
        tmp = src_ip.split(".")
        prefix = tmp[0] + "." + tmp[1] + "." + tmp[2] + "."

        ip1 = prefix + "1"
        ip2 = prefix + "2"
        ip3 = prefix + "3"
        ip4 = prefix + "4"
        ip5 = prefix + "5"

        port = 8333

        peer_1 = (ip1, port, Protocol_Constant.NODE_NETWORK, time.time())
        peer_2 = (ip2, port, Protocol_Constant.NODE_NETWORK, time.time())
        peer_3 = (ip3, port, Protocol_Constant.NODE_NETWORK, time.time())
        peer_4 = (ip4, port, Protocol_Constant.NODE_NETWORK, time.time())
        peer_5 = (ip5, port, Protocol_Constant.NODE_NETWORK, time.time())

        a_blockchain = Blockchain_Manager(init_difficulty, PRIVATE_KEY)
        b_blockchain = Blockchain_Manager(init_difficulty, PRIVATE_KEY)
        c_blockchain = Blockchain_Manager(init_difficulty, PRIVATE_KEY)

        a = Network_Manager(ip1, port, Protocol_Constant.NODE_NONE, "mainnet", [], a_blockchain)

        b = Network_Manager(ip2, port, Protocol_Constant.NODE_NONE, "mainnet", [peer_1, peer_3, peer_4, peer_5],
                            b_blockchain)

        c = Network_Manager(ip3, port, Protocol_Constant.NODE_NONE, "mainnet", [peer_1, peer_2, peer_4, peer_5],
                            c_blockchain)

        a.start_listener_thread()
        b.start_listener_thread()

        b.connect(peer_1[0], peer_1[1], peer_1[2], peer_1[3])
        c.connect(peer_2[0], peer_2[1], peer_2[2], peer_2[3])

        for i in range(100):
            transaction = Transaction(("lol" + str(i)), "lol" + str(i + 1), PRIVATE_KEY.public_key(), time.time())
            transaction.sign(PRIVATE_KEY)

            c_blockchain.add_transaction(transaction)

        start = time.time()

        while time.time() - start < Network_Constant.HANDSHAKE_TIMEOUT + 1 \
                and not (a.get_nb_connection() != 1 and b.get_nb_connection() != 1 and c.get_nb_connection() != 1):
            continue

        b.get_transaction_pool()

        time.sleep(10)

        a.get_transaction_pool()

        time.sleep(10)

        a.join_listener_thread()
        b.join_listener_thread()

        a.join_connections()
        b.join_connections()

        self.assertTrue(a_blockchain.getTransactionPool().getTransactionPool() == b_blockchain.getTransactionPool().getTransactionPool())
        self.assertTrue(b_blockchain.getTransactionPool().getTransactionPool() == c_blockchain.getTransactionPool().getTransactionPool())


if __name__ == '__main__':
    unittest.main()
