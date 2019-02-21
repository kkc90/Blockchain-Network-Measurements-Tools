"""
    All exceptions dealing with the crawler
"""


class CrawlingException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class NoMoreIPToProcessException(CrawlingException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UnprocessedIPException(CrawlingException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UnknownIPAddressTypeException(CrawlingException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class LockTimeoutException(CrawlingException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class SemaphoreTimeoutException(CrawlingException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


"""
    All exceptions dealing with querying peers from a connected peer
"""


class PeerQueryException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UnsupportedBitcoinCommandException(PeerQueryException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class AskAliveException(PeerQueryException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


"""
    All exceptions dealing with trying to connect to a peer (TCP + Bitcoin Handshake)
"""


class ConnectionException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ConnectionTimeoutException(ConnectionException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class DisconnectedSocketException(ConnectionException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class HandShakeFailureException(ConnectionException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


"""
    All exceptions dealing with receiving/sending Messages to a connected peer (TCP connection established)
"""


class MessageFailureException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class SendMessageFailureException(MessageFailureException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class SendMessageTimeoutException(MessageFailureException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class ReceiveMessageTimeoutException(MessageFailureException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class PacketTreatmentException(MessageFailureException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UnknownSendMessageFailureException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UnknownReceiveMessageFailureException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
