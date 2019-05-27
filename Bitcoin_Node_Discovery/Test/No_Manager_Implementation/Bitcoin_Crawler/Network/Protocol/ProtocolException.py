class ProtocolException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UnexpectedPacketException(ProtocolException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UnknownOriginNetworkException(ProtocolException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UnsupportedBitcoinCommandException(ProtocolException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UnknownServiceType(ProtocolException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UnknownIPAddressTypeException(ProtocolException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UnvalidVersionNonceException(ProtocolException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class MissingTimestampExeception(ProtocolException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class DiscardedPacketException(ProtocolException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UnprocessedIPException(ProtocolException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class NotSupportedMessageException(ProtocolException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
