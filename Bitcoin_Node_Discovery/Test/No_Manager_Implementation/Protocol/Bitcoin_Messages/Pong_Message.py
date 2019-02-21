from .Bitcoin_Message import Bitcoin_Message


# PONG Message replies to a ping message, proving to the pinging node that the ponging node is still allive.
class Pong_Message(Bitcoin_Message):
    def __init__(self, command, pong_nonce):
        super().__init__(command)
        self.pong_nonce = pong_nonce

    def getPongNonce(self):
        return self.pong_nonce

    def getPayload(self):
        payload = bytearray()

        rand_nonce = self.pong_nonce.to_bytes(8, byteorder='little')

        for i in rand_nonce:
            payload.append(i)

        return payload
