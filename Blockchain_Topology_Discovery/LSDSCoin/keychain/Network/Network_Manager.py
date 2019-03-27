from .NetworkException import *
from .Network_Constant import *
from .P2P_Connection import *
from .Protocol import *
from .Protocol.Bitcoin_Messages import *


class Network_Manager(Thread):
    def __init__(self, src_ip, src_port, src_service, network, bootstrap, blockchain_manager):
        Thread.__init__(self)

        self._network = network

        self._src_ip = src_ip
        self._src_port = src_port

        self._src_service = src_service

        self.__stop_event = Event()

        self._connections = dict()

        self._peers_pool = set(bootstrap)

        self._unactive_peers = dict()

        self._listener_socket = None

        self._listener_thread = None

        self._blockchain_manager = blockchain_manager

    def run(self):
        try:
            self.start_listener_thread()

            # Connection to the boostrap nodes.
            for node_ip, node_port, node_service, node_timestamp in self._peers_pool.copy():
                self.connect(node_ip, node_port, node_service, node_timestamp)

            while not self.__stop_event.isSet():
                nb_connection_missing = Network_Constant.MIN_NUMBER_OF_CONNECTION - len(self._connections)

                # Check if enough connection are alive
                if nb_connection_missing > 0:
                    self.put_back_unactive(Network_Constant.TIMEOUT_RETRY_UNACTIVE_PEER)

                    # Check if enough peer to connect to in the pool
                    if len(self._peers_pool) < nb_connection_missing:
                        self.get_peers()

                    self.add_more_active_connection(nb_connection_missing)

                self.remove_dead_connection()

        except Exception as err:
            self.display_info(("Unexpected Failure - " + str(err)))
            traceback.print_exc()
            self.error_recording()

    def start_listener_thread(self):
        addr_type = Protocol.get_ip_type(self._src_ip)

        if addr_type == "ipv4":
            self._listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        elif addr_type == "ipv6":
            self._listener_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

        self._listener_socket.settimeout(Network_Constant.SOCKET_TIMEOUT)

        self._listener_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._listener_socket.bind((self._src_ip, self._src_port))

        self._listener_thread = Thread(target=self.listen, args=())

        self._listener_thread.start()

    def listen(self):
        try:
            while not self.__stop_event.isSet():
                try:
                    self._listener_socket.listen(0)

                    (peer_socket, (node_ip, node_port)) = self._listener_socket.accept()

                    peer_socket.settimeout(Network_Constant.SOCKET_TIMEOUT)

                    peer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                    connection = P2P_Connection(self._src_ip, self._src_port, self._src_service, node_ip, node_port,
                                                None, peer_socket, self._network, self, self._blockchain_manager)

                    connection.start()

                    connection.wait_for_handshake()

                    node_service = connection.get_node_service()

                    self._connections[(node_ip, node_port, node_service, time.time())] = connection
                except socket.timeout:
                    continue

        except Exception as err:
            self.display_info(("Unexpected Failure - " + str(err)))
            traceback.print_exc()
            self.error_recording()

        self._listener_socket.close()

    def get_connection(self):
        return self._connections

    def get_nb_connection(self):
        return len(self._connections)

    def get_peer_pool(self):
        return self._peers_pool

    def get_nb_peer_in_pool(self):
        return len(self._peers_pool)

    def put_back_unactive(self, timeout):
        nb_unactive = len(self._unactive_peers)
        if nb_unactive > 0:
            ordered_connections = sorted(self._unactive_peers, key=self._unactive_peers.get)

            if time.time() - self._unactive_peers[ordered_connections[0]] > timeout:

                i = 0
                while i < nb_unactive and time.time() - self._unactive_peers[ordered_connections[i]] > timeout:
                    self._unactive_peers.pop(ordered_connections[i])

                    self._peers_pool.add(ordered_connections[i])

                    i = i + 1

    def remove_dead_connection(self):
        # Check if all connections are still alive
        for node_ip, node_port, node_service, node_timestamp in self._connections.copy():
            if not self._connections[(node_ip, node_port, node_service, node_timestamp)].isAlive():
                ip, port, service = self._connections[
                    (node_ip, node_port, node_service, node_timestamp)].get_node_info()

                self._connections.pop((node_ip, node_port, node_service, node_timestamp))

                self._unactive_peers[(ip, port, service, node_timestamp)] = time.time()

    def add_more_active_connection(self, nb_connection_missing):
        # Connect to the peer in the pool
        i = 0
        while i < nb_connection_missing and len(self._peers_pool) > 0:
            node_ip, node_port, node_service, node_timestamp = next(iter(self._peers_pool))

            self.connect(node_ip, node_port, node_service, node_timestamp)

            i = i + 1

    def get_peers(self):
        connections = self._connections.items()
        for peer_info, connection in connections:

            if connection.is_handshake_done() and connection.isAlive():

                try:
                    connection.ask_for_peers()

                except SendMessageTimeoutException as err:
                    self.display_info(str(err))

                except BrokenConnectionException as err:
                    connection.kill()
                    self.display_info(str(err))

    def add_peer_to_pool(self, peer_list):
        for ip, (port, service, timestamp) in peer_list.items():
            if not self.is_known(ip, port, service, timestamp):
                self._peers_pool.add((ip, port, service, timestamp))

    def send_peers(self, connection):

        all_peers = set.union(self._peers_pool, set(self._unactive_peers.keys()), set(self._connections.keys()))

        nb_peers_to_send = int(len(all_peers) / 10 + 1)

        if nb_peers_to_send > 1000:
            tmp = random.sample(all_peers, 1000)
        else:
            tmp = random.sample(all_peers, nb_peers_to_send)

        peers_to_send = dict()
        for node_ip, node_port, node_service, node_timestamp in tmp:
            peers_to_send[node_ip] = (node_port, node_service, node_timestamp)

        addr_msg = Addr_Message.Addr_Message(peers_to_send)

        connection.send_msg(addr_msg)

    def broadcast_blocks(self, blocks):
        inv_list = list()
        type = Protocol_Constant.INV_VECTOR_MSG_BLOCK

        for block in blocks:
            inv_list.append((type, block.getBlockHash()))

    def broadcast_transactions(self, transactions):
        inv_list = list()
        type = Protocol_Constant.INV_VECTOR_MSG_TX

        for transaction in transactions:
            inv_list.append((type, transaction.__hash__()))

    def is_known(self, ip, port, service, timestamp):
        if ((ip, port, service, timestamp) in self._peers_pool) \
                or ((ip, port, service, timestamp) in self._connections) \
                or ((ip, port, service, timestamp) in self._unactive_peers):
            return True
        else:
            return False

    def connect(self, node_ip, node_port, node_service, node_timestamp):
        peer_socket = None
        # self.display_info(("Connection to " + str(node_ip) + " - " + str(node_port)))

        try:
            peer_socket = self.create_socket(node_ip, node_port)

            connection = P2P_Connection(self._src_ip, self._src_port, self._src_service, node_ip, node_port,
                                        node_service, peer_socket, self._network, self, self._blockchain_manager)

            connection.start()

            connection.bitcoin_handshake()

            timestamp = time.time()

            self._connections[(node_ip, node_port, node_service, timestamp)] = connection

        except ConnectionException as err:
            # self.display_info(("Fail to connect to " + str(node_ip) + " : " + str(err)))

            if peer_socket is not None:
                peer_socket.close()

            self._unactive_peers[(node_ip, node_port, node_service, node_timestamp)] = time.time()

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

    def kill(self):
        self.__stop_event.set()

        for connection in self._connections.values():
            connection.kill()

        self._listener_thread.kill()

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

    def display_info(self, msg):
        print("Network Manager ", self._src_ip, " : ", msg)

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
