from ..Util import *
from .Bitcoin_Message import *


def treat_ping_packet(payload):
    if len(payload) > 8:
        raise DiscardedPacketException((
                "DiscardedPacket Exception : The length of the PING payload is not expected (" + str(
            len(payload)) + " != 8."))

    return Ping_Message(ping_nonce=int.from_bytes(payload, byteorder="little")), bytearray()


# PING Message is sent periodically to help confirm that the receiving peer is still connected.
class Ping_Message(Bitcoin_Message):
    def __init__(self, ping_nonce):
        super().__init__("ping")
        self.ping_nonce = ping_nonce

    def getPingNonce(self):
        return self.ping_nonce

    def getPayload(self):
        payload = bytearray()

        rand_nonce = self.ping_nonce.to_bytes(8, byteorder='little')

        for i in rand_nonce:
            payload.append(i)

        return payload

    def __eq__(self, other):
        return type(self) is type(other) and self.ping_nonce == other.ping_nonce
