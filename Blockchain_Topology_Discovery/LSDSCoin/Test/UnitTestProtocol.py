import hashlib
import unittest

from context import *


def get_hash(string_to_hash):
    return int(hashlib.sha256(hashlib.sha256(string_to_hash.encode("utf-8")).digest()).hexdigest(), 16)


class UnitTestProtocol(unittest.TestCase):

    def test_version_packet_reception(self):
        version = 1
        sender_ip = "192.168.1.2"
        sender_port = 5000
        sender_service = Protocol_Constant.NODE_NONE
        receiver_ip_address = "192.168.2.3"
        receiver_port = 5000
        receiver_service = Protocol_Constant.NODE_NONE
        version_nonce = 3
        msg1 = Version_Message.Version_Message(version, sender_ip, sender_port, sender_service, receiver_ip_address,
                                               receiver_port, receiver_service, version_nonce)

        a = get_packet(msg1, "mainnet")

        command_bytes = bytearray(a[4:16])

        length_bytes = bytearray(a[16:20])
        payload_length = int.from_bytes(length_bytes, byteorder='little')

        checksum_bytes = bytearray(a[20:24])

        payload_bytes = bytearray(a[24:24 + payload_length])

        msg2 = treat_packet(command_bytes, length_bytes, checksum_bytes, payload_bytes)

        self.assertTrue(msg1 == msg2)

    def test_verack_packet_reception(self):
        msg1 = Verack_Message.Verack_Message()

        a = get_packet(msg1, "mainnet")

        command_bytes = bytearray(a[4:16])

        length_bytes = bytearray(a[16:20])
        payload_length = int.from_bytes(length_bytes, byteorder='little')

        checksum_bytes = bytearray(a[20:24])

        payload_bytes = bytearray(a[24:24 + payload_length])

        msg2 = treat_packet(command_bytes, length_bytes, checksum_bytes, payload_bytes)

    def test_getaddr_packet_reception(self):
        msg1 = GetAddr_Message.GetAddr_Message()

        a = get_packet(msg1, "mainnet")

        command_bytes = bytearray(a[4:16])

        length_bytes = bytearray(a[16:20])
        payload_length = int.from_bytes(length_bytes, byteorder='little')

        checksum_bytes = bytearray(a[20:24])

        payload_bytes = bytearray(a[24:24 + payload_length])

        msg2 = treat_packet(command_bytes, length_bytes, checksum_bytes, payload_bytes)

    def test_mempool_packet_reception(self):
        msg1 = MemPool_Message.MemPool_Message()

        a = get_packet(msg1, "mainnet")

        command_bytes = bytearray(a[4:16])

        length_bytes = bytearray(a[16:20])
        payload_length = int.from_bytes(length_bytes, byteorder='little')

        checksum_bytes = bytearray(a[20:24])

        payload_bytes = bytearray(a[24:24 + payload_length])

        msg2 = treat_packet(command_bytes, length_bytes, checksum_bytes, payload_bytes)

    def test_ping_packet_reception(self):
        msg1 = Ping_Message.Ping_Message(1)

        a = get_packet(msg1, "mainnet")

        command_bytes = bytearray(a[4:16])

        length_bytes = bytearray(a[16:20])
        payload_length = int.from_bytes(length_bytes, byteorder='little')

        checksum_bytes = bytearray(a[20:24])

        payload_bytes = bytearray(a[24:24 + payload_length])

        msg2 = treat_packet(command_bytes, length_bytes, checksum_bytes, payload_bytes)

        self.assertTrue(msg1 == msg2)

    def test_pong_packet_reception(self):
        msg1 = Pong_Message.Pong_Message(1)

        a = get_packet(msg1, "mainnet")

        command_bytes = bytearray(a[4:16])

        length_bytes = bytearray(a[16:20])
        payload_length = int.from_bytes(length_bytes, byteorder='little')

        checksum_bytes = bytearray(a[20:24])

        payload_bytes = bytearray(a[24:24 + payload_length])

        msg2 = treat_packet(command_bytes, length_bytes, checksum_bytes, payload_bytes)

        self.assertTrue(msg1 == msg2)

    def test_addr_packet_reception(self):
        ip_table = {"127.0.0.1": (8333, 1, 1553613988.4576137)}

        msg1 = Addr_Message.Addr_Message(ip_table)

        a = get_packet(msg1, "mainnet")

        command_bytes = bytearray(a[4:16])

        length_bytes = bytearray(a[16:20])
        payload_length = int.from_bytes(length_bytes, byteorder='little')

        checksum_bytes = bytearray(a[20:24])

        payload_bytes = bytearray(a[24:24 + payload_length])

        msg2 = treat_packet(command_bytes, length_bytes, checksum_bytes, payload_bytes)

        self.assertTrue(msg1 == msg2)

    def test_inv_packet_reception(self):
        inv_list = list()
        inv_list.append((1, get_hash("lol")))

        msg1 = Inv_Message.Inv_Message(inv_list)

        a = get_packet(msg1, "mainnet")

        command_bytes = bytearray(a[4:16])

        length_bytes = bytearray(a[16:20])
        payload_length = int.from_bytes(length_bytes, byteorder='little')

        checksum_bytes = bytearray(a[20:24])

        payload_bytes = bytearray(a[24:24 + payload_length])

        msg2 = treat_packet(command_bytes, length_bytes, checksum_bytes, payload_bytes)

        self.assertTrue(msg1 == msg2)

    def test_getdata_packet_reception(self):
        data_list = list()
        data_list.append((1, get_hash("lol")))

        msg1 = GetData_Message.GetData_Message(data_list)

        a = get_packet(msg1, "mainnet")

        command_bytes = bytearray(a[4:16])

        length_bytes = bytearray(a[16:20])
        payload_length = int.from_bytes(length_bytes, byteorder='little')

        checksum_bytes = bytearray(a[20:24])

        payload_bytes = bytearray(a[24:24 + payload_length])

        msg2 = treat_packet(command_bytes, length_bytes, checksum_bytes, payload_bytes)

        self.assertTrue(msg1 == msg2)

    def test_notfound_packet_reception(self):
        data_list = list()
        data_list.append((1, get_hash("lol")))

        msg1 = NotFound_Message.NotFound_Message(data_list)

        a = get_packet(msg1, "mainnet")

        command_bytes = bytearray(a[4:16])

        length_bytes = bytearray(a[16:20])
        payload_length = int.from_bytes(length_bytes, byteorder='little')

        checksum_bytes = bytearray(a[20:24])

        payload_bytes = bytearray(a[24:24 + payload_length])

        msg2 = treat_packet(command_bytes, length_bytes, checksum_bytes, payload_bytes)

        self.assertTrue(msg1 == msg2)

    def test_getblock_packet_reception(self):
        version = 1
        block_locator_list = list()
        a = get_hash("hello")
        block_locator_list.append(a)
        block_locator_list.append(a)

        hash_stop = get_hash("hello2")

        msg1 = GetBlock_Message.GetBlock_Message(version, block_locator_list, hash_stop)

        a = get_packet(msg1, "mainnet")

        command_bytes = bytearray(a[4:16])

        length_bytes = bytearray(a[16:20])
        payload_length = int.from_bytes(length_bytes, byteorder='little')

        checksum_bytes = bytearray(a[20:24])

        payload_bytes = bytearray(a[24:24 + payload_length])

        msg2 = treat_packet(command_bytes, length_bytes, checksum_bytes, payload_bytes)

        self.assertTrue(msg1 == msg2)

    def test_getheader_packet_reception(self):
        version = 1
        block_locator_list = list()

        a = get_hash("hello")
        block_locator_list.append(a)

        hash_stop = get_hash("hello2")

        msg1 = GetHeader_Message.GetHeader_Message(version, block_locator_list, hash_stop)

        a = get_packet(msg1, "mainnet")

        command_bytes = bytearray(a[4:16])

        length_bytes = bytearray(a[16:20])
        payload_length = int.from_bytes(length_bytes, byteorder='little')

        checksum_bytes = bytearray(a[20:24])

        payload_bytes = bytearray(a[24:24 + payload_length])

        msg2 = treat_packet(command_bytes, length_bytes, checksum_bytes, payload_bytes)

        self.assertTrue(msg1 == msg2)

    # def test_bitcoin_tx_packet_reception(self):
    #     version = 1
    #     tx_in_list = list()
    #
    #     for i in range(1, 5):
    #         tx_in = dict()
    #
    #         outpoint = dict()
    #         outpoint["hash"] = get_hash(("hello" + str(i)).encode("utf-8"))
    #         outpoint["index"] = i
    #
    #         tx_in["previous_output"] = outpoint
    #
    #         tx_in["signature_script"] = get_hash(("lol" + str(i)).encode("utf-8"))
    #
    #         tx_in["sequence"] = i
    #
    #         tx_in_list.append(tx_in)
    #
    #     tx_out_list = list()
    #
    #     for i in range(1, 5):
    #         tx_out = dict()
    #
    #         tx_out["value"] = i * 5
    #
    #         tx_out["pk_script"] = get_hash(("goodbye" + str(i)).encode("utf-8"))
    #
    #         tx_out_list.append(tx_out)
    #
    #     tx_witness_list = list()
    #
    #     for i in range(1, 5):
    #         tx_witness = dict()
    #
    #         tx_witness["raw_witness_data"] = get_hash(("witness" + str(i)).encode("utf-8")).encode("utf-8")
    #
    #         tx_witness_list.append(tx_witness)
    #
    #     lock_time = 0
    #
    #     msg1 = Tx_Message.Tx_Message(version, tx_in_list, tx_out_list, tx_witness_list, lock_time)
    #
    #     a = get_packet(msg1, "mainnet")
    #
    #     command_bytes = bytearray(a[4:16])
    #
    #     length_bytes = bytearray(a[16:20])
    #     payload_length = int.from_bytes(length_bytes, byteorder='little')
    #
    #     checksum_bytes = bytearray(a[20:24])
    #
    #     payload_bytes = bytearray(a[24:24 + payload_length])
    #
    #     msg2 = treat_packet(command_bytes, length_bytes, checksum_bytes, payload_bytes)
    #
    #     self.assertTrue(msg1 == msg2)

    def test_tx_packet_reception(self):
        key = "lol"
        value = "lol1"
        public_key = generate_key().public_key()
        timestamp = time.time()

        msg1 = Tx_Message.Tx_Message(key, value, public_key, timestamp)

        a = get_packet(msg1, "mainnet")

        command_bytes = bytearray(a[4:16])

        length_bytes = bytearray(a[16:20])
        payload_length = int.from_bytes(length_bytes, byteorder='little')

        checksum_bytes = bytearray(a[20:24])

        payload_bytes = bytearray(a[24:24 + payload_length])

        msg2 = treat_packet(command_bytes, length_bytes, checksum_bytes, payload_bytes)

        self.assertTrue(msg1 == msg2)

    def test_block_packet_reception(self):
        version = 1

        prev_block = get_hash("prev_block_hash")

        merkle_root = get_hash("merkle_root")

        timestamp = time.time()

        bits = 100

        nonce = 5

        txn_list = list()

        public_key = generate_key().public_key()

        for j in range(1, 3):
            key = "lol" + str(j)
            value = "lol" + str(j + 1)
            timestamp = time.time()

            tx = Tx_Message.Tx_Message(key, value, public_key, timestamp)

            txn_list.append(tx)

        msg1 = Block_Message.Block_Message(version, prev_block, merkle_root, timestamp, bits, nonce, txn_list)

        a = get_packet(msg1, "mainnet")

        command_bytes = bytearray(a[4:16])

        length_bytes = bytearray(a[16:20])
        payload_length = int.from_bytes(length_bytes, byteorder='little')

        checksum_bytes = bytearray(a[20:24])

        payload_bytes = bytearray(a[24:24 + payload_length])

        msg2 = treat_packet(command_bytes, length_bytes, checksum_bytes, payload_bytes)

        self.assertTrue(msg1 == msg2)


if __name__ == '__main__':
    unittest.main()
