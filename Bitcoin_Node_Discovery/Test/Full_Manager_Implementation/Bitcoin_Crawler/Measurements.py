# This File will hold the variables that will be used to gather the measurements done.
# EFFICIENT DATA STRUCTURE USAGE https://www.codementor.io/satwikkansal/python-practices-for-efficient-code-performance-memory-and-usability-aze6oiq65

import datetime
import pytricia
import os
import ipaddress

from threading import Lock

from .CrawlingException import *

'''
        Lock and Semaphore used for recording the peer that will be processed.
'''

IP_TABLE_LOCKER = Lock()


'''
    Service Flags
'''

NODE_NONE = 0  # Nothing
NODE_NETWORK = 1  # Node is capable of serving the complete Block Chain
NODE_GETUTXO = (1 << 1)  # Node is capable of responding to the getutxo protocol request
NODE_BLOOM = (1 << 2)  # Node is capable and willing to handle bloom-filtered connections
NODE_WITNESS = (1 << 3)  # Node can be asked for blocks and transactions including witness data
NODE_XTHIN = (1 << 4)  # Node supports Xtreme Thinblocks
NODE_NETWORK_LIMITED = (1 << 10)  # Node is capable of serving the last 288 blocks (2 days)


class Measurements:

    def __init__(self, network_to_crawl, nb_thread):

        self.network_to_crawl = network_to_crawl

        '''
                            Tables used for recording the peer that will be processed.
        '''

        self.ip_table = pytricia.PyTricia(128)
        self.ip_table_to_read = pytricia.PyTricia(128)

        '''
                             Tables used for recording the different measurements.
        '''

        # This table records statistics on the Version of the Bitcoin Nodes already queried
        self.version_stat = dict()

        # This table records statistics on the Services provided by the Bitcoin Nodes already queried
        self.service_stat = dict()

        # This table records statistics on why connection has failed with Bitcoin Nodes
        self.connection_failed_stat = dict()

        # This table records the IPs of the Bitcoin Nodes considered as active
        self.active_peers = dict()

        # This table records the Duration of the TCP handshake with the Bitcoin Nodes already queried
        self.peers_tcp_handshake_duration = dict()

        # This table records the Duration of the Bitcoin Protocol's handshake with the Bitcoin Nodes already queried
        self.peers_bitcoin_handshake_duration = dict()

        # This table records the number of peer queried per Bitcoin Nodes already queried
        self.peers_queried_nb = dict()

        # This table records statistics on the average time_to_crawl taken to query [nb_query] peer for the thread [thread_nb].
        self.process_ip_stat = dict()
        self.process_ip_stat_aux = dict()

        self.nb_collected = 0
        self.nb_ipv4 = 0
        self.nb_ipv6 = 0
        self.nb_being_read = 0
        self.nb_readed = 0
        self.nb_active = 0

        self.nb_thread = nb_thread
        self.start_time = None
        self.stop_time = None

        for i in range(0, nb_thread):
            self.process_ip_stat[i] = dict()

        for i in range(0, nb_thread):
            self.process_ip_stat_aux[i] = dict()

    def set_stop_time(self, stop_time):
        self.stop_time = stop_time

    def set_start_time(self, start_time):
        self.start_time = start_time

    '''
        Store Measurements into Files
    '''

    def store_measurements(self, end=False, folder="Measurements/"):
        if end is True:
            stop = self.stop_time
        else:
            stop = datetime.datetime.now()

        if stop is None:
            stop = datetime.datetime.now()

        if not os.path.exists(folder):
            os.makedirs(folder)

        """
                STORE PROCESS IP STATISTICS
        """

        stdout = open((folder + "Thread_Statistics"), "w+")

        process_ip_stat = self.process_ip_stat.copy()

        for i in range(0, self.nb_thread):
            stdout.write(("Process  " + str(i) + " : \n"))

            for stat in process_ip_stat[i].items():
                stdout.write(("  " + str(stat[0]) + " peers queried in " + str(stat[1]) + " seconds.\n"))

        stdout.write("\n")

        for i in range(0, self.nb_thread):
            stdout.write(("Process  " + str(i) + " : " + str(
                self.get_mean_process_ip_stat(i)) + ' seconds per peer, per process.\n'))

        stdout.write("Average process time_to_crawl : " + str(self.get_mean_process_ip_stat()) + " seconds per peer.\n")

        stdout.write("\n")

        stat = self.get_process_ip_stat_per_query_nb()

        for i in stat.items():
            stdout.write((str(i[0]) + " peers queried in " + str(i[1]) + " seconds on average.\n"))

        stdout.close()

        """
                    STORE IP TABLES
        """

        stdout = open((folder + "IPv4_Table"), "w+")
        stdout1 = open((folder + "IPv6_Table"), "w+")
        stdout2 = open((folder + "All_IP_Table"), "w+")

        table = list(self.ip_table)

        for i in table:
            ip = i.split("/")[0]
            port = self.ip_table.get(i)
            type = self.get_ip_type(ip)

            stdout2.write((str(ip) + ":" + str(port) + "\n"))

            if type == "ipv4":
                stdout.write((str(ip) + ":" + str(port) + "\n"))
            if type == "ipv6":
                stdout1.write((str(ip) + ":" + str(port) + "\n"))

        stdout.close()
        stdout1.close()
        stdout2.close()

        """
                STORE VERSION STATISTICS
        """

        stdout = open((folder + "Version_Stat"), "w+")

        a = dict(self.version_stat).copy()

        for i in a.items():
            stdout.write(("Version " + str(i[0]) + " : " + str(i[1]) + " peers" + '\n'))

        stdout.close()

        """
                STORE SERVICE STATISTICS
        """

        stdout = open((folder + "Service_Stat"), "w+")

        a = dict(self.service_stat).copy()

        for i in a.items():
            stdout.write(("Service " + str(self.get_service(i[0])) + " : " + str(i[1]) + " peers" + '\n'))

        stdout.close()

        """
                STORE CONNECTION STATISTICS
        """

        stdout = open((folder + "Connection_failed_stat"), "w+")

        a = dict(self.connection_failed_stat).copy()

        for i in a.items():
            stdout.write((str(i[0]) + " : " + str(i[1]) + '\n'))

        stdout.close()

        """
                STORE ACTIVE PEERS STATISTICS
        """

        stdout = open((folder + "Active_Peers"), "a")

        a = dict(self.active_peers).copy()

        for i in a.items():
            stdout.write((str(i[0]) + " : " + str(i[1]) + '\n'))

        stdout.close()

        self.active_peers = dict()

        """
                STORE NUMBER OF PEER QUERIED STATISTICS
        """

        stdout = open((folder + "Peers_Query_nb"), "a")

        a = dict(self.peers_queried_nb).copy()

        for i in a.items():
            stdout.write((str(i[0]) + " : " + str(i[1]) + '\n'))

        stdout.close()

        self.peers_queried_nb = dict()

        """
                STORE TCP HANDSHAKE DURATION STATISTICS
        """

        stdout = open((folder + "Peers_TCP_Handshake_Duration"), "a")

        a = dict(self.peers_tcp_handshake_duration).copy()

        for i in a.items():
            stdout.write((str(i[0]) + " : " + str(i[1]) + '\n'))

        stdout.close()

        """
                STORE TCP HANDSHAKE DURATION STATISTICS
        """

        self.peers_tcp_handshake_duration = dict()

        stdout = open((folder + "Peers_Bitcoin_Handshake_Duration"), "a")

        a = dict(self.peers_bitcoin_handshake_duration).copy()

        for i in a.items():
            stdout.write((str(i[0]) + " : " + str(i[1]) + '\n'))

        stdout.close()

        self.peers_bitcoin_handshake_duration = dict()

        """
                STORE MEASURE INFORMATIONS
        """

        stdout = open((folder + "Measure_Information"), "w+")

        stdout.write(("Crawling started at : " + self.start_time.strftime(
            "%Y-%m-%d %H:%M:%S") + " - Elapsed Time : " + str(
            (stop - self.start_time).total_seconds()) + " seconds.\n"))

        if self.network_to_crawl == "ipv4":
            stdout.write((str(self.nb_readed) + " IPv4 addresses has been processed.\n"))
        elif self.network_to_crawl == "ipv6":
            stdout.write((str(self.nb_readed) + " IPv6 addresses has been processed.\n"))
        else:
            stdout.write((str(self.nb_readed) + "addresses has been processed.\n"))

        stdout.write((str(self.nb_active) + " Active peers has been detected.\n"))

        stdout.close()

    def display_measurements(self, network_to_crawl, details=True):
        print("")
        print(("Crawling began at : " + self.start_time.strftime("%Y-%m-%d %H:%M:%S")))
        print(("Crawling done in " + str(
            (self.stop_time - self.start_time).total_seconds()) + " seconds."))
        print("")

        print("Measurements : ")
        nb_readed = self.get_nb_readed()
        nb_active = self.get_nb_active_peers()
        nb_collected = self.get_nb_collected()

        if network_to_crawl == "ipv4":
            print(str(nb_readed) + " IPv4 Peers has been processed.")
            print(str(nb_collected) + " Peers has been collected (IPv4 + IPv6).")
        elif network_to_crawl == "ipv6":
            print(str(nb_readed) + " IPv6 Peers has been processed.")
            print(str(nb_collected) + " Peers has been collected (IPv4 + IPv6).")
        else:
            print(str(nb_readed) + " Peers has been processed (IPv4 + IPv6).")
            print(str(nb_collected) + " Peers has been collected (IPv4 + IPv6).")

        print((str(nb_active) + " Active peers."))

        if details is True:
            print("\n")
            self.display_failed_connection_stat()
            print("\n")
            self.display_version_table()
            print("\n")
            self.display_service_table()

    def display_failed_connection_stat(self):
        failed_connection_stat = self.get_failed_connection_stat()
        print("Connection Failure Statistics :")
        for i in failed_connection_stat.items():
            print(("Number of connection failed because of \"" + str(i[0]) + "\" = " + str(i[1]) + " peers"))

    def display_version_table(self):
        print("Version Statistics :")
        for i in self.get_version_stat().items():
            print(("Version " + str(i[0]) + " : " + str(i[1]) + " peers"))

    def display_service_table(self):
        print("Service Statistics :")
        for i in self.get_service_stat().items():
            print(("Service " + str(self.get_service(i[0])) + " : " + str(i[1]) + " peers"))

    '''
        Add Measure to the tables recording the Measurements
    '''

    def add_process_ip_stat(self, stat, nb_query, thread_nb):
        if nb_query in self.process_ip_stat[thread_nb]:
            self.process_ip_stat[thread_nb][nb_query] = float(
                ((self.process_ip_stat[thread_nb][nb_query] * self.process_ip_stat_aux[thread_nb][
                    nb_query]) + stat) / (self.process_ip_stat_aux[thread_nb][nb_query] + 1))
            self.process_ip_stat_aux[thread_nb][nb_query] = self.process_ip_stat_aux[thread_nb][nb_query] + 1
        else:
            self.process_ip_stat[thread_nb][nb_query] = stat
            self.process_ip_stat_aux[thread_nb][nb_query] = 1

    def add_peer_bitcoin_handshake_duration(self, ip, handshake_duration):
        self.peers_bitcoin_handshake_duration[ip] = handshake_duration

    def add_peer_tcp_handshake_duration(self, ip, handshake_duration):
        self.peers_tcp_handshake_duration[ip] = handshake_duration

    def add_peer_queried(self, ip, nb):
        if ip in self.peers_queried_nb:
            self.peers_queried_nb[ip] = self.peers_queried_nb[ip] + nb
        else:
            self.peers_queried_nb[ip] = nb

    def add_active_peer(self, ip):
        self.active_peers[ip] = str(datetime.datetime.now().time())
        self.nb_active = self.nb_active + 1

    def add_connection_failed_stat(self, reason):
        if reason in self.connection_failed_stat:
            self.connection_failed_stat[reason] = self.connection_failed_stat[reason] + 1
        else:
            self.connection_failed_stat[reason] = 1

    def add_ip_service(self, ip, service):

        if service in self.service_stat:
            self.service_stat[service] = self.service_stat[service] + 1
        else:
            self.service_stat[service] = 1

    def add_version_stat(self, version):
        if version in self.version_stat:
            self.version_stat[version] = self.version_stat[version] + 1
        else:
            self.version_stat[version] = 1

    '''
        Add the IPs to start the crawling
    '''

    def add_seed_ip_to_read(self, seed_ips):

        for ip in seed_ips:
            try:
                ip = ipaddress.ip_address(str(ip))
                type = self.get_ip_type(str(ip))

            except ValueError as err:
                raise UnknownIPAddressTypeException(str(err))

            if not (ip in self.ip_table):
                self.ip_table.insert(ip, 8333)
                self.nb_collected = self.nb_collected + 1

                if type == self.network_to_crawl or self.network_to_crawl == "any":
                    self.ip_table_to_read.insert(ip, 8333)

                if type == "ipv4":
                    self.nb_ipv4 = self.nb_ipv4 + 1
                elif type == "ipv6":
                    self.nb_ipv6 = self.nb_ipv6 + 1

    '''
        Add IPs that has already been queried to the table
    '''

    def add_ip_readed(self, ip):
        global IP_TABLE_LOCKER

        self.acquire_lock(IP_TABLE_LOCKER)

        self.nb_being_read = self.nb_being_read - 1

        self.nb_readed = self.nb_readed + 1

        IP_TABLE_LOCKER.release()

    def add_ip_to_read(self, ips):
        global IP_TABLE_LOCKER

        self.acquire_lock(IP_TABLE_LOCKER)

        counter = 0
        for i in ips.items():
            try:
                ip = ipaddress.ip_address(i[0])

            except ValueError as err:
                raise UnknownIPAddressTypeException(str(err))

            port, service, timestamp = i[1]

            if not (ip in self.ip_table):
                self.ip_table.insert(ip, port)
                self.nb_collected = self.nb_collected + 1

                type = self.get_ip_type(i[0])

                if type == self.network_to_crawl or self.network_to_crawl == "any":
                    self.ip_table_to_read.insert(ip, port)

                if type == "ipv4":
                    self.nb_ipv4 = self.nb_ipv4 + 1
                elif type == "ipv6":
                    self.nb_ipv6 = self.nb_ipv6 + 1

                counter = counter + 1

        IP_TABLE_LOCKER.release()

        return counter

    def get_mean_process_ip_stat(self, thread_nb=None):
        mean_process_ip_stat = 0.0

        if thread_nb is None:
            temp = self.process_ip_stat.copy()
            for process in temp.items():

                a = 0.0
                i = 0
                for stat in process[1].items():
                    if stat[0] > 0:
                        a = a + stat[1] / stat[0]
                    i = i + 1

                if i > 0:
                    a = a / i

                mean_process_ip_stat = mean_process_ip_stat + a

            mean_process_ip_stat = mean_process_ip_stat / self.nb_thread
        else:
            temp = self.process_ip_stat[thread_nb].copy()
            i = 0

            for stat in temp.items():
                if stat[0] > 0:
                    mean_process_ip_stat = mean_process_ip_stat + stat[1] / stat[0]
                i = i + 1

            if i > 0:
                mean_process_ip_stat = mean_process_ip_stat / i

        return mean_process_ip_stat

    def get_process_ip_stat(self, thread_nb=None):
        if thread_nb is None:
            temp = self.process_ip_stat.copy()
        else:
            temp = self.process_ip_stat[thread_nb].copy()

        return temp

    def get_process_ip_stat_per_query_nb(self):
        temp = self.process_ip_stat.copy()

        stat = dict()
        stat_aux = dict()

        for j in temp.items():
            for i in j[1].items():
                if i[0] in stat:
                    stat[i[0]] = ((stat[i[0]] * stat_aux[i[0]]) + i[1]) / (stat_aux[i[0]] + 1)
                    stat_aux[i[0]] = stat_aux[i[0]] + 1
                else:
                    stat[i[0]] = i[1]
                    stat_aux[i[0]] = 1

        return stat

    def get_nb_active_peers(self):
        return self.nb_active

    def get_service(self, service):
        result = []
        tmp = service

        if tmp == NODE_NONE:
            result.append("NODE_NONE")

        if tmp >= NODE_NETWORK_LIMITED:
            result.append("NODE_NETWORK_LIMITED")
            tmp = tmp - NODE_NETWORK_LIMITED

        if tmp >= NODE_XTHIN:
            result.append("NODE_XTHIN")
            tmp = tmp - NODE_XTHIN

        if tmp >= NODE_WITNESS:
            result.append("NODE_WITNESS")
            tmp = tmp - NODE_WITNESS

        if tmp >= NODE_BLOOM:
            result.append("NODE_BLOOM")
            tmp = tmp - NODE_BLOOM

        if tmp >= NODE_GETUTXO:
            result.append("NODE_GETUTXO")
            tmp = tmp - NODE_GETUTXO

        if tmp >= NODE_NETWORK:
            result.append("NODE_NETWORK")
            tmp = tmp - NODE_NETWORK

        if len(result) == 0 or tmp != 0:
            result.append("OTHER")
        return result

    def get_failed_connection_stat(self):
        return dict(self.connection_failed_stat).copy()

    def get_version_stat(self):
        return self.version_stat.copy()

    def get_service_stat(self):
        return self.service_stat.copy()

    def get_nb_readed(self):
        return self.nb_readed

    def get_nb_collected(self):
        return self.nb_collected

    def get_nb_being_read(self):
        return self.nb_being_read

    def get_nb_to_read(self, type="any"):

        if type == "ipv4":
            return self.nb_ipv4

        elif type == "ipv6":
            return self.nb_ipv6

        else:
            return self.nb_ipv4 + self.nb_ipv6

    def get_ip_type(self, ip):
        ip_addr = ipaddress.ip_address(ip)
        version = ip_addr.version

        if version == 4:
            return "ipv4"
        if version == 6:
            return "ipv6"

    def get_ip_to_read(self):
        global IP_TABLE_LOCKER

        self.acquire_lock(IP_TABLE_LOCKER)

        if self.get_nb_being_read() == 0 and self.get_nb_to_read(self.network_to_crawl) == 0:
            if self.stop_time is None:
                self.stop_time = datetime.datetime.now()

            IP_TABLE_LOCKER.release()

            raise NoMoreIPToProcessException(
                "NoMoreIPToProcess Exception : The crawler has no other node to explore.")

        elif self.get_nb_to_read(self.network_to_crawl) == 0:
            result = None

        else:
            tmp = next(iter(self.ip_table_to_read))

            ip = tmp.split("/")[0]
            port = self.ip_table_to_read.get(tmp)

            self.ip_table_to_read.delete(ip)

            self.nb_being_read = self.nb_being_read + 1

            type = self.get_ip_type(ip)

            if type == "ipv4":
                self.nb_ipv4 = self.nb_ipv4 - 1
            elif type == "ipv6":
                self.nb_ipv6 = self.nb_ipv6 - 1

            result = (ip, port)

        IP_TABLE_LOCKER.release()

        return result

    def get_start_time(self):
        return self.start_time

    def acquire_lock(self, lock, timeout=5):
        res = lock.acquire(True, timeout)

        if res is False:
            raise LockTimeoutException("LockTimeout Exception: Lock has not been acquire in the given time_to_crawl")
