import socket
import ipaddress
import random
import time
import subprocess

from Protocol import Protocol
from Protocol.Bitcoin_Messages import *

from CrawlingException import *


class P2P_Connection:
    ORIGIN_NETWORK = 'mainnet'
    PROTOCOL_VERSION = 70015
    SERVICE_PROVIDED = Protocol.NODE_NONE

    # Timeouts
    CONNECTION_TIMEOUT = 1 / 2
    SOCKET_TIMEOUT = 1
    PING_TIMEOUT = 5
    ADDR_TIMEOUT = 20  # longuer because bigger packets
    HANDSHAKE_TIMEOUT = 1

    # Number of Attempts
    CONNECTION_MAX_ATTEMPTS = 2
    ADDR_QUERY_MAX_ATTEMPTS = 2
    ASK_ALIVE_MAX_ATTEMPTS = 3

    def __init__(self, target_service, node_ip, node_port, src_port, src_ip, measurements_manager, thread_nb, displayer,
                 sender, receiver):
        self.node_ip = node_ip
        self.node_port = node_port
        self.src_port = src_port
        self.src_ip = src_ip
        self.target_service = target_service

        self.measurements_manager = measurements_manager

        self.our_connection_nonce = float(
            "nan")  # By sending this nonce in a Version packet, you will end the communication between the two peers
        self.peer_connection_nonce = float(
            "nan")  # By receiving this nonce in a Version packet, you will end the communication between the two peers

        self.pong_nonce = []
        self.error = []
        self.thread_nb = thread_nb
        self.displayer = displayer

        self.connected = False
        self.continue_to_ask = True

        self.sender = sender
        self.receiver = receiver

        self.nb_peer_queried = -1

        self.tracebacks = []

        # self.calibrate_timeouts(1) # Takes a lot of computing time

    def crawl_ip(self):
        nb_attempts = 0

        while nb_attempts < self.CONNECTION_MAX_ATTEMPTS:
            self.display_progression(("Connection to " + self.node_ip + ":" + str(self.node_port) + " (attempts " + str(
                nb_attempts) + ") ..."))

            try:
                self.connect_to_peer(self.node_ip, self.node_port, self.CONNECTION_TIMEOUT)
                self.measurements_manager.add_active_peer(self.node_ip)
                self.connected = True
                self.nb_peer_queried = 0
                break

            # Expected Connection Exceptions
            except ConnectionException as err:
                # Displaying that the Connection Failed for the "nb_attempts" number of time
                self.display_progression(
                    "Connection Exception : Fail to connect to the peer (attempt " + str(nb_attempts + 1) + ")")

                if nb_attempts == (self.CONNECTION_MAX_ATTEMPTS - 1):
                    self.display_progression("Connection Exception : Fail to connect to the peer (" + str(
                        self.CONNECTION_MAX_ATTEMPTS) + " attempts to connect)")
                    self.measurements_manager.add_connection_failed_stat(repr(err))
                    break

                nb_attempts = nb_attempts + 1
                continue

        nb_attempts = 0

        while self.connected and self.continue_to_ask and nb_attempts < self.ADDR_QUERY_MAX_ATTEMPTS:
            try:
                self.ask_alive()
            except PeerQueryException :
                self.display_progression("Peer Query Excpetion : Peer not alive.")
                break
            except DisconnectedSocketException:
                self.connected = False
                self.display_progression(
                    "Disconnected Socket Exception : Connection with the peer has been closed unexpectedly.")
                break

            try:
                self.ask_for_peers()
            except PeerQueryException:
                self.display_progression(
                    "PeerQueryException : Query for other peers failed (attempt " + str(nb_attempts + 1) + ")")

                if nb_attempts == (self.ADDR_QUERY_MAX_ATTEMPTS - 1):
                    self.display_progression(
                        "Peer Request Timeout : Too much attempts to query the peer without success.")
                    break

                nb_attempts = nb_attempts + 1
                continue
            except DisconnectedSocketException:
                self.connected = False
                self.display_progression(
                    "Disconnected Socket Exception : Connection with the peer has been closed unexpectedly.")
                break

        self.sender.disconnect()
        self.receiver.disconnect()

        return self.nb_peer_queried

    def connect_to_peer(self, node_ip, node_port, connection_timeout):

        try:
            addr_type = self.get_ip_type(node_ip)
        except UnknownIPAddressTypeException as err:
            self.add_error(str(err))
            raise ConnectionException(
                "UnknownIPAddressType Exception : The IP Address provided is neither a valid IPv6 nor a valid IPv4 Address")

        if addr_type == "ipv4":
            self.socket_node = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        elif addr_type == "ipv6":
            self.socket_node = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

        self.socket_node.settimeout(connection_timeout)

        self.socket_node.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            if addr_type == "ipv4":
                start = time.time()
                self.socket_node.connect((node_ip, node_port))
                end = time.time()
            elif addr_type == "ipv6":
                start = time.time()
                self.socket_node.connect((node_ip, node_port, 0, 0))
                end = time.time()
        except socket.timeout as err:
            raise ConnectionException(repr(err))
        except socket.error as err:
            raise ConnectionException(repr(err))

        self.measurements_manager.add_peer_tcp_handshake_duration(self.node_ip, end - start)

        self.socket_node.settimeout(self.SOCKET_TIMEOUT)

        self.sender.disconnect()
        self.receiver.disconnect()

        self.sender.connect(self.socket_node)
        self.receiver.connect(self.socket_node)

        start = time.time()
        self.bitcoin_handshake()
        end = time.time()

        self.measurements_manager.add_peer_bitcoin_handshake_duration(self.node_ip, end - start)

    def bitcoin_handshake(self):

        nonce = random.randint(0, pow(2, 8))
        self.connection_nonce = nonce

        version_msg_to_send = Version_Message.Version_Message("version", self.PROTOCOL_VERSION, self.src_ip,
                                                              self.src_port, self.SERVICE_PROVIDED, self.node_ip,
                                                              self.node_port, self.target_service,
                                                              self.connection_nonce)

        try:
            self.send_msg(version_msg_to_send)
        except SendMessageTimeoutException:
            raise HandShakeFailureException(
                "HandShakeFailure Exception : Fail to send a Version Message to the peer (Timeout).")
        except SendMessageFailureException as err:
            raise HandShakeFailureException(
                "HandShakeFailure Exception : Fail to send a Version Message to the peer (Protocol Exception).")

        msg_to_rcv = ["version", "verack"]
        try:
            while len(msg_to_rcv) > 0:
                rcv_msg = self.rcv_msg(self.HANDSHAKE_TIMEOUT)

                command = rcv_msg.getCommand()
                if command in msg_to_rcv:
                    try:
                        self.treat_msg(rcv_msg)
                    except PacketTreatmentException:
                        raise HandShakeFailureException(
                            "HandShakeFailure Exception : Fail to treat " + rcv_msg.getCommand() + " Message from the peer.")
                    if command == "version":
                        self.peer_connection_nonce = rcv_msg.getVersionNonce()
                    msg_to_rcv.remove(command)
                else:
                    raise HandShakeFailureException(
                        "HandShakeFailure Exception : Reception of a Unexpected Message : " + command + " (VERSION/VERACK Messages expected).")
        except ReceiveMessageTimeoutException:
            raise HandShakeFailureException(
                "HandShakeFailure Exception : Fail to receive the VERSION/VERACK Messages from the peer (Timeout).")

        if len(msg_to_rcv) > 0:
            raise HandShakeFailureException(
                "HandShakeFailure Exception : Fail to receive the VERSION/VERACK Messages from the peer (timeout).")

        verack_msg_to_send = Verack_Message.Verack_Message("verack")

        try:
            self.send_msg(verack_msg_to_send)
        except SendMessageTimeoutException:
            raise HandShakeFailureException(
                "HandShakeFailure Exception : Fail to send the VERACK Message to the peer (Timeout).")
        except SendMessageFailureException as err:
            raise HandShakeFailureException(
                ("HandShakeFailure Exception : Fail to send the VERACK Message to the peer.\n" + str(err)))

    def ask_for_peers(self):
        request_successfull = False
        self.display_progression("Querying for other Peers ...")

        if self.bitcoin_ask_for_peers():
            request_successfull = True

        if not request_successfull:
            raise PeerQueryException("PeerQuery Exception : Fail to ask the peers for new peers.")
        else:
            self.display_progression("Query for other Peers successfull.")

    def ask_alive(self):
        request_successfull = False
        nb_attempts = 0

        while nb_attempts < self.ASK_ALIVE_MAX_ATTEMPTS:
            try:
                self.bitcoin_ask_alive()
                request_successfull = True
                break
            except AskAliveException:
                nb_attempts = nb_attempts + 1
                continue

        if not request_successfull:
            raise PeerQueryException("PeerQuery Exception : Peer considered as not alive (no answer to PING).")

    def bitcoin_ask_alive(self):
        nonce = random.randint(0, pow(2, 8))
        msg_to_send = Ping_Message.Ping_Message("ping", nonce)

        try:
            self.send_msg(msg_to_send)
        except SendMessageTimeoutException:
            raise AskAliveException("AskAlive Exception : Fail to send the PING Message from the peer (Timeout).")
        except SendMessageFailureException as err:
            raise AskAliveException(
                ("AskAlive Exception : Fail to send a GetAddr Message to the peer (Protocol Exception).\n" + str(err)))

        try:
            command = ""
            start = time.time()
            timeout = self.PING_TIMEOUT

            while command != "pong" and command != "ping":
                if (time.time() - start) > timeout:
                    raise AskAliveException(
                        "AskAlive Exception : Fail to receive Pong Message from the peer (Timeout).")

                rcv_msg = self.rcv_msg(self.PING_TIMEOUT)

                start_treat_msg = time.time()
                try:
                    self.treat_msg(rcv_msg)
                except PacketTreatmentException:
                    raise AskAliveException(
                        "AskAlive Exception : Fail to treat " + rcv_msg.getCommand() + " Message from the peer.")

                timeout = timeout + (time.time() - start_treat_msg)
                command = rcv_msg.getCommand()
        except ReceiveMessageTimeoutException:
            raise AskAliveException("AskAlive Exception : Fail to receive Pong Message from the peer (Timeout).")

    def bitcoin_ask_for_peers(self):
        getaddr_msg_to_send = GetAddr_Message.GetAddr_Message("getaddr")

        try:
            self.send_msg(getaddr_msg_to_send)
        except SendMessageTimeoutException:
            raise PeerQueryException("PeerQuery Exception : Fail to send the GETADDR Message from the peer (Timeout).")
        except SendMessageFailureException as err:
            raise PeerQueryException(
                ("PeerQuery Exception : Fail to send a GetAddr Message to the peer (Protocol Exception).\n" + str(err)))

        try:
            command = ""
            start = time.time()
            timeout = self.ADDR_TIMEOUT
            while command != "addr":
                if (time.time() - start) > timeout:
                    raise PeerQueryException(
                        "PeerQuery Exception : Fail to receive ADDR Message from the peer (Timeout).")

                rcv_msg = self.rcv_msg(self.ADDR_TIMEOUT)

                command = rcv_msg.getCommand()


                start_treat_msg = time.time()
                try:
                    self.treat_msg(rcv_msg)
                except PacketTreatmentException:
                    raise PeerQueryException(
                        "PeerQuery Exception : Fail to treat " + rcv_msg.getCommand() + " Message from the peer.")
                timeout = timeout + (time.time() - start_treat_msg)

        except ReceiveMessageTimeoutException:
            raise PeerQueryException("PeerQuery Exception : Fail to receive the ADDR Message from the peer (Timeout).")

        if rcv_msg.isAdvertisement(self.node_ip):
            return False
        else:
            return True

    def bitcoin_close_connection(self):
        self.display_progression("Connection to " + self.node_ip + ":" + str(self.node_port) + " being closed ...")

        self.sender.disconnect()
        self.receiver.disconnect()

        self.socket_node.shutdown(socket.SHUT_RDWR)
        self.socket_node.close()

        self.display_progression("Connection to " + self.node_ip + ":" + str(self.node_port) + " closed successfully.")

    def send_msg(self, bitcoin_msg, timeout=1):
        self.sender.send_msg(bitcoin_msg, timeout)

    def rcv_msg(self, timeout):
        """
        Wait for a message for [timeout] seconds and return the message or throw a Queue.Empty Error if None is
        available.
        :param timeout: nb of seconds to wait for a message
        :return: the most ancient message on the queue
        """

        result = self.receiver.rcv_msg(timeout)

        return result

    def treat_msg(self, rcv_msg):
        command = rcv_msg.getCommand()

        if command == "version":
            self.measurements_manager.add_version_stat(rcv_msg.getVersion())
            self.measurements_manager.add_IP_Service(self.node_ip, rcv_msg.getSenderService())

        elif command == "verack":
            None
        elif command == "getaddr":
            None
        elif command == "addr":
            if not rcv_msg.isAdvertisement(self.node_ip):
                nb_rcv = rcv_msg.get_IP_Nb()

                if nb_rcv < 999:
                    self.continue_to_ask = False
                self.nb_peer_queried = self.nb_peer_queried + nb_rcv

                nb_rcv = rcv_msg.get_IP_Nb()

                nb_new = self.measurements_manager.treatAddrPacket(rcv_msg)

                self.measurements_manager.add_peer_queried(self.node_ip, nb_rcv)
        elif command == "ping":
            msg = Pong_Message.Pong_Message("pong", rcv_msg.getPingNonce())

            try:
                self.send_msg(msg)
            except SendMessageTimeoutException:
                raise PacketTreatmentException(
                    "PacketTreatment Exception : Fail to anwer the PING Message from the peer (Timeout).")
            except SendMessageFailureException as err:
                raise PacketTreatmentException(
                    ("PacketTreatment Exception : Fail to answer the PING Message of the peer.\n" + str(err)))

        elif command == "pong":
            None
        else:
            raise UnsupportedBitcoinCommandException(
                "UnsupportedBitcoinCommand Exception : The command " + command + " is not supported.")

    def get_ip_type(self, ip_addr):
        try:
            ip = ipaddress.ip_address(ip_addr)
        except ValueError:
            error = "UnknownIPAddressType Exception : Unknown IP Address type of " + ip_addr + "."
            raise UnknownIPAddressTypeException(error)

        version = ip.version
        if version == 4:
            return "ipv4"
        if version == 6:
            return "ipv6"

    def display_progression(self, string):
        if self.displayer is not None:
            if self.connected:
                self.displayer.display_thread_progression(("Connected to " + str(self.node_ip) + " - " + string),
                                                          self.thread_nb)
            else:
                self.displayer.display_thread_progression(("Not Connected to " + str(self.node_ip) + " - " + string),
                                                          self.thread_nb)

    def add_error(self, error):
        self.error.append(error)

    def get_tracebacks(self):
        return self.tracebacks

    def calibrate_timeouts(self, nb_pings=3):
        """
        This function will calibrate the different timeouts value thanks to the estimation of
        the rtt (done with consecutive ping(s)).
        :return: void
        """
        stat = self.ping(self.node_ip, nb_pings)

        if stat is not None:
            # PING PACKET is 64 Bytes
            per_bytes_rtt = (float(stat["avg"]) / 64) / 1000  # seconds

            self.PING_TIMEOUT = (per_bytes_rtt / 2) * 92 + (
                        per_bytes_rtt / 2) * 92  # Time for the PING to reach its destination + Time for the PONG to reach you back
            self.ADDR_TIMEOUT = (per_bytes_rtt / 2) * 84 + (
                        per_bytes_rtt / 2) * 30027  # Time for the GETADDR to reach its destination + Time for the ADDR to reach you back (WORSE CASE = ADDR with 1000 addresses)
            self.HANDSHAKE_TIMEOUT = (per_bytes_rtt / 2) * 170 + ((per_bytes_rtt / 2) * 170 + (
                        per_bytes_rtt / 2) * 84)  # Time for the VERSION to reach its destination + Time for the VERSION/VERACK message to reach you back.

    def ping(self, address, count=3):
        """
        This command is sending [count] 56 Bytes ping(s) (+ 8 Bytes ICMP Header) to the node
        having the address [address].
        :param address: address of the node to whom you wants to send the pings
        :param count: nb of pings you would like to send
        :return: RTT statistics
        """
        cmd = ["ping", ("-c " + str(count)), address, "-s 56"]
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip()
        except subprocess.CalledProcessError:
            return None

        lines = output.split("\n")
        total = lines[-2].split(",")[3].split()[1]
        timing = lines[-1].split()[3].split('/')

        return {
            'type': "rtt",
            "min": timing[0],
            "avg": timing[1],
            "max": timing[2],
            "mdev": timing[3],
            "total": total
        }
