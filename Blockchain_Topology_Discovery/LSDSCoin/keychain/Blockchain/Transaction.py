import hashlib

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import utils, padding


class Transaction:
    def __init__(self, key, value, origin, timestamp, signature=None):
        """A transaction, in our KV setting. A transaction typically involves
        some key, value and an origin (the one who put it onto the storage).
        """
        self._key = key
        self._value = value
        self._origin = origin
        self._timestamp = int(timestamp)
        self._signature = signature

    def getValue(self):
        return self._value

    def getOrigin(self):
        return self._origin

    def getKey(self):
        return self._key

    def getSignature(self):
        return self._signature

    def getTimestamp(self):
        return self._timestamp

    def sign(self, private_key):
        chosen_hash = hashes.SHA256()
        hasher = hashes.Hash(chosen_hash, default_backend())
        hasher.update(repr(self._value).encode("utf-8"))
        hasher.update(repr(self._origin.public_numbers().n).encode("utf-8"))
        hasher.update(repr(self._key).encode("utf-8"))
        hasher.update(repr(self._timestamp).encode("utf-8"))
        digest = hasher.finalize()

        self._signature = private_key.sign(
            digest,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            utils.Prehashed(chosen_hash)
        )

    def verify(self, public_key):
        chosen_hash = hashes.SHA256()
        hasher = hashes.Hash(chosen_hash, default_backend())
        hasher.update(repr(self._value).encode("utf-8"))
        hasher.update(repr(self._origin.public_numbers().n).encode("utf-8"))
        hasher.update(repr(self._key).encode("utf-8"))
        hasher.update(repr(self._timestamp).encode("utf-8"))
        digest = hasher.finalize()

        public_key.verify(
            self._signature,
            digest,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            utils.Prehashed(chosen_hash)
        )

    def byte_hash(self):
        hasher = hashlib.sha256()
        hasher.update(repr(self._key).encode("utf-8"))
        hasher.update(repr(self._value).encode("utf-8"))
        hasher.update(repr(self._origin.public_numbers().n).encode("utf-8"))
        hasher.update(repr(self._timestamp).encode("utf-8"))
        hasher.update(repr(self._signature).encode("utf-8"))

        return hasher.digest()

    def __hash__(self):
        hasher = hashlib.sha256()
        hasher.update(repr(self._key).encode("utf-8"))
        hasher.update(repr(self._value).encode("utf-8"))
        hasher.update(repr(self._origin.public_numbers().n).encode("utf-8"))
        hasher.update(repr(self._timestamp).encode("utf-8"))
        hasher.update(repr(self._signature).encode("utf-8"))

        return int(hasher.hexdigest(), 16)

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __str__(self):
        return self._key + " - " + self._value
