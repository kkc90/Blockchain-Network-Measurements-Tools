from ..Util import *
from .Bitcoin_Message import *


def treat_getaddr_packet(payload):
    return GetAddr_Message(), bytearray()


# GETADDR Message requests an ADDR Message from the receiving node containing IP Addresses of other receiving nodes.
class GetAddr_Message(Bitcoin_Message):
    def __init__(self, ):
        super().__init__("getaddr")

    def getPayload(self):
        # GETADDR Messages have no payload
        payload = bytearray()

        return payload
