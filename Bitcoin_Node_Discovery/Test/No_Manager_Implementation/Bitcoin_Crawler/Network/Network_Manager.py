import datetime
import sys
import os
import time
import traceback
from threading import Thread, Event

from .P2P_Connection import P2P_Connection
from ..CrawlingException import *
from ..Crawler_Constant import *
from .Network_Constant import *
from .Protocol import Protocol, Protocol_Constant
from .Protocol.Bitcoin_Messages import Addr_Message, GetAddr_Message


class Network_Manager(Thread):

    def __init__(self, src_ip, src_port, src_service, network, measurements_manager, displayer, thread_id,
                 nb_connection_limit, monitor_connections):
        Thread.__init__(self)

        """
                PEER INFORMATIONS
        """

        self._src_ip = src_ip
        self._src_port = src_port
        self._src_service = src_service
        self._network = network

        self._connections = dict()

        self._measurements_manager = measurements_manager

        """
                CRAWLING INFORMATIONS
        """

        self._displayer = displayer

        """
                THREAD MANAGEMENT
        """

        self.__stop_event = Event()

        self._thread_id = thread_id

        self._nb_connection_limit = nb_connection_limit

        self._monitor_connections = monitor_connections

        self.display_progression("Network Manager is starting...")

    """
            GETTERS
    """

    def get_nb_connection(self):
        return len(self._connections.copy())

    def need_more_peer(self):
        return self.get_nb_connection() < self._nb_connection_limit

    def get_connected_peers(self):
        connected_peers = list()

        for peer_info, connection in self._connections.copy().items():
            connected_peers.append(peer_info[0])

        return connected_peers

    """
            THREAD MANAGEMENT
    """

    def run(self):
        try:
            while not self.__stop_event.isSet():
                self.add_active_peers()

                self.crawl()

        except NoMoreIPToProcessException:
            self.display_progression("No More Ip To Process : Crawling Done.")

        except Exception:
            self.error_recording()

        self.kill_connections()
        self.join_connections()

        if self.__stop_event.isSet():
            self.display_progression("Crawling is finished but there are still IPs to process.")

        self._measurements_manager.measurements.set_stop_time(datetime.datetime.now())

    def kill(self):
        self.__stop_event.set()

    def kill_connections(self):
        for connection in self._connections.copy().values():
            connection.kill()

    def join_connections(self):
        for connection in self._connections.copy().values():
            connection.join()

    def is_alive(self):
        return not self.__stop_event.is_set()

    """
            CONNECTION MANAGEMENT
    """

    def connect(self, node_ip, node_port, node_service, connection_timeout=None):
        self.display_progression("Connection to " + str(node_ip) + "...")

        connection = P2P_Connection(self._src_ip, self._src_service, node_ip, node_port, node_service, self._network,
                                    self, self._measurements_manager, self._thread_id, connection_timeout,
                                    self._monitor_connections)

        connection.start()

        self._connections[(node_ip, node_port, node_service)] = connection

    def add_active_peers(self):
        while self.need_more_peer() and not self.__stop_event.isSet():
            peer_info = self.get_ip_to_read_from_measurements()

            if peer_info is not None:
                self.connect(str(peer_info[0]), peer_info[1], Protocol.Protocol_Constant.NODE_NONE,
                             connection_timeout=Crawler_Constant.CONNECTION_TIMEOUT)

            else:
                break

    def remove_dead_peers(self):
        # Check if all connections are still alive
        for peer_info, connection in self._connections.copy().items():

            if not connection.isAlive():
                self._connections.pop(peer_info)

    """
            CRAWLING MANAGEMENT
    """

    def crawl(self):
        self.display_progression("Crawling ...")

        for peer_info, connection in self._connections.copy().items():

            if not connection.isAlive():

                self._connections.pop(peer_info)

                continue

            elif connection.is_handshake_done():

                if connection.get_nb_peer_queries() > Crawler_Constant.NB_QUERY_PER_PEER:
                    connection.kill()

                elif connection.has_last_peer_request_timeout():
                    self.query_peers(connection)

    def query_peers(self, connection=None):
        getaddr_msg = GetAddr_Message.GetAddr_Message()

        if connection is None:
            self.broadcast(getaddr_msg)

            for peer_info, connection in self._connections:
                connection.request_peers()

        else:
            self.send(connection, getaddr_msg)
            connection.request_peers()

    def treat_addr_message(self, connection, addr_msg):
        peer_info = connection.get_node_info()
        node_ip = peer_info[0]

        if not addr_msg.isAdvertisement(node_ip):
            nb_rcv = addr_msg.get_nb_ip()
            ip_table = addr_msg.get_ip_table()

            nb_new = self._measurements_manager.add_ip_to_read(ip_table)

            self.display_progression((str(nb_rcv) + " peers (" + str(nb_new) + " news) has been received from "
                                      + str(node_ip) + "..."))

            self._measurements_manager.add_peer_queried(node_ip, nb_rcv)

            if nb_rcv < 999 or nb_new == 0:
                connection.kill()

    def send_peers(self, connection):
        ips = self._measurements_manager.get_known_ips()

        if len(ips) > 0:
            peers_to_send = dict()
            for node_ip in ips:
                peers_to_send[node_ip] = (Network_Constant.DEFAULT_PORT, Protocol_Constant.NODE_NONE,
                                          time.time() - 1000)

            addr_msg = Addr_Message.Addr_Message(peers_to_send)

            self.send(connection, addr_msg)

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

    """
            MEASUREMENTS MANAGER
    """

    def add_ip_readed_to_measurements(self, node_ip):
        self._measurements_manager.add_ip_readed(node_ip)

    def get_ip_to_read_from_measurements(self):
        self.display_progression("Picking a Peer to query ...")

        peer_info = self._measurements_manager.get_ip_to_read()

        if peer_info is not None:
            ip, port = peer_info

            if ip is not None and port is not None:
                return ip, port

        return None

    """
            THREAD INFORMATION MANAGEMENT
    """

    def error_recording(self):
        directory = "Log/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        directory = "Log/Thread_" + str(self._thread_id) + "/"

        if not os.path.exists(directory):
            os.makedirs(directory)

        stdout = open((directory + "Network_Manager_Log.txt"), "a")

        ex_type, ex, tb = sys.exc_info()
        traceback.print_exception(ex_type, ex, tb, file=stdout)
        stdout.write('\n\n')

        stdout.close()

        self.display_error_message("An error occured (cfr. log for details). Press <q> to end.")

        self.display_progression("Error : Network Manager failed unexpectedly.")

    def display_error_message(self, string):
        if self._displayer is not None:
            self._displayer.display_error_message(string)
        else:
            print(string)

    def display_message(self, string):
        if self._displayer is not None:
            self._displayer.display_message(string)

    def display_progression(self, string):
        if self._displayer is not None:
            self._displayer.display_thread_progression(("Connected to " + str(self.get_nb_connection()) + " peers - "
                                                       + string), self._thread_id)
