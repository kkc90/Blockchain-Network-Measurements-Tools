import unittest
import socket
import time

from context import *


class UnitTestNetwork(unittest.TestCase):

    def test_connection(self):
        src_ip = socket.gethostbyname(socket.gethostname())
        tmp = src_ip.split(".")
        prefix = tmp[0] + "." + tmp[1] + "." + tmp[2] + "."

        ip1 = prefix + "1"
        ip2 = prefix + "2"

        port = 8333

        peer_1 = (ip1, port, Protocol_Constant.NODE_NETWORK, time.time())

        a = Network_Manager(ip1, port, Protocol_Constant.NODE_NONE, "mainnet", [], None)
        b = Network_Manager(ip2, port, Protocol_Constant.NODE_NONE, "mainnet", [peer_1], None)

        a.start_listener_thread()
        b.start_listener_thread()

        b.connect(peer_1[0], peer_1[1], peer_1[2], peer_1[3])

        time.sleep(Network_Constant.HANDSHAKE_TIMEOUT + 1)

        test_1 = b.get_nb_connection()
        test_2 = a.get_nb_connection()

        a.join_listener_thread()
        b.join_listener_thread()

        a.join_connections()
        b.join_connections()

        self.assertTrue(test_1 == 1)
        self.assertTrue(test_2 == 1)

    def test_connection_to_peer_down(self):
        src_ip = socket.gethostbyname(socket.gethostname())
        tmp = src_ip.split(".")
        prefix = tmp[0] + "." + tmp[1] + "." + tmp[2] + "."

        ip1 = prefix + "1"
        ip2 = prefix + "2"
        ip3 = prefix + "3"

        port = 8333

        peer_3 = (ip3, port, Protocol_Constant.NODE_NETWORK, time.time())

        a = Network_Manager(ip1, port, Protocol_Constant.NODE_NONE, "mainnet", [], None)
        b = Network_Manager(ip2, port, Protocol_Constant.NODE_NONE, "mainnet", [peer_3], None)

        a.start_listener_thread()
        b.start_listener_thread()

        b.connect(peer_3[0], peer_3[1], peer_3[2], peer_3[3])

        time.sleep(Network_Constant.HANDSHAKE_TIMEOUT + 1)

        test_1 = b.get_nb_connection()
        test_2 = a.get_nb_connection()

        a.join_listener_thread()
        b.join_listener_thread()

        a.join_connections()
        b.join_connections()

        self.assertTrue(test_1 == 0)
        self.assertTrue(test_2 == 0)

    def test_peer_down(self):
        src_ip = socket.gethostbyname(socket.gethostname())
        tmp = src_ip.split(".")
        prefix = tmp[0] + "." + tmp[1] + "." + tmp[2] + "."

        ip1 = prefix + "1"
        ip2 = prefix + "2"

        port = 8333

        peer_1 = (ip1, port, Protocol_Constant.NODE_NETWORK, time.time())

        a = Network_Manager(ip1, port, Protocol_Constant.NODE_NONE, "mainnet", [], None)
        b = Network_Manager(ip2, port, Protocol_Constant.NODE_NONE, "mainnet", [peer_1], None)

        a.start_listener_thread()
        b.start_listener_thread()

        b.connect(peer_1[0], peer_1[1], peer_1[2], peer_1[3])

        time.sleep(Network_Constant.HANDSHAKE_TIMEOUT + 1)

        test_1 = b.get_nb_connection()
        test_2 = a.get_nb_connection()

        b.kill_connections()

        time.sleep(Network_Constant.SOCKET_TIMEOUT * 3 + Network_Constant.PING_TIMEOUT + 1)

        a.remove_dead_connection()
        b.remove_dead_connection()

        test_3 = b.get_nb_connection()
        test_4 = a.get_nb_connection()

        a.kill_connections()

        a.join_listener_thread()
        b.join_listener_thread()

        a.join_connections()
        b.join_connections()

        self.assertTrue(test_1 == 1)
        self.assertTrue(test_2 == 1)

        self.assertTrue(test_3 == 0)
        self.assertTrue(test_4 == 0)

    def test_getaddr_exchange(self):
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
        peer_3 = (ip3, port, Protocol_Constant.NODE_NETWORK, time.time())
        peer_4 = (ip4, port, Protocol_Constant.NODE_NETWORK, time.time())
        peer_5 = (ip5, port, Protocol_Constant.NODE_NETWORK, time.time())

        a = Network_Manager(ip1, port, Protocol_Constant.NODE_NONE, "mainnet", [], None)
        b = Network_Manager(ip2, port, Protocol_Constant.NODE_NONE, "mainnet", [peer_1, peer_3, peer_4, peer_5], None)

        a.start_listener_thread()
        b.start_listener_thread()

        b.connect(peer_1[0], peer_1[1], peer_1[2], peer_1[3])

        time.sleep(Network_Constant.HANDSHAKE_TIMEOUT + 1)

        test_1 = b.get_nb_connection()
        test_2 = a.get_nb_connection()

        test_3 = b.get_nb_peer_in_pool()
        test_4 = a.get_nb_peer_in_pool()

        a.get_peers()

        time.sleep(Network_Constant.SOCKET_TIMEOUT * 3 + Network_Constant.ADDR_TIMEOUT + 1)

        test_5 = b.get_nb_connection()
        test_6 = a.get_nb_connection()

        test_7 = b.get_nb_peer_in_pool()
        test_8 = a.get_nb_peer_in_pool()

        a.join_listener_thread()
        b.join_listener_thread()

        a.join_connections()
        b.join_connections()

        self.assertTrue(test_1 == 1)
        self.assertTrue(test_2 == 1)

        self.assertTrue(test_3 == 3)
        self.assertTrue(test_4 == 0)

        self.assertTrue(test_5 == 1)
        self.assertTrue(test_6 == 1)

        self.assertTrue(test_7 == 3)
        self.assertTrue(test_8 == 1)

    def test_getblock_exchange(self):
        pass


if __name__ == '__main__':
    unittest.main()
