import datetime

class Transaction_Pool:
    def __init__(self, ):

        self._transaction_pool = set()
        self._transaction_hashes = set()

    def contains(self, transaction):
        if transaction in self._transaction_pool:
            return True
        else:
            return False

    def containsHash(self, transaction_hash):
        if transaction_hash in self._transaction_hashes:
            return True
        else:
            return False

    def isEmpty(self):
        return not len(self._transaction_pool) > 0

    def getTransactionPool(self):
        return self._transaction_pool

    def getTransactionPoolHashes(self):
        return self._transaction_hashes

    def getNbTransactions(self):
        return len(self._transaction_pool)

    def removeTransaction(self, transaction):
        if transaction in self._transaction_pool:
            self._transaction_pool.remove(transaction)
            self._transaction_hashes.remove(transaction.__hash__())

    def getTransactionFromHash(self, transaction_hash):
        if transaction_hash in self._transaction_hashes:
            transaction_list = set(self._transaction_pool)
            for transaction in transaction_list:
                if transaction_hash == transaction.__hash__():
                    return transaction

        return None

    def getTransactions(self, nb):

        transaction_list = list()
        i = 0

        while len(transaction_list) < nb and len(self._transaction_pool) > 0:
            t = self._transaction_pool.pop()
            transaction_list.append(t)
            i = i + 1

        for trans in transaction_list:
            self._transaction_pool.add(trans)

        return transaction_list

    def verify_transaction(self, transaction):
        public_key = transaction.getOrigin()
        transaction.verify(public_key)

    def add_transaction(self, transaction):
        """Adds a transaction to your current list of transactions,

        If the `mine` method is called, it will collect the current list
        of transactions, and attempt to mine a block with those.
        """

        public_key = transaction.getOrigin()
        transaction.verify(public_key)
        self._transaction_pool.add(transaction)
        self._transaction_hashes.add(transaction.__hash__())

    def __eq__(self, other):
        trans_pool = other.getTransactionPool()

        if len(trans_pool) != len(self._transaction_pool):
            return False

        for transaction in self._transaction_pool:
            if transaction in trans_pool:
                continue
            else:
                return False

        return True

    def __str__(self):
        string = ""

        for transaction in self._transaction_pool:
            string += "\t" + str(transaction) + "\n"

        return string + "\n"
