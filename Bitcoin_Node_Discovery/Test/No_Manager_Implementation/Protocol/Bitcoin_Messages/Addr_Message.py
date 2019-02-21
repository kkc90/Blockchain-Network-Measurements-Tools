from .Bitcoin_Message import Bitcoin_Message
from ..ProtocolException import *


# ADDR Message relays connection information for peers on the network.
# Sending Addr Message not supported yet
class Addr_Message(Bitcoin_Message):
    def __init__(self, command):
        super().__init__(command)
        self.IP_Table_service = {}
        self.IP_Table = {}
        self.nb_entries = 0

    def add_IP_Service(self, ip, service):
        self.IP_Table_service[ip] = service

    def add_IP_Table(self, ip, port):
        self.IP_Table[ip] = port
        self.nb_entries = self.nb_entries + 1

    def get_IP_Table(self):
        return self.IP_Table

    def get_IP_Service(self):
        return self.IP_Table_service

    def get_IP_Nb(self):
        return self.nb_entries

    def isAdvertisement(self, my_ip):
        if self.nb_entries == 1 and my_ip in self.IP_Table:
            return True
        else:
            return False

    def getPayload(self):
        raise NotSupportedMessageException("NotSupportedMessage Exception : Sending Addr Messages is not supported.")
