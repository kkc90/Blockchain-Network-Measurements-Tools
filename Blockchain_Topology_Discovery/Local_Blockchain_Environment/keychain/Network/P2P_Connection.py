import datetime
import os
import queue
import random
import socket
import sys
import time
import traceback
from threading import Thread, Event

import math

from keychain.Network.NetworkException import *
from keychain.Network.Network_Constant import Network_Constant
from keychain.Network.Protocol import Protocol
from keychain.Network.Protocol.Bitcoin_Messages import \
    Version_Message, Ping_Message, Verack_Message, Pong_Message
from keychain.Network.Protocol.ProtocolException import *
from keychain.Network.Protocol.Protocol_Constant import *


class P2P_Connection(Thread):

    def __init__(self, src_ip, src_port, src_service, node_ip, node_port, node_service, socket_node, network,
                 network_manager):
        Thread.__init__(self)

        self._src_ip = src_ip
        self._src_port = src_port
        self._src_service = src_service

        self._node_ip = node_ip
        self._node_port = node_port
        self._node_service = node_service

        self._network = network

        self._socket_node = socket_node

        self._handshake_msg = dict()

        self._handshake_msg["Version Sent"] = False
        self._handshake_msg["Verack Received"] = False
        self._handshake_msg["Version Received"] = False

        self._handshake_start_timestamp = None

        self._connection_nonce_to_send = None
        self._connection_nonce_to_rcv = None

        self._ping_nonce = None
        self._last_ping_timestamp = None
        self._last_pong_timestamp = None

        self._nb_timeout = 0

        self._network_manager = network_manager

        self.__stop_event = Event()

        self._data_requested = list()

        self._send_queue = queue.Queue()
        self._handler_queue = queue.Queue()

        self._sender_thread = None
        self._listener_thread = None
        self._handler_thread = None

        self._message_waiting_to_be_sent = list()

        if self._network_manager.monitorIsTrue():
            self.init_log_packet()

    """
            GETTERS
    """

    def get_data_requested(self):
        return self._data_requested

    def get_node_service(self):
        return self._node_service

    def get_node_info(self):
        return self._node_ip, self._node_port, self._node_service, self._handshake_start_timestamp

    def get_handshake_time(self):
        return self._handshake_start_timestamp

    def is_valid_handshake_message(self, command):
        if self._handshake_msg["Version Received"] is False and command == "version":
            return True
        elif self._handshake_msg["Verack Received"] is False and command == "verack":
            return True
        else:
            return False

    def has_ping_timeout(self):
        if self._last_ping_timestamp is not None and self._last_pong_timestamp is not None\
                and self._last_pong_timestamp < self._last_ping_timestamp\
                and (time.time() - self._last_ping_timestamp) > Network_Constant.PING_TIMEOUT:

            return True
        elif self._last_ping_timestamp is not None and self._last_pong_timestamp is None \
                and (time.time() - self._last_ping_timestamp) > Network_Constant.PING_TIMEOUT:

            return True
        else:
            return False

    def get_last_round_trip_time(self):
        if self._last_ping_timestamp is not None and self._last_pong_timestamp is not None \
                and self._last_ping_timestamp < self._last_pong_timestamp:
            return self._last_pong_timestamp - self._last_ping_timestamp

        else:
            return None
    """
            THREAD MANAGEMENT
    """

    def run(self):
        self._listener_thread = Thread(target=self.listener_thread, args=())

        self._sender_thread = Thread(target=self.sender_thread, args=())

        self._handler_thread = Thread(target=self.handler_thread, args=())

        self._listener_thread.start()

        self._sender_thread.start()

        self._handler_thread.start()

        self._listener_thread.join()

        self._sender_thread.join()

        self._handler_thread.join()

        self._network_manager.display_info(("Connection with " + self._node_ip + " has been shut down"), 8)

    def sender_thread(self):
        try:
            while not self.__stop_event.isSet():
                try:
                    bitcoin_msg = self._send_queue.get(block=False)
                    self.send(bitcoin_msg)
                except queue.Empty:
                    pass

        except SendMessageTimeoutException as err:
            if self._network_manager.monitorIsTrue():
                self.error_recording()

        except BrokenConnectionException:
            if self._network_manager.monitorIsTrue():
                self.error_recording()

        except Exception:
            self.error_recording()

        self.__stop_event.set()

    def listener_thread(self):
        try:
            while not self.__stop_event.isSet():
                self.listen()

        except BrokenConnectionException:
            if self._network_manager.monitorIsTrue():
                self.error_recording()

        except Exception:
            self.error_recording()

        self.__stop_event.set()

    def handler_thread(self):
        try:
            while not self.__stop_event.isSet():
                try:
                    msg = self._handler_queue.get(block=False)
                    self.handle_msg(msg)
                except queue.Empty:
                    pass

        except SendMessageTimeoutException:
            if self._network_manager.monitorIsTrue():
                self.error_recording()

        except BrokenConnectionException:
            if self._network_manager.monitorIsTrue():
                self.error_recording()

        except Exception:
            self.error_recording()

        self.__stop_event.set()

    def listen(self):
        try:
            rcv_msg = self.rcv_msg(block=True, timeout=3*Network_Constant.SOCKET_TIMEOUT)

            if self.is_handshake_done() or self.is_valid_handshake_message(rcv_msg.getCommand()):

                if self.is_important(rcv_msg):
                    self.handle_msg(rcv_msg)
                else:
                    self._handler_queue.put(rcv_msg)

            else:
                raise BrokenConnectionException("BrokenConnection Exception : Unvalid " + rcv_msg.getCommand()
                                                + " packet sent during handshake")

        except ReceiveMessageTimeoutException:
            if self._nb_timeout < Network_Constant.NB_TIMEOUT_BEFORE_UNACTIVE:
                self._nb_timeout = self._nb_timeout + 1

                if self.is_handshake_done():
                    self.ask_alive()

            else:
                if self.has_ping_timeout():
                    raise BrokenConnectionException("BrokenConnection Exception : Peer fail to answer "
                                                    + str(Network_Constant.NB_TIMEOUT_BEFORE_UNACTIVE)
                                                    + " PING messages.")

        except SendMessageTimeoutException:
            if self._nb_timeout < Network_Constant.NB_TIMEOUT_BEFORE_UNACTIVE:
                self._nb_timeout = self._nb_timeout + 1

                if self.is_handshake_done():
                    self.ask_alive()

            else:
                if self.has_ping_timeout():
                    raise BrokenConnectionException("BrokenConnection Exception : Peer fail to answer " + str(Network_Constant.NB_TIMEOUT_BEFORE_UNACTIVE) + " PING messages.")

    def send(self, bitcoin_msg, block=False, timeout=math.inf):
        start_send = time.time()
        while time.time() - start_send < timeout and not self.__stop_event.is_set():
            try:
                self.bitcoin_send_msg(bitcoin_msg)

                if bitcoin_msg in self._message_waiting_to_be_sent:
                    self._message_waiting_to_be_sent.remove(bitcoin_msg)

                if self._network_manager.monitorIsTrue():
                    self.log_packet_sent(bitcoin_msg.getCommand())

                return

            except socket.timeout:
                if block is True:
                    continue
                else:
                    raise SendMessageTimeoutException("SendMessageTimeout Exception: Fail to send "
                                                      + bitcoin_msg.getCommand() + " packet (Timeout).")

            except socket.error:
                raise BrokenConnectionException(("BrokenConnection Exception: Fail to send "
                                                 + bitcoin_msg.getCommand() + " packet (broken socket)."))

    def join(self, **kwargs):
        self.__stop_event.set()

        Thread.join(self)

        self.bitcoin_close_connection()

    def kill(self):
        self.__stop_event.set()

        self.bitcoin_close_connection()

    def isAlive(self):
        return not self.__stop_event.isSet()

    """
            CONNECTION WITH THE PEER MANAGEMENT
    """

    def is_handshake_done(self):
        return self._handshake_msg["Version Sent"] and self._handshake_msg["Version Received"] \
               and self._handshake_msg["Verack Received"]

    def wait_for_handshake(self, timeout=Network_Constant.HANDSHAKE_TIMEOUT):
        start = time.time()

        while not self.is_handshake_done() and not self.__stop_event.isSet():
            handshake_duration = (time.time() - start)

            if handshake_duration > timeout:
                raise HandShakeFailureException("HandshakeFailure Exception: Fail to execute the handshake (Timeout).")

    def bitcoin_handshake(self):

        nonce = random.randint(0, pow(2, 8))

        self._connection_nonce_to_rcv = nonce

        version_msg = Version_Message.Version_Message(Network_Constant.PROTOCOL_VERSION, self._src_ip,
                                                      self._src_port, self._src_service, self._node_ip,
                                                      self._node_port, self._node_service, nonce)

        self.send_msg(version_msg)

        self._handshake_msg["Version Sent"] = True

        start_connection = time.time()

        while not self.__stop_event.is_set() and time.time() - start_connection < Network_Constant.HANDSHAKE_TIMEOUT \
                and not self.is_handshake_done():
            continue

        if not self.is_handshake_done():
            raise HandShakeFailureException("HandshakeFailure Exception: Fail to execute the handshake (Timeout).")

    def bitcoin_close_connection(self):
        if self._connection_nonce_to_rcv is not None and self._connection_nonce_to_send is not None:
            version_msg = Version_Message.Version_Message(Network_Constant.PROTOCOL_VERSION,
                                                          self._src_ip, self._src_port, self._src_service,
                                                          self._node_ip, self._node_port,
                                                          Protocol_Constant.NODE_NETWORK,
                                                          self._connection_nonce_to_send)

            self.bitcoin_send_msg(version_msg)

            self._socket_node.close()

    """
            INTERACTIONS WITH PEERS
    """

    def send_msg(self, bitcoin_msg, block=False):
        self._send_queue.put(bitcoin_msg)

        if block is True:
            self._message_waiting_to_be_sent.append(bitcoin_msg)

        while block is True and bitcoin_msg in self._message_waiting_to_be_sent and not self.__stop_event.is_set():
            continue

    def ask_alive(self, block=False):
        nonce = random.randint(0, pow(2, 8))

        ping_msg = Ping_Message.Ping_Message(nonce)

        self.send_msg(ping_msg, block=block)

        self._ping_nonce = nonce

        self._last_ping_timestamp = time.time()

    def request_data(self, data):
        self._data_requested.append(data)

    def remove_data_requested(self, object_type, object_hash):
        if (object_type, object_hash) in self._data_requested:
            self._data_requested.remove((object_type, object_hash))

    """
            SENDING/RECEIVING MANAGEMENT
    """

    def bitcoin_send_msg(self, bitcoin_msg):
        msg = Protocol.get_packet(bitcoin_msg, self._network)

        self._socket_node.send(msg, socket.MSG_WAITALL)

    def rcv_msg(self, block=False, timeout=math.inf):
        result = None

        start_rcv = time.time()
        while time.time() - start_rcv < timeout and not self.__stop_event.is_set():
            try:
                result = self.bitcoin_rcv_msg()

                self._nb_timeout = 0

                break

            except socket.timeout:

                if block is True:
                    continue
                else:
                    raise ReceiveMessageTimeoutException("ReceiveMessageTimeout Exception: "
                                                         "Fail to receive a Packet (Timeout).")
            except socket.error:
                raise BrokenConnectionException("BrokenConnection Exception: Fail to receive a Packet.")

        if result is None:
            raise ReceiveMessageTimeoutException("ReceiveMessageTimeout Exception: Fail to receive a Packet (Timeout).")

        return result

    def bitcoin_rcv_msg(self):
        magic_nb = self.rcv_socket(4)

        command = self.rcv_socket(12)

        length = self.rcv_socket(4)
        payload_length = int.from_bytes(length, byteorder='little')

        checksum = self.rcv_socket(4)

        payload = self.rcv_socket(payload_length)

        net = Protocol.get_origin_network(magic_nb)

        if net != self._network:
            raise ProtocolException("Protocol Exception : The Origin Network " + net + " is unvalid.")

        result = Protocol.treat_packet(command, length, checksum, payload)

        return result

    def rcv_socket(self, to_read, step=4):
        payload = bytearray()

        while to_read > 0 and not self.__stop_event.is_set():
            if to_read > step:
                readed = step
            else:
                readed = to_read

            msg = bytearray(self._socket_node.recv(readed, socket.MSG_WAITALL))
            payload = payload + msg  # See TCP Protocol for Bits Order
            to_read = to_read - len(msg)

        if len(payload) < to_read:
            raise socket.timeout("Socket Timeout: Fail to received " + str(to_read) + " bytes")

        return payload

    """
            MESSAGE TREATMENT
    """

    def is_important(self, rcv_msg):
        if rcv_msg.getCommand() == "ping" or rcv_msg.getCommand() == "pong" or rcv_msg.getCommand() == "version" \
                or rcv_msg.getCommand() == "verack":
            return True

        else:
            return False

    def handle_msg(self, rcv_msg):
        command = rcv_msg.getCommand()

        if self._network_manager.monitorIsTrue():
            self.log_packet_received(command)

        if command == "version":
            self.treat_version_msg(rcv_msg)

        elif command == "verack":
            self.treat_verack_msg(rcv_msg)

        elif command == "getaddr":
            self.treat_getaddr_msg(rcv_msg)

        elif command == "addr":
            self.treat_addr_msg(rcv_msg)

        elif command == "ping":
            self.treat_ping_msg(rcv_msg)

        elif command == "pong":
            self.treat_pong_msg(rcv_msg)

        elif command == "block":
            self.treat_block_msg(rcv_msg)

        elif command == "getblock":
            self.treat_getblock_msg(rcv_msg)

        elif command == "getdata":
            self.treat_getdata_msg(rcv_msg)

        elif command == "getheader":
            self.treat_getheader_msg(rcv_msg)

        elif command == "inv":
            self.treat_inv_msg(rcv_msg)

        elif command == "notfound":
            self.treat_notfound_msg(rcv_msg)

        elif command == "tx":
            self.treat_tx_msg(rcv_msg)

        elif command == "mempool":
            self.treat_mempool_msg(rcv_msg)

        else:
            raise Protocol.UnsupportedBitcoinCommandException(
                "UnsupportedBitcoinCommand Exception : The command " + command + " is not supported.")

    def treat_version_msg(self, version_msg):
        # Version Message Sent for executing the Handshake
        if not self.is_handshake_done() and self._handshake_msg["Version Received"] is not True:
            verack_msg = Verack_Message.Verack_Message()

            self.send_msg(verack_msg)

            self._connection_nonce_to_send = version_msg.getVersionNonce()

            self._node_service = version_msg.getSenderService()

            # Version Message Sent First by the peer
            if self._handshake_msg["Version Sent"] is not True:
                nonce = random.randint(0, pow(2, 8))

                self._connection_nonce_to_rcv = nonce

                version_msg = Version_Message.Version_Message(Network_Constant.PROTOCOL_VERSION,
                                                              self._src_ip, self._src_port, self._src_service,
                                                              self._node_ip, self._node_port,
                                                              Protocol_Constant.NODE_NETWORK, nonce)

                self.send_msg(version_msg)

                self._handshake_msg["Version Sent"] = True
                self._handshake_msg["Version Received"] = True

            # Version Message Sent by the peer to answer your Version Message
            else:
                self._handshake_msg["Version Received"] = True

                self._handshake_start_timestamp = time.time()

        else:

            # Version Message Sent to end the Connection
            if version_msg.getVersionNonce() == self._connection_nonce_to_rcv:
                self._connection_nonce_to_rcv = None
                self.__stop_event.set()

    def treat_verack_msg(self, verack_msg):
        if self._handshake_msg["Version Sent"] is True:
            self._handshake_msg["Verack Received"] = True

            self._handshake_start_timestamp = time.time()

    def treat_ping_msg(self, ping_msg):
        pong_msg = Pong_Message.Pong_Message(ping_msg.getPingNonce())

        self.send_msg(pong_msg)

    def treat_pong_msg(self, pong_msg):
        if self._ping_nonce == pong_msg.getPongNonce():

            self._ping_nonce = None

            self._last_pong_timestamp = time.time()

    def treat_getaddr_msg(self, getaddr_msg):
        self._network_manager.send_peers(self)

    def treat_addr_msg(self, addr_msg):
        peer_list = addr_msg.get_ip_table()
        self._network_manager.add_peer_to_pool(peer_list)

    def treat_inv_msg(self, inv_msg):
        self._network_manager.treat_inv_packet(self, inv_msg, inv_msg.getMessageSize())

    def treat_getdata_msg(self, getdata_msg):
        block_hash_asked, tx_hashes_asked = getdata_msg.objects_asked()

        self._network_manager.send_data(self, tx_hashes_asked, block_hash_asked)

    def treat_block_msg(self, block_msg):
        self._network_manager.treat_block_message(self, block_msg, block_msg.getMessageSize())

    def treat_tx_msg(self, tx_msg):
        self._network_manager.treat_tx_message(self, tx_msg, tx_msg.getMessageSize())

    def treat_notfound_msg(self, notfound_msg):
        block_hashes, tx_hashes = notfound_msg.get_available_objectst()

        for block_hash in block_hashes:
            if ("block", block_hash) in self._data_requested:
                self._data_requested.remove(("block", block_hash))

        for tx_hash in tx_hashes:
            if ("tx", tx_hash) in self._data_requested:
                self._data_requested.remove(("tx", tx_hash))

    def treat_getblock_msg(self, getblock_msg):
        self._network_manager.treat_getblock(self, getblock_msg)

    def treat_getheader_msg(self, getheader_msg):
        self._network_manager.treat_getheader(self, getheader_msg)

    def treat_mempool_msg(self, mempool_msg):
        self._network_manager.treat_mempool(self, mempool_msg)

    """
            MONITORING MANAGEMENT
    """

    def display_info(self, msg):
        connected = self.is_handshake_done()
        if connected is True:
            print("Peer ", self._src_ip, " - Connected to ", self._node_ip, " : ", msg)
        else:
            print("Peer ", self._src_ip, " - Not Connected to ", self._node_ip, " : ", msg)

    def error_recording(self):
        directory = "Log/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        directory = "Log/Log_Peer_" + self._src_ip + "/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        directory = "Log/Log_Peer_" + self._src_ip + "/Connections/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        directory = "Log/Log_Peer_" + self._src_ip + "/Connections/" + self._node_ip + "/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        stdout = open((directory + self._node_ip + "_errors.txt"), "a")

        ex_type, ex, tb = sys.exc_info()
        traceback.print_exception(ex_type, ex, tb, file=stdout)
        stdout.write('\n\n')

        stdout.close()

    def init_log_packet(self):
        self.log_packet(None, None, init=True)

    def log_packet_received(self, command):
        self.log_packet(command, received=True)

    def log_packet_sent(self, command):
        self.log_packet(command, received=False)

    def log_packet(self, command, received, init=False):
        directory = "Log/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        directory = "Log/Log_Peer_" + self._src_ip + "/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        directory = "Log/Log_Peer_" + self._src_ip + "/Connections/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        directory = "Log/Log_Peer_" + self._src_ip + "/Connections/" + self._node_ip + "/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        stdout = open((directory + self._node_ip + "_packets.txt"), "a")

        if init is True:
            stdout.write("Connection Time : " + (str(datetime.datetime.fromtimestamp(time.time())) + "\n\n"))

        elif received is True:
            stdout.write((str(datetime.datetime.fromtimestamp(time.time())) + " : " + command
                          + " packet has been received from " + self._node_ip + "\n"))

        else:
            stdout.write((str(datetime.datetime.fromtimestamp(time.time())) + " : " + command
                          + " packet has been sent to " + self._node_ip + "\n"))

        stdout.close()
