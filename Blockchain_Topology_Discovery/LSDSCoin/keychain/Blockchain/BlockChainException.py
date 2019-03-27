class BlockChainException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ZeroTransactionBlockException(BlockChainException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UnminedBlockException(BlockChainException):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
