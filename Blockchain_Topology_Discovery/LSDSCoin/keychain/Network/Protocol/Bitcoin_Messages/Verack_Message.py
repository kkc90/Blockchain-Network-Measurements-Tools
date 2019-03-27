from .Bitcoin_Message import *


def treat_verack_packet(payload):
    return Verack_Message()


# VERACK Message acknowledge a previoulsy-received version message, informing the connecting node that it can begin to send other messages.
class Verack_Message(Bitcoin_Message):
    def __init__(self):
        super().__init__("verack")

    def getPayload(self):
        # VERACK Messages have no payload
        payload = bytearray()
        return payload
