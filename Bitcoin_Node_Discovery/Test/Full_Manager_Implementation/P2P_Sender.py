from threading import Thread, Lock, Event
from Protocol import Protocol
from Protocol.ProtocolException import *
from CrawlingException import *

import queue
import sys
import socket


class P2P_Sender(Thread):
    def __init__(self, socket, origin_network):
        Thread.__init__(self)
        self.socket = socket
        self.in_queue = queue.Queue()
        self.out_queue = queue.Queue()
        self.origin_network = origin_network
        self.handshake_done = False
        self.__stop_event = Event()
        self.__pause_event = Event()
        self.socket_modifier = Lock()
        self.close = False
        self.tracebacks = []
        self.TIMEOUT = 5

    def run(self):
        self.send()

    def disconnect(self):
        self.__pause_event.set()
        self.socket_modifier.acquire()
        self.socket = None
        self.socket_modifier.release()

        self.clean_queue()

    def clean_queue(self):
        while True:
            try:
                self.in_queue.get(False)
                self.in_queue.task_done()
            except queue.Empty:
                break

        while True:
            try:
                feedback = self.out_queue.get(False)
                self.out_queue.task_done()
                if feedback == "Exception":
                    raise UnknownSendMessageFailureException("UnknownReceiveMessageFailure Exception : Failure "
                                                                "detected while cleaning the queue.")
            except queue.Empty:
                break

    def connect(self, socket):
        self.socket_modifier.acquire()
        self.socket = socket
        self.socket_modifier.release()
        self.__pause_event.clear()

    def send(self):
        retry = False
        while not self.__stop_event.isSet():
            nb_timeout = 0
            while not self.__pause_event.isSet():
                self.socket_modifier.acquire()
                try:
                    if not retry:
                        bitcoin_msg = self.in_queue.get(True, timeout=1 / 2)
                        self.in_queue.task_done()
                    self.bitcoin_send_msg(self.socket, bitcoin_msg, self.origin_network)
                    self.out_queue.put("ok")
                    retry = False
                    nb_timeout = 0
                except ProtocolException:
                    self.out_queue.put("ProtocolException")
                    self.out_queue.put(sys.exc_info())
                    pass
                except queue.Empty:
                    pass
                except socket.timeout:
                    if nb_timeout > 3:
                        self.out_queue.put("Disconnected")
                        self.__pause_event.set()
                    nb_timeout = nb_timeout + 1
                except socket.error:
                    self.out_queue.put("Disconnected")
                    self.__pause_event.set()
                except Exception:
                    self.out_queue.put("Exception")
                    self.tracebacks.append(sys.exc_info())
                    self.__pause_event.set()

                self.socket_modifier.release()

    def send_msg(self, bitcoin_msg, timeout):
        try:
            self.in_queue.put(bitcoin_msg, True, timeout)

            feedback = self.out_queue.get(True, timeout)
            self.out_queue.task_done()

            if feedback == "ProtocolException":
                raise SendMessageFailureException(
                    "Send Message Failure Exception : Fail to send a Message to the peer (Protocol Exception).")
            elif feedback == "Exception":
                raise UnknownSendMessageFailureException("Unknown Send Message Failure Exception : Fail to send a Message to the peer.")
            elif feedback == "Disconnected":
                raise DisconnectedSocketException("Send Message Failure Exception : Fail to send a Message from the peer (Broken Socket).")
        except queue.Full:
            raise SendMessageTimeoutException("SendMessageTimeout Exception : Fail to send a Message to the peer (Timeout). ")
        except queue.Empty:
            raise SendMessageTimeoutException("SendMessageTimeout Exception : Fail to send a Message to the peer (Timeout).")

    def get_tracebacks(self):
        return self.tracebacks

    def join(self):
        self.disconnect()
        self.__stop_event.set()
        Thread.join(self)

    def bitcoin_send_msg(self, socket, bitcoin_msg, origin_network):
        msg = Protocol.bitcoin_msg(bitcoin_msg, origin_network)
        socket.send(msg)
