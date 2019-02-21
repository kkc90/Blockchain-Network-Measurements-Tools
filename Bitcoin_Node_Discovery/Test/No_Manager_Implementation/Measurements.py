# This File will hold the variables that will be used to gather the measurements done.
# EFFICIENT DATA STRUCTURE USAGE https://www.codementor.io/satwikkansal/python-practices-for-efficient-code-performance-memory-and-usability-aze6oiq65

import datetime
import pytricia
from threading import Semaphore, Lock

from CrawlingException import *
from Protocol.Protocol import *

'''
    Tables used for recording the peer that has already been processed and the peer that will be processed.
        They are classified into IPv4 and IPv6 tables for convenience.
'''

IP_TABLE = pytricia.PyTricia(128)

IP_TABLE_TO_READ = pytricia.PyTricia(128)  # ip:port

IP_TABLE_LOCKER = Lock()

# Those are the Semaphore that will be used to monitor the number of peer in the tables
TABLE_TO_READ_SEMAPHORE = Semaphore()

'''
                                Tables used for recording the different measurements.
    NB: They do not need to be protected with mutexes as there is only one producer(Measurements Manager) and one consumer (Displayer).
'''

# This table records statistics on the Version of the Bitcoin Nodes already queried
VERSION_STAT = dict()
VERSION_STAT_LOCKER = Lock()

# This table records statistics on the Services provided by the Bitcoin Nodes already queried
SERVICE_STAT = dict()
SERVICE_STAT_LOCKER = Lock()

# This table records statistics on why connection has failed with Bitcoin Nodes
CONNECTION_FAILED_STAT = dict()
CONNECTION_FAILED_STAT_LOCKER = Lock()

# This table records the IPs of the Bitcoin Nodes considered as active
ACTIVE_PEERS = dict()
ACTIVE_PEERS_LOCKER = Lock()

# This table records the Duration of the TCP handshake with the Bitcoin Nodes already queried
PEERS_TCP_HANDSHAKE_DURATION = dict()
PEERS_TCP_HANDSHAKE_DURATION_LOCKER = Lock()

# This table records the Duration of the Bitcoin Protocol's handshake with the Bitcoin Nodes already queried
PEERS_BITCOIN_HANDSHAKE_DURATION = dict()
PEERS_BITCOIN_HANDSHAKE_DURATION_LOCKER = Lock()

# This table records the number of peer queried per Bitcoin Nodes already queried
PEERS_QUERIED_NB = dict()
PEERS_QUERIED_NB_LOCKER = Lock()

# This table records statistics on the average time taken to query [nb_query] peer for the thread [thread_nb].
PROCESS_IP_STAT = dict()
PROCESS_IP_STAT_AUX = dict()
PROCESS_IP_STAT_LOCKER = Lock()

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

    def __init__(self, network_to_crawl, nb_thread, start_time):
        global TABLE_TO_READ_SEMAPHORE

        TABLE_TO_READ_SEMAPHORE.acquire()

        self.network_to_crawl = network_to_crawl

        self.nb_ipv4 = 0
        self.nb_ipv6 = 0
        self.nb_being_read = 0
        self.nb_readed = 0
        self.nb_active = 0

        self.nb_thread = nb_thread
        self.start_time = start_time

        for i in range(0, nb_thread):
            PROCESS_IP_STAT[i] = dict()

        for i in range(0, nb_thread):
            PROCESS_IP_STAT_AUX[i] = dict()

    '''
        Store Measurements into Files
    '''

    def store_measurements(self):
        global IP_TABLE_TO_READ

        global VERSION_STAT

        global SERVICE_STAT

        global CONNECTION_FAILED_STAT

        global ACTIVE_PEERS

        global PEERS_TCP_HANDSHAKE_DURATION

        global PEERS_BITCOIN_HANDSHAKE_DURATION

        global IP_TABLE

        global PROCESS_IP_STAT

        global PEERS_QUERIED_NB

        stop = datetime.datetime.now()

        stdout = open("Measurements/Process_IP_Stat", "w+")

        process_ip_stat = PROCESS_IP_STAT.copy()

        for i in range(0, self.nb_thread):
            stdout.write(("Process  " + str(i) + " : \n"))

            for stat in process_ip_stat[i].items():
                stdout.write(("  " + str(stat[0]) + " peers queried in " + str(stat[1]) + " seconds.\n"))

        stdout.write("\n")

        for i in range(0, self.nb_thread):
            stdout.write(("Process  " + str(i) + " : " + str(
                self.get_mean_process_ip_stat(i)) + ' seconds per peer, per process.\n'))

        stdout.write("Average process time : " + str(self.get_mean_process_ip_stat()) + " seconds per peer.\n")

        stdout.write("\n")

        stat = self.get_process_ip_stat_per_query_nb()

        for i in stat.items():
            stdout.write((str(i[0]) + " peers queried in " + str(i[1]) + " seconds on average.\n"))

        stdout.close()

        stdout = open("Measurements/IPV4_Table", "w+")
        stdout1 = open("Measurements/IPV6_Table", "w+")
        stdout2 = open("Measurements/IP_Table", "w+")

        table = list(IP_TABLE)

        for i in table:
            ip = ipaddress.ip_address(i.split("/")[0])
            type = self.get_ip_type(ip)

            stdout2.write((str(ip) + "\n"))

            if type == "ipv4":
                stdout.write((str(ip) + "\n"))
            if type == "ipv6":
                stdout1.write((str(ip) + "\n"))

        stdout.close()
        stdout1.close()
        stdout2.close()

        stdout = open("Measurements/Version_Stat", "w+")

        a = dict(VERSION_STAT).copy()

        for i in a.items():
            stdout.write((str(i[0]) + " : " + str(i[1]) + '\n'))

        stdout.close()

        stdout = open("Measurements/Service_Stat", "w+")

        a = dict(SERVICE_STAT).copy()

        for i in a.items():
            stdout.write((str(i[0]) + " : " + str(i[1]) + '\n'))

        stdout.close()

        stdout = open("Measurements/Connection_failed_stat", "w+")

        a = dict(CONNECTION_FAILED_STAT).copy()

        for i in a.items():
            stdout.write((str(i[0]) + " : " + str(i[1]) + '\n'))

        stdout.close()

        stdout = open("Measurements/Active_Peers", "a")

        a = dict(ACTIVE_PEERS).copy()

        for i in a.items():
            stdout.write((str(i[0]) + " : " + str(i[1]) + '\n'))

        stdout.close()

        ACTIVE_PEERS = dict()

        stdout = open("Measurements/Peers_Query_nb", "a")

        a = dict(PEERS_QUERIED_NB).copy()

        for i in a.items():
            stdout.write((str(i[0]) + " : " + str(i[1]) + '\n'))

        stdout.close()

        PEERS_QUERIED_NB = dict()

        stdout = open("Measurements/Peers_TCP_Handshake_Duration", "a")

        a = dict(PEERS_TCP_HANDSHAKE_DURATION).copy()

        for i in a.items():
            stdout.write((str(i[0]) + " : " + str(i[1]) + '\n'))

        stdout.close()

        PEERS_TCP_HANDSHAKE_DURATION = dict()

        stdout = open("Measurements/Peers_Bitcoin_Handshake_Duration", "a")

        a = dict(PEERS_BITCOIN_HANDSHAKE_DURATION).copy()

        for i in a.items():
            stdout.write((str(i[0]) + " : " + str(i[1]) + '\n'))

        stdout.close()

        PEERS_BITCOIN_HANDSHAKE_DURATION = dict()

        stdout = open("Measurements/Measure_Information", "w+")

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

    '''
        Add Measure to the tables recording the Measurements
    '''

    def add_process_ip_stat(self, stat, nb_query, thread_nb):
        global PROCESS_IP_STAT
        global PROCESS_IP_STAT_AUX
        global PROCESS_IP_STAT_LOCKER

        PROCESS_IP_STAT_LOCKER.acquire()

        if nb_query in PROCESS_IP_STAT[thread_nb]:
            PROCESS_IP_STAT[thread_nb][nb_query] = float(
                ((PROCESS_IP_STAT[thread_nb][nb_query] * PROCESS_IP_STAT_AUX[thread_nb][
                    nb_query]) + stat) / (PROCESS_IP_STAT_AUX[thread_nb][nb_query] + 1))
            PROCESS_IP_STAT_AUX[thread_nb][nb_query] = PROCESS_IP_STAT_AUX[thread_nb][nb_query] + 1
        else:
            PROCESS_IP_STAT[thread_nb][nb_query] = stat
            PROCESS_IP_STAT_AUX[thread_nb][nb_query] = 1

        PROCESS_IP_STAT_LOCKER.release()

    def add_peer_bitcoin_handshake_duration(self, ip, handshake_duration):
        global PEERS_BITCOIN_HANDSHAKE_DURATION
        global PEERS_BITCOIN_HANDSHAKE_DURATION_LOCKER

        PEERS_BITCOIN_HANDSHAKE_DURATION_LOCKER.acquire()

        PEERS_BITCOIN_HANDSHAKE_DURATION[ip] = handshake_duration

        PEERS_BITCOIN_HANDSHAKE_DURATION_LOCKER.release()

    def add_peer_tcp_handshake_duration(self, ip, handshake_duration):
        global PEERS_TCP_HANDSHAKE_DURATION
        global PEERS_TCP_HANDSHAKE_DURATION_LOCKER

        PEERS_TCP_HANDSHAKE_DURATION_LOCKER.acquire()

        PEERS_TCP_HANDSHAKE_DURATION[ip] = handshake_duration

        PEERS_TCP_HANDSHAKE_DURATION_LOCKER.release()

    def add_peer_queried(self, ip, nb):
        global PEERS_QUERIED_NB
        global PEERS_QUERIED_NB_LOCKER

        PEERS_QUERIED_NB_LOCKER.acquire()

        if ip in PEERS_QUERIED_NB:
            PEERS_QUERIED_NB[ip] = PEERS_QUERIED_NB[ip] + nb
        else:
            PEERS_QUERIED_NB[ip] = nb

        PEERS_QUERIED_NB_LOCKER.release()

    def add_active_peer(self, ip):
        global ACTIVE_PEERS
        global ACTIVE_PEERS_LOCKER

        ACTIVE_PEERS_LOCKER.acquire()

        ACTIVE_PEERS[ip] = str(datetime.datetime.now().time())
        self.nb_active = self.nb_active + 1

        ACTIVE_PEERS_LOCKER.release()

    def add_connection_failed_stat(self, reason):
        global CONNECTION_FAILED_STAT
        global CONNECTION_FAILED_STAT_LOCKER

        CONNECTION_FAILED_STAT_LOCKER.acquire()

        if reason in CONNECTION_FAILED_STAT:
            CONNECTION_FAILED_STAT[reason] = CONNECTION_FAILED_STAT[reason] + 1
        else:
            CONNECTION_FAILED_STAT[reason] = 1

        CONNECTION_FAILED_STAT_LOCKER.release()

    def add_IP_Service(self, ip, service):
        global SERVICE_STAT
        global SERVICE_STAT_LOCKER

        SERVICE_STAT_LOCKER.acquire()

        i = str(service)

        if i in SERVICE_STAT:
            SERVICE_STAT[i] = SERVICE_STAT[i] + 1
        else:
            SERVICE_STAT[i] = 1

        SERVICE_STAT_LOCKER.release()

    def add_version_stat(self, version):
        global VERSION_STAT
        global VERSION_STAT_LOCKER

        VERSION_STAT_LOCKER.acquire()

        if version in VERSION_STAT:
            VERSION_STAT[version] = VERSION_STAT[version] + 1
        else:
            VERSION_STAT[version] = 1

        VERSION_STAT_LOCKER.release()

    def add_seed_IP_to_read(self, seed_file):
        global IP_TABLE_TO_READ
        global TABLE_TO_READ_SEMAPHORE

        ips = self.get_ips_from_file(seed_file)

        for ip in ips:
            ip = ipaddress.ip_address(str(A_ip))
            type = self.get_ip_type(ip)

            if not (ip in IP_TABLE):
                IP_TABLE.insert(ip, 8333)

                if (type == self.network_to_crawl or self.network_to_crawl == "any"):
                    IP_TABLE_TO_READ.insert(ip, 8333)
                    TABLE_TO_READ_SEMAPHORE.release()

                if (type == "ipv4"):
                    self.nb_ipv4 = self.nb_ipv4 + 1
                elif (type == "ipv6"):
                    self.nb_ipv6 = self.nb_ipv6 + 1

    def get_ips_from_file(self, file):
        stdout = open(file, "r")
        ips = list()

        for i in stdout:
            ips.append(i.split("\n")[0])

        stdout.close()
        return ips

    '''
        Add the IPs queried from the DNS Servers
    '''

    def add_dns_list_IP_to_read(self, ips):
        global IP_TABLE_TO_READ
        global TABLE_TO_READ_SEMAPHORE

        for A_ip in ips:
            ip = ipaddress.ip_address(str(A_ip))
            type = self.get_ip_type(ip)

            if not (ip in IP_TABLE):
                IP_TABLE.insert(ip, 8333)

                if (type == self.network_to_crawl or self.network_to_crawl == "any"):
                    IP_TABLE_TO_READ.insert(ip, 8333)
                    TABLE_TO_READ_SEMAPHORE.release()

                if (type == "ipv4"):
                    self.nb_ipv4 = self.nb_ipv4 + 1
                elif (type == "ipv6"):
                    self.nb_ipv6 = self.nb_ipv6 + 1

    '''
        Add IPs that has already been queried to the table
    '''

    def add_IP_readed(self, ip):
        try:
            ipaddress.ip_address(ip)
        except ValueError as err:
            raise UnknownIPAddressTypeException(str(err))

        self.nb_being_read = self.nb_being_read - 1
        self.nb_readed = self.nb_readed + 1

    def treatAddrPacket(self, rcv_msg):
        global IP_TABLE

        global IP_TABLE_TO_READ
        global TABLE_TO_READ_SEMAPHORE

        self.acquire_lock(IP_TABLE_LOCKER)

        tmp = rcv_msg.get_IP_Table()
        counter = 0

        for i in tmp.items():
            ip = ipaddress.ip_address(i[0])

            if not (ip in IP_TABLE):
                IP_TABLE.insert(ip, 8333)

                type = self.get_ip_type(ip)

                if (type == self.network_to_crawl or self.network_to_crawl == "any"):
                    IP_TABLE_TO_READ.insert(ip, 8333)
                    TABLE_TO_READ_SEMAPHORE.release()

                if (type == "ipv4"):
                    self.nb_ipv4 = self.nb_ipv4 + 1
                elif (type == "ipv6"):
                    self.nb_ipv6 = self.nb_ipv6 + 1

                counter = counter + 1

        IP_TABLE_LOCKER.release()

        return counter

    def get_mean_process_ip_stat(self, thread_nb=None):
        global PROCESS_IP_STAT

        mean_process_ip_stat = 0.0

        if thread_nb is None:
            temp = PROCESS_IP_STAT.copy()
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
            temp = PROCESS_IP_STAT[thread_nb].copy()
            i = 0

            for stat in temp.items():
                if stat[0] > 0:
                    mean_process_ip_stat = mean_process_ip_stat + stat[1] / stat[0]
                i = i + 1

            if i > 0:
                mean_process_ip_stat = mean_process_ip_stat / i

        return mean_process_ip_stat

    def get_process_ip_stat(self, thread_nb=None):
        global PROCESS_IP_STAT

        if thread_nb is None:
            temp = PROCESS_IP_STAT.copy()
        else:
            temp = PROCESS_IP_STAT[thread_nb].copy()

        return temp

    def get_process_ip_stat_per_query_nb(self):
        global PROCESS_IP_STAT

        temp = PROCESS_IP_STAT.copy()

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
        global ACTIVE_PEERS

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
        global CONNECTION_FAILED_STAT

        return dict(CONNECTION_FAILED_STAT).copy()

    def get_version_stat(self):
        global VERSION_STAT

        return VERSION_STAT.copy()

    def get_service_stat(self):
        global SERVICE_STAT

        return SERVICE_STAT.copy()

    def get_nb_readed(self):
        return self.nb_readed

    def get_nb_being_read(self):
        return self.nb_being_read

    def get_nb_to_read(self, type="any"):

        if type == "ipv4":
            return self.nb_ipv4
        elif type == "ipv6":
            return self.nb_ipv6
        else:
            return self.nb_ipv4 + self.nb_ipv6

    def get_ip_type(self, ip_addr):
        version = ip_addr.version

        if version == 4:
            return "ipv4"
        if version == 6:
            return "ipv6"

    def get_IP_to_read(self):
        global IP_TABLE_TO_READ
        global TABLE_TO_READ_SEMAPHORE
        global IP_TABLE_LOCKER

        i = 0
        while not TABLE_TO_READ_SEMAPHORE.acquire(timeout=5):
            if self.get_nb_being_read() == 0:
                raise NoMoreIPToProcessException(
                    "NoMoreIPToProcess Exception : The crawler has no other node to explore.")

            if i > 3:
                raise SemaphoreTimeoutException(
                    " Too much attempt to query the IP database without success (no ip to process in the queue)")
            i = i + 1

        self.acquire_lock(IP_TABLE_LOCKER)

        result = ipaddress.ip_address(next(iter(IP_TABLE_TO_READ)).split("/")[0])
        IP_TABLE_TO_READ.delete(result)

        self.nb_being_read = self.nb_being_read + 1

        IP_TABLE_LOCKER.release()

        try:
            type = self.get_ip_type(result)
        except ValueError as err:
            raise UnknownIPAddressTypeException(str(err))

        if type == "ipv4":
            self.nb_ipv4 = self.nb_ipv4 - 1
        elif type == "ipv6":
            self.nb_ipv6 = self.nb_ipv6 - 1

        return result

    def get_start_time(self):
        return self.start_time

    def acquire_lock(self, lock, timeout=5):
        res = False

        res = lock.acquire(True, timeout)

        if res is False:
            raise LockTimeoutException("LockTimeout Exception: Lock has not been acquire in the given time")
