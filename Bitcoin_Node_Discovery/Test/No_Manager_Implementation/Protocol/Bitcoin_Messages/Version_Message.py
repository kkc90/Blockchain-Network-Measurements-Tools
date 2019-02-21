from .Bitcoin_Message import Bitcoin_Message
from ..ProtocolException import *
import math
import time
import ipaddress


# VERSION Message provides information about the transmitting nod to the receiving node at the beginning of a connection
class Version_Message(Bitcoin_Message):
    def __init__(self, command, version, sender_ip, sender_port, sender_service, receiver_ip_address, receiver_port,
                 receiver_service, version_nonce):
        super().__init__(command)
        self.version = version
        self.sender_ip = sender_ip
        self.sender_port = sender_port
        self.sender_service = sender_service
        self.receiver_ip_address = receiver_ip_address
        self.receiver_port = receiver_port
        self.receiver_service = receiver_service
        self.version_nonce = version_nonce

    def getVersion(self):
        return self.version

    def getProtocol(self):
        return self.origin_network

    def getCommand(self):
        return self.command

    def getReceiverService(self):
        return self.receiver_service

    def getSenderIp(self):
        return self.sender_ip

    def getSenderPort(self):
        return self.sender_port

    def getSenderService(self):
        return self.sender_service

    def getReceiverIP(self):
        return self.receiver_ip_address

    def getReceiverPort(self):
        return self.receiver_port

    def getVersionNonce(self):
        return self.version_nonce

    def getPayload(self):
        payload = bytearray()

        # Version Field
        version = self.version.to_bytes(4, byteorder='little')
        for i in version:
            payload.append(i)

        # Services Field
        service = self.sender_service.to_bytes(8, byteorder='little')
        for i in service:
            payload.append(i)

        # Timestamp Fields
        timestamp = int(time.time()).to_bytes(8, byteorder='little')
        for i in timestamp:
            payload.append(i)

        # Network address of the receiving node
        receiver = bitcoin_network_address_field(self.receiver_service, self.receiver_ip_address, self.receiver_port,
                                                 True)
        for i in receiver:
            payload.append(i)

        # Network address of the emitting node
        sender = bitcoin_network_address_field(self.sender_service, self.sender_ip, self.sender_port, True)
        for i in sender:
            payload.append(i)

        # Random nonce to authentify the connection
        nonce = self.version_nonce.to_bytes(8, byteorder='little')
        for i in nonce:
            payload.append(i)

        # User Agent length
        user_agent_length = (0).to_bytes(1, byteorder='little')
        payload.append(user_agent_length[0])

        # User Agent
        # NOT USED FOR NOW

        # Last Block received by the emitting node
        start_height = (0).to_bytes(4, byteorder='little')
        for i in start_height:
            payload.append(i)

        # Relay Field --> If not present = Node wants new transaction to be announced
        relay = (0).to_bytes(1, byteorder='little')
        payload.append(relay[0])
        return payload


def bitcoin_network_address_field(service, ip_address, port, is_version=False, advertising=False,
                                  timestamp=float("nan")):
    net_addr = bytearray()
    if not is_version:
        if advertising:
            timestamp = time.time().to_bytes(4, byteorder='little')
        else:
            if math.isnan(timestamp):
                raise MissingTimestampExeception(
                    "MissingTimestamp Exception : You have to mention the last time you connect to the node in the Version Message.")

    # Service Fields mentionning the service offer by the device associated to the IP Address
    service_byte = service.to_bytes(8, byteorder='little')
    for i in service_byte:
        net_addr.append(i)

    ip_address_bytes = encode_ip(ip_address)
    # to_pad = 16 - len(ip_address_bytes)

    # ip_address_bytes = ip_address_bytes + (0x00).to_bytes((to_pad), byteorder='little')

    for i in ip_address_bytes:
        net_addr.append(i)

    port_bytes = port.to_bytes(2, byteorder='big')

    for i in port_bytes:
        net_addr.append(i)
    return net_addr


def encode_ip(ip):
    if get_ip_type(ip) == "ipv4":
        result = bytearray()
        result = result + 0x00.to_bytes(10, byteorder='little') + 0xFFFF.to_bytes(2, byteorder='little')
        ip_parsed = ip.split(".")
        for i in ip_parsed:
            result.append(int(i))

    else:
        ip_add = ipaddress.ip_address(ip)
        result = bytearray()
        result = result + int(ip_add).to_bytes(16, byteorder="big")
    return result


def get_ip_type(ip_addr):
    ip = ipaddress.ip_address(ip_addr)

    version = ip.version
    if version == 4:
        return "ipv4"
    if version == 6:
        return "ipv6"
