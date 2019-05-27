from .Bitcoin_Message import *
from ..Util import *


class Addr_Message(Bitcoin_Message):
    def __init__(self, ip_table):
        super().__init__("addr")
        self.ip_table = ip_table
        self.nb_entries = len(ip_table)

    def get_ip_table(self):
        return self.ip_table

    def get_nb_ip(self):
        return self.nb_entries

    def isAdvertisement(self, my_ip):
        if self.nb_entries == 1 and my_ip in self.ip_table:
            return True
        else:
            return False

    def getPayload(self):
        payload = bytearray()

        var_int = get_variable_length_integer(self.nb_entries)

        addr_list = get_addr_list(self.ip_table)

        payload = payload + var_int + addr_list

        return payload

    def __eq__(self, other):
        return type(self) is type(other) and self.nb_entries == other.nb_entries and same_ip_table(self.ip_table,
                                                                                                   other.ip_table)


def same_ip_table(iptable1, iptable2):
    a = len(iptable1)
    b = len(iptable2)

    if a == b:
        i = 0
        c = list(iptable1.items())
        while i < a:
            ip, (port1, service1, timestamp1) = c[i]
            port2, service2, timestamp2 = iptable2[ip]

            if port1 != port2 or service1 != service2 or int(timestamp1) != int(timestamp2):
                return False

            i = i + 1

        return True

    else:
        return False


def get_addr_list(ip_table):
    addr_list = bytearray()

    for ip in ip_table:
        port, service, timestamp = ip_table[ip]
        net_addr = get_network_address_field(service, ip, port, timestamp=timestamp)
        addr_list = addr_list + net_addr

    return addr_list


def treat_addr_list(nb_entries, addr_list):
    ip_table = {}

    i = 0
    while i < nb_entries:
        net_addr = addr_list[
                   i * Protocol_Constant.NETWORK_ADDRESS_SIZE:i * Protocol_Constant.NETWORK_ADDRESS_SIZE
                                                              + Protocol_Constant.NETWORK_ADDRESS_SIZE]

        timestamp, service, ip, port = treat_network_address(net_addr)

        ip_table[ip] = (port, service, timestamp)

        i = i + 1

    return ip_table, addr_list[i * Protocol_Constant.NETWORK_ADDRESS_SIZE::]


def treat_addr_packet(payload):
    nb_entries, entries = treat_variable_length_list(payload)

    ip_table, payload_left = treat_addr_list(nb_entries, entries)

    return Addr_Message(ip_table), payload_left
