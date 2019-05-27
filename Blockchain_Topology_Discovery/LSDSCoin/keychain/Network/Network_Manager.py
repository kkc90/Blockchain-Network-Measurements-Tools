import random
import shutil
import socket
import sys
import time
import traceback
import math
from threading import Thread, Event, Lock

from keychain.Network.P2P_Connection import P2P_Connection
from keychain.Network.Protocol import Protocol, Protocol_Constant
from keychain.Network.Protocol.Bitcoin_Messages import GetBlock_Message, Addr_Message, Inv_Message, MemPool_Message, \
    GetData_Message, GetAddr_Message
from keychain.Network.Util import *

COLUMNS, ROWS = shutil.get_terminal_size(fallback=(80, 24))


def print_there(x, y, text):
    global COLUMNS, ROWS
    empty_line = ""
    for i in range(0, COLUMNS):
        empty_line += " "

    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x + 1, 0, empty_line))
    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x + 1, y + 1, text))
    sys.stdout.flush()


PEERS_MANAGEMENT_LOCKER = Lock()


class Network_Manager(Thread):

    def __init__(self, src_ip, src_port, src_service, network, bootstrap, blockchain_manager, monitor=False,
                 grow_peer_number=True):
        Thread.__init__(self)

        """
                PEER INFORMATIONS
        """
        self._src_ip = src_ip
        self._src_port = src_port
        self._src_service = src_service
        self._network = network

        """
                PEER POOL INFORMATIONS
        """

        self._connections = dict()

        self._peers_pool = set(bootstrap)

        self._unactive_peers = dict()

        self._grow_peer_number = grow_peer_number

        """
                CONNECTION RECEPTION MANAGEMENT 
        """

        addr_type = Protocol.get_ip_type(self._src_ip)

        if addr_type == "ipv4":
            self._listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        elif addr_type == "ipv6":
            self._listener_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

        self._listener_socket.settimeout(Network_Constant.SOCKET_TIMEOUT)

        self._listener_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._listener_socket.bind((self._src_ip, self._src_port))

        self._listener_thread = Thread(target=self.listener_thread, args=())

        """
                BLOCKCHAIN MANAGEMENT
        """

        self._blockchain_manager = blockchain_manager

        self.block_asked = False

        self.block_asked_list = dict()

        """
                MONITORING MANAGEMENT
        """

        self._monitor = monitor

        """
                THREAD MANAGEMENT
        """

        self.__stop_event = Event()

        """
                ERROR MANAGEMENT
        """

        self._traceback_list = list()
    """
            GETTERS
    """

    def monitorIsTrue(self):
        return self._monitor

    def get_nb_connection(self):
        return len(self._connections)

    def get_connected_peers(self):
        connected_peers = list()

        for peer_info, connection in self._connections.copy().items():
            connected_peers.append(peer_info[0])

        return connected_peers
    """
            THREAD MANAGEMENT
    """

    def run(self):
        if self._monitor is True:
            self.display_info("Network Manager is starting ...", 6)

        try:

            self._listener_thread.start()

            start = time.time()

            while not self.__stop_event.isSet():

                nb_connection_missing = Network_Constant.MIN_NUMBER_OF_CONNECTION - len(self._connections)

                # Check if enough connection are alive
                if (time.time() - start) > Network_Constant.TIMEOUT_RETRY_ASK_NEW_PEER and nb_connection_missing > 0 \
                        and self._grow_peer_number is True:

                    self.put_back_unactive_in_pool(Network_Constant.TIMEOUT_RETRY_UNACTIVE_PEER)

                    # Check if enough peer to connect to in the pool
                    if len(self._peers_pool) < nb_connection_missing:
                        self.query_peers()

                    self.connect_to_peers(nb_connection_missing)

                    start = time.time()

                self.remove_dead_peers()
                self.remove_dead_block_queries()

        except Exception:
            self.error_recording()
            self.kill()

    def kill(self):
        self.__stop_event.set()

        for connection in self._connections.values():
            connection.kill()

    def join(self, **kwargs):
        self.__stop_event.set()

        self._listener_thread.join()

        for connection in self._connections.values():
            connection.join()

        Thread.join(self)

    def kill_connections(self):
        self.__stop_event.set()

        for connection in self._connections.values():
            connection.kill()

    def join_connections(self):
        for connection in self._connections.values():
            connection.join()

    def kill_listener_thread(self):
        self.__stop_event.set()

    def join_listener_thread(self):
        self.__stop_event.set()

        self._listener_thread.join()

    def is_alive(self) -> bool:
        return not self.__stop_event.is_set()

    """
            INCOMING CONNECTION QUERIES MANAGEMENT
    """

    def listener_thread(self):
        try:
            while not self.__stop_event.isSet():
                self.listen()

        except Exception:
            self.error_recording()
            self.kill()

        self.__stop_event.set()

        self._listener_socket.close()

    def listen(self):
        global PEERS_MANAGEMENT_LOCKER
        connection = None

        try:
            self._listener_socket.listen(0)

            (peer_socket, (node_ip, node_port)) = self._listener_socket.accept()

            peer_socket.settimeout(Network_Constant.SOCKET_TIMEOUT)

            peer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            connection = P2P_Connection(self._src_ip, self._src_port, self._src_service, node_ip, node_port,
                                        Protocol_Constant.NODE_NETWORK, peer_socket, self._network, self)

            connection.start()

            connection.wait_for_handshake()

            PEERS_MANAGEMENT_LOCKER.acquire()

            self._connections[(node_ip, node_port, connection.get_node_service(), connection.get_handshake_time())] \
                = connection

            for ip, port, service, timestamp in self._unactive_peers.keys():
                if node_ip == ip:
                    del self._unactive_peers[(ip, port, service, timestamp)]
                    break

            PEERS_MANAGEMENT_LOCKER.release()

        except socket.timeout:
            if connection is not None:
                connection.join()

        except HandShakeFailureException:
            if connection is not None:
                connection.join()

    """
            PEERS MANAGEMENT
    """

    def connect(self, node_ip, node_port, node_service, node_timestamp):
        peer_socket = None
        connection = None
        # self.display_info(("Connection to " + str(node_ip) + " - " + str(node_port)))

        try:
            peer_socket = self.create_socket(node_ip, node_port)

            connection = P2P_Connection(self._src_ip, self._src_port, self._src_service, node_ip, node_port,
                                        node_service, peer_socket, self._network, self)

            connection.start()

            connection.bitcoin_handshake()

            self._connections[(node_ip, node_port, node_service, connection.get_handshake_time())] = connection

            self.query_peers(connection)

        except ConnectionException:
            if connection is not None:
                connection.join()

            if peer_socket is not None:
                peer_socket.close()

            self._unactive_peers[(node_ip, node_port, node_service, node_timestamp)] = time.time()

        if self._monitor is True:
            self.display_info(("Connected to " + str(len(self._connections)) + " peer, "
                               + str(len(self._unactive_peers)) + " unactive peers, "
                               + str(len(self._peers_pool)) + " peers in the pool."), 7)

        self._peers_pool.remove((node_ip, node_port, node_service, node_timestamp))

    def create_socket(self, node_ip, node_port):

        try:
            addr_type = Protocol.get_ip_type(node_ip)

        except Protocol.UnknownIPAddressTypeException:
            raise ConnectionException("The IP Address provided is neither a valid IPv6 nor a valid IPv4 Address")

        socket_node = None

        if addr_type == "ipv4":
            socket_node = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        elif addr_type == "ipv6":
            socket_node = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

        socket_node.settimeout(Network_Constant.SOCKET_TIMEOUT)

        socket_node.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        socket_node.bind((self._src_ip, 0))

        try:
            if addr_type == "ipv4":
                socket_node.connect((node_ip, node_port))
            elif addr_type == "ipv6":
                socket_node.connect((node_ip, node_port, 0, 0))

        except socket.timeout as err:
            socket_node.close()
            raise SocketTimeoutException(str(err))
        except socket.error as err:
            socket_node.close()
            raise BrokenSocketException(str(err))

        return socket_node

    def is_known(self, ip, port, service, timestamp):
        if ((ip, port, service, timestamp) in self._peers_pool) \
                or ((ip, port, service, timestamp) in self._connections.copy()) \
                or ((ip, port, service, timestamp) in self._unactive_peers):
            return True
        else:
            return False

    def put_back_unactive_in_pool(self, timeout):
        nb_unactive = len(self._unactive_peers)
        if nb_unactive > 0:
            ordered_connections = sorted(self._unactive_peers, key=self._unactive_peers.get)

            if time.time() - self._unactive_peers[ordered_connections[0]] > timeout:

                i = 0
                while i < nb_unactive and time.time() - self._unactive_peers[ordered_connections[i]] > timeout \
                        and not self.__stop_event.is_set():
                    self._unactive_peers.pop(ordered_connections[i])

                    self._peers_pool.add(ordered_connections[i])

                    i = i + 1

        if self._monitor is True:
            self.display_info(("Connected to " + str(len(self._connections)) + " peer, "
                               + str(len(self._unactive_peers)) + " unactive peers, "
                               + str(len(self._peers_pool)) + " peers in the pool."), 7)

    def remove_dead_peers(self):
        # Check if all connections are still alive
        for node_ip, node_port, node_service, node_timestamp in self._connections.copy():
            if not self._connections[(node_ip, node_port, node_service, node_timestamp)].isAlive():
                self._connections.pop((node_ip, node_port, node_service, node_timestamp))

                self._unactive_peers[(node_ip, node_port, node_service, node_timestamp)] = time.time()

        if self._monitor is True:
            self.display_info(("Connected to " + str(len(self._connections)) + " peer, "
                               + str(len(self._unactive_peers)) + " unactive peers, "
                               + str(len(self._peers_pool)) + " peers in the pool."), 7)

    def connect_to_peers(self, nb_connection_missing=math.inf):
        # Connect to the peer in the pool
        i = 0
        while i < nb_connection_missing and len(self._peers_pool) > 0 and not self.__stop_event.is_set():
            node_ip, node_port, node_service, node_timestamp = next(iter(self._peers_pool))

            self.connect(node_ip, node_port, node_service, node_timestamp)

            i = i + 1

    def query_peers(self, connection=None):
        getaddr_msg = GetAddr_Message.GetAddr_Message()

        if connection is None:
            self.broadcast(getaddr_msg)
        else:
            self.send(connection, getaddr_msg)

    def remove_dead_block_queries(self):
        for block_hash, timestamp in self.block_asked_list.copy().items():
            if time.time() - timestamp > Network_Constant.QUERY_TIMEOUT:
                del self.block_asked_list[block_hash]

    def add_peer_to_pool(self, peer_list):
        for ip, (port, service, timestamp) in peer_list.items():
            if not self.is_known(ip, port, service, timestamp):
                self._peers_pool.add((ip, port, service, timestamp))

        if self._monitor is True:
            self.display_info(("Connected to " + str(len(self._connections)) + " peer, "
                               + str(len(self._unactive_peers)) + " unactive peers, "
                               + str(len(self._peers_pool)) + " peers in the pool."), 7)

    def send_peers(self, connection):
        all_peers = set.union(self._peers_pool, set(self._unactive_peers.keys()), set(self._connections.keys()))

        # Remove the IP of the peer that ask for peers.
        ip, port, service, timestamp = connection.get_node_info()

        if (ip, port, service, timestamp) not in all_peers:
            raise BrokenConnectionException("BrokenConnection Exception : "
                                            "The peer is not considered as active anymore.")

        all_peers.remove((ip, port, service, timestamp))

        nb_peers_to_send = int(len(all_peers) / 10) + 1

        if nb_peers_to_send > 1000:
            tmp = random.sample(all_peers, 1000)
        elif len(all_peers) > nb_peers_to_send:
            tmp = random.sample(all_peers, nb_peers_to_send)
        else:
            return

        if len(tmp) > 0:
            peers_to_send = dict()
            for node_ip, node_port, node_service, node_timestamp in tmp:
                peers_to_send[node_ip] = (node_port, node_service, node_timestamp)

            addr_msg = Addr_Message.Addr_Message(peers_to_send)

            self.send(connection, addr_msg)

    """
            INV MESSAGE TREATMENT
    """

    def get_interesting_blocks_hash(self, block_hashes):

        interesting_block_hashes = set()

        for block_hash in block_hashes:
            if not self._blockchain_manager.isBlockHashKnown(block_hash):
                interesting_block_hashes.add(block_hash)

        return interesting_block_hashes

    def get_interesting_tx_hash(self, tx_hashes):
        interesting_tx_hashes = set()

        for tx_hash in tx_hashes:
            if not self._blockchain_manager.isTransactionHashKnown(tx_hash):
                interesting_tx_hashes.add(tx_hash)

        return interesting_tx_hashes

    def treat_inv_packet(self, connection, inv_msg, inv_msg_size):

        block_hashes, tx_hashes = inv_msg.get_available_objects()

        interesting_block_hashes = self.get_interesting_blocks_hash(block_hashes)
        interesting_tx_hashes = self.get_interesting_tx_hash(tx_hashes)

        inv_list = list()

        for block_hash in interesting_block_hashes:

            # Not to query two time_to_crawl the same block.
            if block_hash not in self.block_asked_list:
                inv_list.append((Protocol_Constant.INV_VECTOR_MSG_BLOCK, block_hash))
                connection.request_data(("block", block_hash))

                self.block_asked_list[block_hash] = time.time()

        for tx_hash in interesting_tx_hashes:
            inv_list.append((Protocol_Constant.INV_VECTOR_MSG_TX, tx_hash))
            connection.request_data(("tx", tx_hash))

        getdata_msg = GetData_Message.GetData_Message(inv_list)

        self.send(connection, getdata_msg)

        self.block_asked = False

    """
            GETDATA MESSAGE TREATMENT
    """

    def send_data(self, connection, tx_hashes, block_hashes):

        if self._monitor is True:
            self.display_info(("Sending " + str(len(tx_hashes)) + " transactions and " + str(len(block_hashes))
                               + " blocks to " + connection.get_node_info()[0] + "..."), 6)

        for tx_hash in tx_hashes:
            transaction = self._blockchain_manager.getTransactionFromHash(tx_hash)

            if transaction is not None:
                tx_msg = transaction_to_tx_message(transaction)

                self.send(connection, tx_msg)

        blocks = list()

        for block_hash in block_hashes:
            block = self._blockchain_manager.getBlockFromHash(block_hash)

            if block is not None:
                blocks.append(block)

        for block in sorted(blocks):
            block_msg = block_to_block_message(block)

            self.send(connection, block_msg)

    """
            TX MESSAGE TREATMENT
    """

    def treat_tx_message(self, connection, tx_msg, tx_msg_size):

        if self._monitor is True:
            self.display_info(("Tx Message Received from " + connection.get_node_info()[0] + "."), 6)

        transaction = tx_message_to_transaction(tx_msg)

        self._blockchain_manager.add_transaction(transaction)

        if self._monitor is True:
            self._blockchain_manager.log_transaction_pool(self._src_ip)

        data_requested = connection.get_data_requested()

        if ("tx", transaction.__hash__()) in data_requested:
            connection.remove_data_requested("tx", transaction.__hash__())

        else:
            self.relay_transactions([transaction], except_info=[connection.get_node_info()[0]])

    def get_transaction_pool(self):
        if self._monitor is True:
            self.display_info("Querying Transaction Pool ...", 6)

        mempool_msg = MemPool_Message.MemPool_Message()

        self.broadcast(mempool_msg)

        if self._monitor is True:
            self.display_info("Transaction Pool queried.", 6)

    def treat_mempool(self, connection, mempool_msg):
        transaction_pool_hashes = self._blockchain_manager.getTransactionPool().getTransactionPoolHashes()

        inv_list = list()

        i = 0
        for transaction_hashes in transaction_pool_hashes:
            if i > Network_Constant.MAX_NUMBER_OF_OBJECT_IN_INV_MESSAGE:
                break

            inv_list.append((Protocol_Constant.INV_VECTOR_MSG_TX, transaction_hashes))

            i = i + 1

        inv_msg = Inv_Message.Inv_Message(inv_list)

        self.send(connection, inv_msg)

    """
            BLOCK MESSAGE TREATMENT
    """

    def treat_block_message(self, connection, block_msg, block_msg_size):

        if self._monitor is True:
            self.display_info(("Block Message Received from " + connection.get_node_info()[0] + "."), 6)

        block = block_message_to_block(block_msg)

        ret = self._blockchain_manager.add_block(block)

        if block.getBlockHash() in self.block_asked_list:
            # Ask for removing this block of the queried blocks (already received)
            self.block_asked_list[block.getBlockHash()] = time.time() - 2 * Network_Constant.QUERY_TIMEOUT

        if ret == "invalid block index":
            self.get_blockchain(connection, block=False)

        if self._monitor is True:
            self._blockchain_manager.log_blockchain(self._src_ip)

        data_requested = connection.get_data_requested()

        if ("block", block.getBlockHash()) in data_requested:
            connection.remove_data_requested("block", block.getBlockHash())

        else:
            self.relay_blocks([block], except_info=[connection.get_node_info()[0]])

    def get_blockchain(self, connection=None, block=True):

        if self._monitor is True:
            self.display_info("Querying Blockchain ...", 6)

        block_locator_list = self.get_block_locator()

        version = Network_Constant.PROTOCOL_VERSION

        getblock_msg = GetBlock_Message.GetBlock_Message(version, block_locator_list)

        if connection is None:
            for co in self._connections.values():
                self.send(co, getblock_msg)

        else:
            self.send(connection, getblock_msg)

        if len(self._connections) > 0 or connection is not None:
            self.block_asked = True

            while not self.__stop_event.isSet() and block is True \
                    and ((self.block_asked is True) or (len(self.block_asked_list) > 0)):
                continue

        if self._monitor is True:
            self.display_info("Blockchain queried.", 6)

    def get_block_locator(self):
        block_locator = list()
        blocks = self._blockchain_manager.getBlockchain().getBlocks()

        i = 0
        while i < len(blocks):
            block_hash = blocks[i].getBlockHash()

            block_locator.append(block_hash)

            if i < 10:
                i = i + 1
            else:
                i = i * 2

        block_locator.reverse()

        return block_locator

    def get_block_from_block_locator(self, block_locators, hash_stop):
        blockchain = self._blockchain_manager.getBlockchain()

        init_block = None
        for block_locator in block_locators:
            if blockchain.containsBlock(block_locator):
                init_block = blockchain.getBlockFromHash(block_locator)

        blocks = list()
        if init_block is not None:
            i = init_block.getIndex()

            block_hash = init_block.getBlockHash()

            i = i + 1

            while i < blockchain.length() and block_hash != hash_stop:
                block = blockchain.getBlock(i)

                blocks.append(block)

                block_hash = block.getBlockHash()

                i = i + 1

        return blocks

    def treat_getblock(self, connection, getblock_msg):

        if self._monitor is True:
            self.display_info(("GetBlock Message Received from " + connection.get_node_info()[0] + "."), 6)

        block_locator = getblock_msg.get_block_locator_list()
        hash_stop = getblock_msg.get_hash_stop()

        blocks = self.get_block_from_block_locator(block_locator, hash_stop)

        self.relay_blocks_to_peer(connection, blocks)

    """
            GETHEADER MESSAGE TREATMENT
    """

    def get_header(self, connection):
        pass

    def treat_getheader(self, connection, getheader_msg):
        pass

    """
            BROADCAST OR RELAY OF MINED BLOCKS
    """

    def broadcast_blocks(self, blocks):
        if self._monitor is True:
            self.display_info("Broadcast of blocks.", 6)

        for block in sorted(blocks):
            block_msg = block_to_block_message(block)

            self.broadcast(block_msg)

    def relay_blocks(self, blocks, except_info=None):

        if self._monitor is True:
            self.display_info("Relay of blocks.", 6)

        inv_list = list()

        for block in sorted(blocks):
            inv_list.append((Protocol_Constant.INV_VECTOR_MSG_BLOCK, block.getBlockHash()))

        inv_msg = Inv_Message.Inv_Message(inv_list)

        self.broadcast(inv_msg, except_info=except_info)

    def relay_blocks_to_peer(self, connection, blocks):
        inv_list = list()

        for block in sorted(blocks):
            inv_list.append((Protocol_Constant.INV_VECTOR_MSG_BLOCK, block.getBlockHash()))

        inv_msg = Inv_Message.Inv_Message(inv_list)

        self.send(connection, inv_msg)

    def send_blocks(self, connection, blocks):

        if self._monitor is True:
            self.display_info(("Sending Blocks to " + connection.get_node_info()[0] + "."), 6)

        for block in sorted(blocks):
            block_msg = block_to_block_message(block)

            self.send(connection, block_msg)

    """
            BROADCAST OR RELAY OF TRANSACTIONS
    """

    def broadcast_transactions(self, transactions):

        if self._monitor is True:
            self.display_info("Broadcast of Transactions.", 6)

        for transaction in transactions:
            tx_msg = transaction_to_tx_message(transaction)

            self.broadcast(tx_msg)

    def relay_transactions(self, transactions, except_info=None):

        if self._monitor is True:
            self.display_info("Relay of Transactions.", 6)

        inv_list = list()

        for transaction in transactions:
            inv_list.append((Protocol_Constant.INV_VECTOR_MSG_TX, transaction.__hash__()))

        inv_msg = Inv_Message.Inv_Message(inv_list)

        self.broadcast(inv_msg, except_info=except_info)

    def relay_transactions_to_peer(self, connection, transactions):

        if self._monitor is True:
            self.display_info("Relay of Transactions.", 6)

        inv_list = list()

        for transaction in transactions:
            inv_list.append((Protocol_Constant.INV_VECTOR_MSG_TX, transaction.__hash__()))

        inv_msg = Inv_Message.Inv_Message(inv_list)

        self.send(connection, inv_msg)

    def send_transactions(self, connection, transactions):
        if self._monitor is True:
            self.display_info(("Sending Transactions to " + connection.get_node_info()[0] + "."), 6)

        for transaction in transactions:
            tx_msg = transaction_to_tx_message(transaction)

            self.send(connection, tx_msg)

    """
            GENERAL MESSAGE MANAGEMENT
    """

    def send(self, connection, msg):
        if connection.is_handshake_done() and connection.isAlive():
            connection.send_msg(msg)

    def broadcast(self, msg, except_info=None):
        for peer_info, connection in self._connections.copy().items():
            if not (except_info is not None and peer_info[0] in except_info) \
                    and connection.is_handshake_done() and connection.isAlive():
                connection.send_msg(msg)
    """
            MONITORING MANAGEMENT
    """

    def get_round_trip_time(self, connection=None):
        if connection is None:
            round_trip_time = dict()

            peers = self._connections.copy()

            for peer_info, connection in peers.items():
                connection.ask_alive(block=True)

            for peer_info, connection in peers.items():
                ret = None

                while ret is None and not self.__stop_event.is_set():
                    ret = connection.get_last_round_trip_time()

                round_trip_time[peer_info[0]] = ret

                return round_trip_time
        else:
            connection.ask_alive(block=True)

            ret = None

            while ret is None and not self.__stop_event.is_set():
                ret = connection.get_last_round_trip_time()

            return ret

    def display_info(self, text, x):
        print_there(x, 0, ("Network Manager " + self._src_ip + " : " + str(text)))

    def error_recording(self):
        directory = "Log/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        directory = "Log/Log_Peer_" + self._src_ip + "/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        stdout = open(("Log/Log_Peer_" + self._src_ip + "/Network_Manager_Log.txt"), "a")

        ex_type, ex, tb = sys.exc_info()
        traceback.print_exception(ex_type, ex, tb, file=stdout)
        stdout.write('\n\n')

        stdout.close()

        self._traceback_list.append((ex_type, ex, tb))

    def get_tracebacks(self):
        return self._traceback_list
