from .Bitcoin_Message import Bitcoin_Message


# VERACK Message acknowledge a previoulsy-received version message, informing the connecting node that it can begin to send other messages.
class Verack_Message(Bitcoin_Message):
    def __init__(self, command):
        super().__init__(command)

    def getPayload(self):
        # VERACK Messages have no payload
        payload = bytearray()
        return payload
