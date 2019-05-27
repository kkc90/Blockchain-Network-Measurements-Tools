from ..Util import *
from .Bitcoin_Message import *


def treat_reject_packet(payload):
    type, payload_left = treat_variable_length_string(payload)

    ccode = payload_left[0]

    payload_left = payload_left[1::]

    reason, payload_left = treat_variable_length_string(payload_left)

    data = None

    return Reject_Message(type, ccode, reason, data), payload_left


# PONG Message replies to a ping message, proving to the pinging node that the ponging node is still allive.
class Reject_Message(Bitcoin_Message):
    def __init__(self, type, ccode, reason, data=None):
        super().__init__("reject")

        self.type = type
        self.ccode = ccode
        self.reason = reason
        self.data = data

    def getType(self):
        return self.type

    def getCode(self):
        return self.ccode

    def getReason(self):
        return self.reason

    def getData(self):
        return self.data

    def getPayload(self):
        payload = bytearray()

        payload += get_variable_length_string(self.type)

        payload += self.ccode.to_bytes(1, byteorder="little")

        payload += get_variable_length_string(self.reason)

        return payload

    def __eq__(self, other):
        return type(self) is type(other) and self.type == other.type and self.ccode == other.ccode \
               and self.reason == other.reason and self.data == other.data
