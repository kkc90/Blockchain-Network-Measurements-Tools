from ..Util import *
from .Bitcoin_Message import *


def treat_pong_packet(payload):
    if len(payload) > 8:
        raise DiscardedPacketException((
                "DiscardedPacket Exception : The length of the PONG payload is not expected (" + str(
            len(payload)) + " != 8."))

    return Pong_Message(pong_nonce=int.from_bytes(payload, byteorder="little"))


# PONG Message replies to a ping message, proving to the pinging node that the ponging node is still allive.
class Pong_Message(Bitcoin_Message):
    def __init__(self, pong_nonce):
        super().__init__("pong")
        self.pong_nonce = pong_nonce

    def getPongNonce(self):
        return self.pong_nonce

    def getPayload(self):
        payload = bytearray()

        rand_nonce = self.pong_nonce.to_bytes(8, byteorder='little')

        for i in rand_nonce:
            payload.append(i)

        return payload

    def __eq__(self, other):
        return self.pong_nonce == other.pong_nonce
