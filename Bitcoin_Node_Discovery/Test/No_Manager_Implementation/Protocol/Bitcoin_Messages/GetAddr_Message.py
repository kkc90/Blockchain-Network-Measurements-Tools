from .Bitcoin_Message import Bitcoin_Message


# GETADDR Message requests an ADDR Message from the receiving node containing IP Addresses of other receiving nodes.
class GetAddr_Message(Bitcoin_Message):
    def __init__(self, command):
        super().__init__(command)

    def getPayload(self):
        # GETADDR Messages have no payload
        payload = bytearray()

        return payload
