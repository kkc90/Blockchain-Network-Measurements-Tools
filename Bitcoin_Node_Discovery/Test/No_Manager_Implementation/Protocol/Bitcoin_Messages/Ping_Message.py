from .Bitcoin_Message import Bitcoin_Message


# PING Message is sent periodically to help confirm that the receiving peer is still connected.
class Ping_Message(Bitcoin_Message):
    def __init__(self, command, ping_nonce):
        super().__init__(command)
        self.ping_nonce = ping_nonce

    def getPingNonce(self):
        return self.ping_nonce

    def getPayload(self):
        payload = bytearray()

        rand_nonce = self.ping_nonce.to_bytes(8, byteorder='little')

        for i in rand_nonce:
            payload.append(i)

        return payload
