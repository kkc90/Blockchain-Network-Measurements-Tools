import datetime

class Blockchain:

    def __init__(self):
        """The bootstrap address serves as the initial entry point of
        the bootstrapping procedure. In principle it will contact the specified
        address, download the peerlist, and start the bootstrapping procedure.
        """
        # Initialize the properties.
        self._blocks = list()
        self._blocks_hashes = set()

    def getBlock(self, index):
        return self._blocks[index]

    def setBlock(self, index, block):
        self._blocks[index] = block

    def getLastBlock(self):
        return self._blocks[-1]

    def getPrevLastBlock(self):
        return self._blocks[-2]

    def getBlocks(self):
        return self._blocks

    def addBlock(self, block):
        self._blocks.append(block)
        self._blocks_hashes.add(block.getBlockHash())

    def get_last_hash(self):
        return self._blocks[-1].getBlockHash()

    def length(self):
        return len(self._blocks)

    def hasDuplicateTransactions(self):
        transaction_list = set()

        for block in self._blocks:
            transactions = set(block.getTransactions())

            for t in transactions:
                if t in transaction_list:
                    return True

            transaction_list = transaction_list | transactions

        return False

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

    def containsBlock(self, block_hash):
        if block_hash in self._blocks_hashes:
            return True
        else:
            return False

    def containsTransaction(self, transaction):
        for block in self._blocks:
            if block.contains(transaction):
                return True
            else:
                return False

    def containsTransactionHash(self, transaction_Hash):
        for block in self._blocks:
            if block.containsHash(transaction_Hash):
                return True
            else:
                return False

    def getBlockFromHash(self, block_hash):
        for block in self._blocks:
            if block.getBlockHash() == block_hash:
                return block
        return None

    def __eq__(self, other):
        our_blocks = self._blocks
        other_blocks = other.getBlocks()

        i = 0
        while i < len(our_blocks):
            if our_blocks[i] != other_blocks[i]:
                return False

            i = i + 1

        return True

    def __str__(self):
        string = ""
        for block in self._blocks:
            string += "\t" + str(block) + "\n"

        return string
