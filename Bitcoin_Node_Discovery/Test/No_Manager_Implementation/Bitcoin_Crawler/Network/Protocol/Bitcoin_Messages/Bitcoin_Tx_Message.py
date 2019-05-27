from .Bitcoin_Message import *
from ..Util import *


class Bitcoin_Tx_Message(Bitcoin_Message):
    def __init__(self, version, tx_in_list, tx_out_list, tx_witness_list, lock_time):
        super().__init__("tx")
        self._version = version
        self._tx_in_list = tx_in_list
        self._tx_out_list = tx_out_list
        self._tx_witness_list = tx_witness_list
        self._lock_time = lock_time

    def get_version(self):
        return self._version

    def get_tx_in_list(self):
        return self._tx_in_list

    def get_tx_out_list(self):
        return self._tx_out_list

    def get_tx_witness_list(self):
        return self._tx_witness_list

    def get_lock_time(self):
        return self._lock_time

    def getPayload(self):
        version_bytes = self._version.to_bytes(4, byteorder="little")

        flag_bytes = bytearray()

        if self._tx_witness_list is not None:
            flag_bytes = (1).to_bytes(2, byteorder="little")

        tx_in_bytes = bitcoin_tx_in_list_to_bytes(self._tx_in_list)
        tx_in_count_bytes = get_variable_length_integer(len(self._tx_in_list))

        tx_out_bytes = bitcoin_tx_out_list_to_bytes(self._tx_out_list)
        tx_out_count_bytes = get_variable_length_integer(len(self._tx_out_list))

        tx_witness_bytes = bitcoin_tx_witness_list_to_bytes(self._tx_witness_list)
        tx_witness_count_bytes = get_variable_length_integer(len(self._tx_witness_list))

        lock_time_bytes = self._lock_time.to_bytes(4, byteorder="little")

        payload = version_bytes + flag_bytes + tx_in_count_bytes + tx_in_bytes + tx_out_count_bytes + tx_out_bytes \
                  + tx_witness_count_bytes + tx_witness_bytes + lock_time_bytes

        return payload

    def __eq__(self, other):
        return self._version == other.get_version() and self._tx_in_list == other.get_tx_in_list() \
               and self._tx_out_list == other.get_tx_out_list() and self._tx_witness_list == other.get_tx_witness_list() \
               and self._lock_time == other.get_lock_time()


def treat_tx_packet(payload):
    version = int.from_bytes(payload[0:4], byteorder="little")

    lock_time = int.from_bytes(payload[-4::], byteorder="little")

    payload_left = payload[4:-4]

    flag = False
    if payload_left[0:2] == (1).to_bytes(2, byteorder="little"):
        flag = True
        payload_left = payload_left[2::]

    nb_entries_tx_in, payload_left = treat_variable_length_list(payload_left)

    tx_in_list, payload_left = treat_bitcoin_tx_in_list_bytes(nb_entries_tx_in, payload_left)

    nb_entries_tx_out, payload_left = treat_variable_length_list(payload_left)

    tx_out_list, payload_left = treat_bitcoin_tx_out_list_bytes(nb_entries_tx_out, payload_left)

    tx_witness_list = None
    if flag is True and nb_entries_tx_in > 0:
        nb_entries_tx_witness, payload_left = treat_variable_length_list(payload_left)

        tx_witness_list, payload_left = treat_tx_witness_list_bytes(nb_entries_tx_witness, payload_left)

    return Bitcoin_Tx_Message(version, tx_in_list, tx_out_list, tx_witness_list, lock_time), payload_left
