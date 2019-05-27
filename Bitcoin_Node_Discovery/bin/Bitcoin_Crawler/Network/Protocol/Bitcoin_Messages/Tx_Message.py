from .Bitcoin_Message import *
from ..Util import *
from ....Util import *


class Tx_Message(Bitcoin_Message):
    def __init__(self, key, value, public_key, timestamp, signature=None):
        super().__init__("tx")
        self._key = key  # String or Number
        self._value = value
        self._public_key = public_key
        self._signature = signature
        self._timestamp = int(timestamp)

    def get_key(self):
        return self._key

    def get_value(self):
        return self._value

    def get_public_key(self):
        return self._public_key

    def get_timestamp(self):
        return self._timestamp

    def get_signature(self):
        return self._signature

    def getPayload(self):
        payload = bytearray()

        key_bytes = self._key.encode("utf-8")

        nb_key_bytes = get_variable_length_integer(len(key_bytes))

        value_bytes = self._value.encode("utf-8")

        nb_value_bytes = get_variable_length_integer(len(value_bytes))

        public_key_bytes = public_key_to_bytes(self._public_key)

        nb_public_key_bytes = get_variable_length_integer(len(public_key_bytes))

        if self._signature is not None:
            nb_signature_bytes = get_variable_length_integer(len(self._signature))

            signature_bytes = self._signature
        else:
            nb_signature_bytes = get_variable_length_integer(0)

            signature_bytes = bytearray()

        timestamp_bytes = get_variable_length_integer(self._timestamp)

        payload = payload + nb_key_bytes + key_bytes + nb_value_bytes + value_bytes + nb_public_key_bytes \
                  + public_key_bytes + nb_signature_bytes + signature_bytes + timestamp_bytes

        return payload

    def __eq__(self, other):
        return type(self) is type(other) and self._key == other.get_key() and self._value == other.get_value() \
               and self._public_key.public_numbers().n == other.get_public_key().public_numbers().n and self._timestamp == other.get_timestamp()


def treat_tx_packet(payload):
    nb_key_bytes, payload_left = treat_variable_length_integer(payload)

    key = payload_left[0:nb_key_bytes].decode("utf-8")

    payload_left = payload_left[nb_key_bytes::]

    nb_value_bytes, payload_left = treat_variable_length_integer(payload_left)

    value = payload_left[0:nb_value_bytes].decode("utf-8")

    payload_left = payload_left[nb_value_bytes::]

    nb_public_key_bytes, payload_left = treat_variable_length_integer(payload_left)

    public_key = bytes_to_public_key(bytes(payload_left[0:nb_public_key_bytes]))

    payload_left = payload_left[nb_public_key_bytes::]

    nb_signature_bytes, payload_left = treat_variable_length_integer(payload_left)

    signature = payload_left[0:nb_signature_bytes]

    payload_left = payload_left[nb_signature_bytes::]

    timestamp, payload_left = treat_variable_length_integer(payload_left)

    return Tx_Message(key, value, public_key, timestamp, signature=signature), payload_left
