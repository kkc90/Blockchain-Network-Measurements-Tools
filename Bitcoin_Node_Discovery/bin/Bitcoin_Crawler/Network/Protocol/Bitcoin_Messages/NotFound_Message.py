from ..Util import *
from .Bitcoin_Message import *


class NotFound_Message(Bitcoin_Message):
    def __init__(self, inv_list):
        super().__init__("inv")
        self._inv_list = inv_list
        self._nb_entries = len(inv_list)

    def get_nb_entries(self):
        return self._nb_entries

    def get_inv_list(self):
        return self._inv_list

    def get_available_objects(self):
        blocks_hash_available = list()
        tx_hash_available = list()

        for inv_vectors in self._inv_list:
            object_type = inv_vectors[0]
            object_hash = inv_vectors[1]

            if object_type == Protocol_Constant.INV_VECTOR_MSG_TX:
                tx_hash_available.append(object_hash)

            elif object_type == Protocol_Constant.INV_VECTOR_MSG_BLOCK:
                blocks_hash_available.append(object_hash)

        return blocks_hash_available, tx_hash_available

    def getPayload(self):
        payload = bytearray()

        var_int = get_variable_length_integer(self._nb_entries)

        inv_list = get_inv_list(self._inv_list)

        payload = payload + var_int + inv_list

        return payload

    def __eq__(self, other):
        return type(self) is type(
            other) and self._nb_entries == other.get_nb_entries() and self._inv_list == other.get_inv_list()


def treat_notfound_packet(payload):
    nb_entries, entries = treat_variable_length_list(payload)

    inv_list, payload_left = treat_inv_list(nb_entries, entries)

    return NotFound_Message(inv_list), payload_left
