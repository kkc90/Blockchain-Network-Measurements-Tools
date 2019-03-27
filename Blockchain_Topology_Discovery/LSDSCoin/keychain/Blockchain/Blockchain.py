class Blockchain:

    def __init__(self):
        """The bootstrap address serves as the initial entry point of
        the bootstrapping procedure. In principle it will contact the specified
        address, download the peerlist, and start the bootstrapping procedure.
        """
        # Initialize the properties.
        self._blocks = list()

    def getBlock(self, index):
        return self._blocks[index]

    def setBlock(self, index, block):
        self._blocks[index] = block

    def getLasBlock(self):
        return self._blocks[-1]

    def getPrevLastBlock(self):
        return self._blocks[-2]

    def getBlocks(self):
        return self._blocks

    def addBlock(self, block):
        self._blocks.append(block)

    def get_last_hash(self):
        return self._blocks[-1].getBlockHash()

    def length(self):
        return len(self._blocks)

    def has_duplicate(self):
        transaction_list = set()

        for block in self._blocks:
            transactions = block.getTransactions()

            for t in transactions:
                if t in transaction_list:
                    return False

            transaction_list = transaction_list | transactions

        return True

    def is_valid(self):
        """Checks if the current state of the blockchain is valid.

        Meaning, are the sequence of hashes, and the proofs of the
        blocks correct?
        """
        previous_hash = self._blocks[0].computeHash()

        for block in self._blocks[1:]:
            hash = block.computeHash()

            if block.getPrevBlockHash() != previous_hash or block.getBlockHash() != hash:
                return False

            previous_hash = hash

        return True
