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

    def getPayload(self):
        payload = bytearray()

        var_int = get_variable_length_integer(self._nb_entries)

        inv_list = get_inv_list(self._inv_list)

        payload = payload + var_int + inv_list

        return payload

    def __eq__(self, other):
        return self._nb_entries == other.get_nb_entries() and self._inv_list == other.get_inv_list()


def treat_notfound_packet(payload):
    nb_entries, entries = treat_variable_length_list(payload)

    inv_list = treat_inv_list(nb_entries, entries)

    return NotFound_Message(inv_list)
