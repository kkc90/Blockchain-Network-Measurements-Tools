from threading import Thread, Lock, Event
from .Protocol import Protocol
from .Protocol.ProtocolException import *
from .CrawlingException import *

import socket
import queue
import sys


class P2P_Receiver(Thread):

    def __init__(self, socket, origin_network):
        Thread.__init__(self)
        self.socket = socket
        self.out_queue = queue.Queue()
        self.handshake_done = False
        self.origin_network = origin_network
        self.__stop_event = Event()
        self.__pause_event = Event()
        self.__pause_event.set()
        self.socket_modifier = Lock()
        self.tracebacks = []

    def run(self):
        self.listen()

    def disconnect(self):
        self.__pause_event.set()
        self.socket_modifier.acquire()
        self.socket = None
        self.socket_modifier.release()

        self.clean_queue()

    def clean_queue(self):
        while True:
            try:
                feedback = self.out_queue.get(False)
                self.out_queue.task_done()

                if feedback == "Exception":
                    raise UnknownReceiveMessageFailureException("UnknownReceiveMessageFailure Exception : Failure "
                                                                "detected while cleaning the queue.")
            except queue.Empty:
                break

    def connect(self, socket):
        self.socket_modifier.acquire()
        self.socket = socket
        self.socket_modifier.release()
        self.__pause_event.clear()

    def rcv_msg(self, timeout):
        try:
            result = self.out_queue.get(True, timeout)
            self.out_queue.task_done()

            if result == "Exception":
                raise UnknownReceiveMessageFailureException(
                    "Unknown Receive Message Failure Exception : Fail to Receive a Message from the peer.")
            elif result == "Disconnected":
                raise DisconnectedSocketException(
                    "Receive Message Failure Exception : Fail to Receive a Message from the peer (Broken Socket).")
        except queue.Empty:
            raise ReceiveMessageTimeoutException("Receive Message Timeout Exception : Fail to Receive a Message from the peer (Timeout).")

        return result

    def get_tracebacks(self):
        return self.tracebacks

    def listen(self):
        retry = False
        while not self.__stop_event.isSet():
            nb_timeout = 0
            while not self.__pause_event.isSet():
                self.socket_modifier.acquire()
                try:
                    if not retry:
                        result = self.bitcoin_rcv_msg()
                    self.out_queue.put(result, block=True, timeout=1 / 2)
                    retry = False
                    nb_timeout = 0
                except ProtocolException:
                    pass
                except socket.timeout:
                    if nb_timeout > 3:
                        self.out_queue.put("Disconnected")
                        self.__pause_event.set()
                    nb_timeout = nb_timeout + 1
                except socket.error:
                    self.out_queue.put("Disconnected")
                    self.__pause_event.set()
                except queue.Full:
                    retry = True
                    pass
                except Exception:
                    self.out_queue.put("Exception")
                    self.tracebacks.append(sys.exc_info())
                    self.__pause_event.set()

                self.socket_modifier.release()

    def join(self):
        self.disconnect()
        self.__stop_event.set()
        Thread.join(self)

    # If bitcoin_command unspecified, this function will treat uncoming packets no matter which commands received.
    def bitcoin_rcv_msg(self):
        magic_nb = bytearray(self.socket.recv(4, socket.MSG_WAITALL))

        command = bytearray(self.socket.recv(12, socket.MSG_WAITALL))

        length = bytearray(self.socket.recv(4, socket.MSG_WAITALL))
        payload_length = int.from_bytes(length, byteorder='little')

        checksum = bytearray(self.socket.recv(4, socket.MSG_WAITALL))

        to_read = payload_length

        readed = 0
        payload = bytearray()

        while to_read > 0:
            if to_read > 1024:
                readed = 1024
            else:
                readed = to_read

            msg = bytearray(self.socket.recv(readed, socket.MSG_WAITALL))
            payload = payload + msg  # See TCP Protocol for Bits Order
            to_read = to_read - len(msg)

        net = Protocol.get_origin_network(magic_nb)
        rcv_command = Protocol.get_command(command)

        if net != self.origin_network:
            raise ProtocolException("Protocol Exception : The Origin Network " + net + " is unvalid.")

        result = Protocol.bitcoin_treat_packet(net, rcv_command, length, checksum, payload)

        return result
