from ..Util import *
from .Bitcoin_Message import *
from .Tx_Message import *


class Block_Message(Bitcoin_Message):
    def __init__(self, version, prev_block, merkle_root, timestamp, bits, nonce, txn_list):
        super().__init__("block")
        self._version = version
        self._prev_block = prev_block
        self._merkle_root = merkle_root
        self._timestamp = int(timestamp)
        self._bits = int(bits)
        self._nonce = nonce
        self._txn_list = txn_list

    def get_version(self):
        return self._version

    def get_prev_block(self):
        return self._prev_block

    def get_merkle_root(self):
        return self._merkle_root

    def get_timestamp(self):
        return self._timestamp

    def get_bits(self):
        return self._bits

    def get_nonce(self):
        return self._nonce

    def get_txn_list(self):
        return self._txn_list

    def getPayload(self):
        payload = bytearray()

        version_bytes = self._version.to_bytes(4, byteorder="little")

        prev_block_bytes = self._prev_block.to_bytes(32, byteorder="little")

        merkle_root_bytes = self._merkle_root.to_bytes(32, byteorder="little")

        timestamp_bytes = self._timestamp.to_bytes(4, byteorder="little")

        bits_bytes = self._bits.to_bytes(4, byteorder="little")

        nonce_bytes = self._nonce.to_bytes(4, byteorder="little")

        txn_count_bytes = get_variable_length_integer(len(self._txn_list))

        txn_list_bytes = bytearray()

        for tx in self._txn_list:
            txn_list_bytes = txn_list_bytes + tx.getPayload()

        payload = payload + version_bytes + prev_block_bytes + merkle_root_bytes + timestamp_bytes + bits_bytes \
                  + nonce_bytes + txn_count_bytes + txn_list_bytes

        return payload

    def __eq__(self, other):
        return type(self) is type(
            other) and self._version == other.get_version() and self._prev_block == other.get_prev_block() \
               and self._merkle_root == other.get_merkle_root() and self._timestamp == other.get_timestamp() \
               and self._bits == other.get_bits() and self._nonce == other.get_nonce() \
               and self._txn_list == other.get_txn_list()


def treat_block_packet(payload):
    version = int.from_bytes(payload[0:4], byteorder="little")

    prev_block = int.from_bytes(payload[4:36], byteorder="little")

    merkle_root = int.from_bytes(payload[36:68], byteorder="little")

    timestamp = int.from_bytes(payload[68:72], byteorder="little")

    bits = int.from_bytes(payload[72:76], byteorder="little")

    nonce = int.from_bytes(payload[76:80], byteorder="little")

    txn_count, txns_bytes = treat_variable_length_integer(payload[80::])

    txn_list = list()

    i = 0
    while i < txn_count:
        tx, txns_bytes = treat_tx_packet(txns_bytes)

        txn_list.append(tx)

        i = i + 1

    return Block_Message(version, prev_block, merkle_root, timestamp, bits, nonce, txn_list), txns_bytes
