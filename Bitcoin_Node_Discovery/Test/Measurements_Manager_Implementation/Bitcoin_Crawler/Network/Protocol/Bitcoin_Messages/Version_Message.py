from .Bitcoin_Message import *
from ..Util import *


def treat_version_packet(payload):
    version = payload[0:4]

    services = payload[4:12]

    timestamp = payload[12:20]

    addr_rcv = payload[20:46]

    receiver_service, receiver_ip, receiver_port = treat_network_address(addr_rcv, version_msg=True)

    addr_from = payload[46:72]

    sender_service, sender_ip, sender_port = treat_network_address(addr_from, version_msg=True)

    nonce = payload[72:80]

    return Version_Message(int.from_bytes(version, byteorder="little"), sender_ip,
                           sender_port, sender_service, receiver_ip, receiver_port,
                           receiver_service, int.from_bytes(nonce, byteorder="little")), payload[80::]


class Version_Message(Bitcoin_Message):
    def __init__(self, version, sender_ip, sender_port, sender_service, receiver_ip_address, receiver_port,
                 receiver_service, version_nonce):
        super().__init__("version")

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
        receiver = get_network_address_field(self.receiver_service, self.receiver_ip_address, self.receiver_port, True)
        for i in receiver:
            payload.append(i)

        # Network address of the emitting node
        sender = get_network_address_field(self.sender_service, self.sender_ip, self.sender_port, True)
        for i in sender:
            payload.append(i)

        # Random nonce to authentify the connection
        nonce = self.version_nonce.to_bytes(8, byteorder='little')
        for i in nonce:
            payload.append(i)

        # User Agent length
        user_agent_length = (0).to_bytes(1, byteorder='little')
        payload.append(user_agent_length[0])

        # Last Block received by the emitting node
        start_height = (0).to_bytes(4, byteorder='little')
        for i in start_height:
            payload.append(i)

        # Relay Field --> If not present or True = Node wants new transaction to be announced without Bloom Filters
        relay = (1).to_bytes(1, byteorder='little')

        payload.append(relay[0])

        return payload

    def __eq__(self, other):
        return type(self) is type(
            other) and self.version == other.version and self.version == other.version and self.sender_ip == other.sender_ip \
               and self.sender_port == other.sender_port and self.sender_service == other.sender_service \
               and self.receiver_ip_address == other.receiver_ip_address and self.receiver_port == other.receiver_port \
               and self.receiver_service == other.receiver_service and self.version_nonce == other.version_nonce
