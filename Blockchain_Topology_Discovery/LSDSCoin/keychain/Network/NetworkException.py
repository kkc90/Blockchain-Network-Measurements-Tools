class NetworkException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UnitializedBlockchainException(NetworkException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ConnectionException(NetworkException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class SocketTimeoutException(ConnectionException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class BrokenSocketException(ConnectionException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class HandShakeFailureException(ConnectionException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class BrokenConnectionException(NetworkException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ConnectionTimeoutException(NetworkException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class SendMessageException(NetworkException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class SendMessageTimeoutException(SendMessageException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ReceiveMessageException(NetworkException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ReceiveMessageTimeoutException(ReceiveMessageException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
