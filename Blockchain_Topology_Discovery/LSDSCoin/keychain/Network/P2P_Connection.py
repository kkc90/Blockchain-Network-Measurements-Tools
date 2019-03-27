import os
import sys
import traceback

import socket

import time
import random
import math

from threading import Thread, Event

from .Protocol import *
from .Protocol.Bitcoin_Messages import *
from .NetworkException import *
from .Network_Constant import *


class P2P_Connection(Thread):
    def __init__(self, src_ip, src_port, src_service, node_ip, node_port, node_service, socket_node, network,
                 network_manager, blockchain_manager):
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

        self._connection_nonce_to_send = None
        self._connection_nonce_to_rcv = None

        self._ping_nonce = None
        self._last_ping_timestamp = None

        self._nb_timeout = 0

        self._network_manager = network_manager
        self._blockchain_manager = blockchain_manager

        self.__stop_event = Event()

    def run(self):
        try:
            while not self.__stop_event.isSet():
                self.listen()

            self.bitcoin_close_connection()

        except BrokenConnectionException as err:
            self.display_info(str(err))

        except Exception:
            traceback.print_exc()
            self.error_recording()

        self._socket_node.close()

        self.__stop_event.set()

        #self.display_info(("Connection with " + str(self._node_ip) + " has been closed."))

    def listen(self):
        try:
            rcv_msg = self.rcv_msg()
            self.handle_msg(rcv_msg)

        except ReceiveMessageTimeoutException as err:
            if self._nb_timeout < Network_Constant.NB_TIMEOUT_BEFORE_UNACTIVE:
                self._nb_timeout = self._nb_timeout + 1

            else:
                # If handshake has not been done or if pong has not been answered back from previous ping.
                if (not self.is_handshake_done()) or (self._last_ping_timestamp is not None and time.time() -
                                                      self._last_ping_timestamp < Network_Constant.PING_TIMEOUT):
                    raise BrokenConnectionException(repr(err))
                else:
                    self.ask_alive()

        except SendMessageTimeoutException as err:
            if self._nb_timeout < Network_Constant.NB_TIMEOUT_BEFORE_UNACTIVE:
                self._nb_timeout = self._nb_timeout + 1

            else:
                # If handshake has not been done or if pong has not been answered back from previous ping.
                if (not self.is_handshake_done()) or (self._last_ping_timestamp is not None and time.time()
                                                     - self._last_ping_timestamp < Network_Constant.PING_TIMEOUT):
                    raise BrokenConnectionException(repr(err))
                else:
                    self.ask_alive()

    def join(self, **kwargs):
        self.__stop_event.set()

        Thread.join(self)

    def kill(self):
        self.__stop_event.set()

    def isAlive(self):
        return not self.__stop_event.isSet()

    def is_handshake_done(self):
        return self._handshake_msg["Version Sent"] and self._handshake_msg["Version Received"] \
               and self._handshake_msg["Verack Received"]

    def get_node_service(self):
        return self._node_service

    def get_node_info(self):
        return self._node_ip, self._node_port, self._node_service

    def wait_for_handshake(self):
        while self.is_handshake_done() and (not self.__stop_event.isSet()):
            continue

    def bitcoin_handshake(self):

        nonce = random.randint(0, pow(2, 8))

        self._connection_nonce_to_rcv = nonce

        version_msg = Version_Message.Version_Message(Network_Constant.PROTOCOL_VERSION, self._src_ip,
                                                               self._src_port, self._src_service, self._node_ip,
                                                               self._node_port, self._node_service, nonce)

        try:
            self.send_msg(version_msg)

        except SendMessageException:
            raise HandShakeFailureException("HandshakeFailure Exception: Fail to execute the handshake (Timeout).")

        self._handshake_msg["Version Sent"] = True

        start_connection = time.time()

        while not self.__stop_event.isSet() and time.time() - start_connection < Network_Constant.HANDSHAKE_TIMEOUT \
                and not self.is_handshake_done():
            continue

        if not self.is_handshake_done():
            raise HandShakeFailureException("HandshakeFailure Exception: Fail to execute the handshake (Timeout).")

    def bitcoin_close_connection(self):
        if self._connection_nonce_to_rcv is not None:
            version_msg = Version_Message.Version_Message(Network_Constant.PROTOCOL_VERSION,
                                                                   self._src_ip, self._src_port, self._src_service,
                                                                   self._node_ip, self._node_port,
                                                                   Protocol_Constant.NODE_NETWORK,
                                                                   self._connection_nonce_to_send)

            self.send_msg(version_msg)

            self._socket_node.shutdown(socket.SHUT_WR)

    def ask_for_peers(self, block=False):
        getaddr_msg = GetAddr_Message.GetAddr_Message()

        self.send_msg(getaddr_msg)

    def ask_alive(self):
        nonce = random.randint(0, pow(2, 8))

        ping_msg = Ping_Message.Ping_Message(nonce)

        try:
            self.send_msg(ping_msg)
        except SendMessageTimeoutException:
            raise BrokenConnectionException("BrokenConnection Exception: Fail to ask the peer for heartbeat.")

        self._ping_nonce = nonce

        self._last_ping_timestamp = time.time()

    def send_msg(self, bitcoin_msg, block=False, timeout=math.inf):
        start_send = time.time()
        while time.time() - start_send < timeout:
            try:
                self.bitcoin_send_msg(bitcoin_msg)

                self._nb_timeout = 0

                #self.display_info((str(self._src_ip) + " : " + str(bitcoin_msg.getCommand()) + " sent"))

                return

            except socket.timeout:
                if block is True:
                    continue
                else:
                    raise SendMessageTimeoutException("SendMessageTimeout Exception: "
                                                      "Fail to receive a Packet (Timeout).")
            except socket.error:
                raise BrokenConnectionException(("BrokenConnection Exception: Fail to send "
                                                 + bitcoin_msg.getCommand() + " Packet."))

        raise SendMessageTimeoutException("SendMessageTimeout Exception: "
                                          "Fail to receive a Packet (Timeout).")

    def bitcoin_send_msg(self, bitcoin_msg):

        msg = Protocol.get_packet(bitcoin_msg, self._network)

        self._socket_node.send(msg, socket.MSG_WAITALL)

    def rcv_msg(self, block=False, timeout=math.inf):
        result = None

        start_rcv = time.time()
        while time.time() - start_rcv < timeout:
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
            ReceiveMessageTimeoutException("ReceiveMessageTimeout Exception: "
                                           "Fail to receive a Packet (Timeout).")

        return result

    def bitcoin_rcv_msg(self):
        magic_nb = bytearray(self._socket_node.recv(4, socket.MSG_WAITALL))

        command = bytearray(self._socket_node.recv(12, socket.MSG_WAITALL))

        length = bytearray(self._socket_node.recv(4, socket.MSG_WAITALL))
        payload_length = int.from_bytes(length, byteorder='little')

        checksum = bytearray(self._socket_node.recv(4, socket.MSG_WAITALL))

        to_read = payload_length

        readed = 0
        payload = bytearray()

        # So that the socket doesn't timeout
        while to_read > 0:
            if to_read > 4:
                readed = 4
            else:
                readed = to_read

            msg = bytearray(self._socket_node.recv(readed, socket.MSG_WAITALL))
            payload = payload + msg  # See TCP Protocol for Bits Order
            to_read = to_read - len(msg)

        net = Protocol.get_origin_network(magic_nb)

        if net != self._network:
            raise ProtocolException("Protocol Exception : The Origin Network " + net + " is unvalid.")

        result = Protocol.treat_packet(command, length, checksum, payload)

        return result

    def handle_msg(self, rcv_msg):
        command = rcv_msg.getCommand()

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

        else:

            # Version Message Sent to end the Connection
            if version_msg.getVersionNonce() == self._connection_nonce_to_rcv:
                self._connection_nonce_to_rcv = None
                self.__stop_event.set()

    def treat_verack_msg(self, verack_msg):
        if self._handshake_msg["Version Sent"] is True:
            self._handshake_msg["Verack Received"] = True

    def treat_ping_msg(self, ping_msg):
        msg = Pong_Message.Pong_Message(ping_msg.getPingNonce())

        self.send_msg(msg)

    def treat_pong_msg(self, pong_msg):
        if self._ping_nonce == pong_msg.getPongNonce():
            self._ping_nonce = None
            self._last_ping_timestamp = None

    def treat_getaddr_msg(self, getaddr_msg):
        self._network_manager.send_peers(self)

    def treat_addr_msg(self, addr_msg):
        peer_list = addr_msg.get_ip_table()
        self._network_manager.add_peer_to_pool(peer_list)

    def treat_block_msg(self, block_msg):
        pass

    def treat_getblock_msg(self, getblock_msg):
        pass

    def treat_getdata_msg(self, getdata_msg):
        pass

    def treat_getheader_msg(self, getheader_msg):
        pass

    def treat_inv_msg(self, inv_msg):
        pass

    def treat_notfound_msg(self, notfound_msg):
        pass

    def treat_tx_msg(self, tx_msg):
        pass

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

        stdout = open(("Log/Log_Peer_" + self._src_ip + "/Connections/" + self._node_ip + ".txt"), "a")

        ex_type, ex, tb = sys.exc_info()
        traceback.print_exception(ex_type, ex, tb, file=stdout)
        stdout.write('\n\n')

        stdout.close()
