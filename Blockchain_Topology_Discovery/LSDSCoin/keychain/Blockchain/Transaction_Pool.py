class Transaction_Pool:
    def __init__(self, transaction_pool=None):

        if transaction_pool is None:
            self._transaction_pool = set()
        else:
            self._transaction_pool = transaction_pool

    def isEmpty(self):
        return not len(self._transaction_pool) > 0

    def getTransactionPool(self):
        return self._transaction_pool

    def getNbTransactions(self):
        return len(self._transaction_pool)

    def removeTransaction(self, transaction):
        if transaction in self._transaction_pool:
            self._transaction_pool.remove(transaction)

    def valid_transaction_pool(self):
        for block in self._blocks:
            transactions = block.getTransactions()

            for t in transactions:
                if t in self._transaction_pool:
                    return False

        return True

    def get_transactions(self, nb):

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
        and broadcasts it to your Blockchain network.

        If the `mine` method is called, it will collect the current list
        of transactions, and attempt to mine a block with those.
        """

        public_key = transaction.getOrigin()
        transaction.verify(public_key)
        self._transaction_pool.add(transaction)
