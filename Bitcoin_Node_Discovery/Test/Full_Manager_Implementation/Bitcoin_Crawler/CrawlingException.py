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