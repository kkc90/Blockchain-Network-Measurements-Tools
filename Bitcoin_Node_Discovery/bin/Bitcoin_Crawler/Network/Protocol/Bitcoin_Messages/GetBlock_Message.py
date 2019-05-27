from ..Util import *
from .Bitcoin_Message import *


class GetBlock_Message(Bitcoin_Message):
    def __init__(self, version, block_locator_list, hash_stop=None):
        super().__init__("getblock")
        self._version = version
        self._block_locator_list = block_locator_list
        self._nb_block_locator = len(block_locator_list)
        self._hash_stop = hash_stop

    def get_version(self):
        return self._version

    def get_block_locator_list(self):
        return self._block_locator_list

    def get_nb_block_locator(self):
        return self._nb_block_locator

    def get_hash_stop(self):
        return self._hash_stop

    def getPayload(self):
        payload = bytearray()

        version_bytes = self._version.to_bytes(4, byteorder="little")

        var_int_bytes = get_variable_length_integer(self._nb_block_locator)

        block_locator_bytes = block_locator_list_to_bytes(self._block_locator_list)

        if self._hash_stop is not None:
            hash_stop_bytes = self._hash_stop.to_bytes(32, byteorder="little")
        else:
            hash_stop_bytes = bytearray()

        payload = payload + version_bytes + var_int_bytes + block_locator_bytes + hash_stop_bytes

        return payload

    def __eq__(self, other):
        return type(self) is type(
            other) and self._version == other.get_version() and self._nb_block_locator == other.get_nb_block_locator() \
               and self._block_locator_list == other.get_block_locator_list() and self._hash_stop == other.get_hash_stop()


def block_locator_list_to_bytes(block_locator_list):
    block_locator_list_bytes = bytearray()

    for block_locator in block_locator_list:
        block_locator_bytes = block_locator.to_bytes(32, byteorder="little")
        block_locator_list_bytes = block_locator_list_bytes + block_locator_bytes

    return block_locator_list_bytes


def treat_getblock_packet(payload):
    version = int.from_bytes(payload[0:4], byteorder="little")
    block_locator_list, payload_left = treat_block_locator_bytes(payload[4::])

    if len(payload_left) >= 32:
        hash_stop = int.from_bytes(payload_left[0:32], byteorder="little")
    else:
        hash_stop = None

    return GetBlock_Message(version, block_locator_list, hash_stop), bytearray()
