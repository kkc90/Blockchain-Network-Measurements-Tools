import unittest


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
        msg1 = Version_Message(version, sender_ip, sender_port, sender_service, receiver_ip_address, receiver_port,
                              receiver_service, version_nonce)

        a = get_packet(Bitcoin_Message, "mainnet")

        magic_nb_bytes = bytearray(a[0:4])

        command_bytes = bytearray(a[4:16])

        length_bytes = bytearray(a[16:20])
        payload_length = int.from_bytes(length_bytes, byteorder='little')

        checksum_bytes = bytearray(a[20:24])

        payload_bytes = bytearray(a[24:24+payload_length])

        msg2 = treat_packet(magic_nb_bytes, command_bytes, length_bytes, checksum_bytes, payload_bytes)

        self.assertTrue(msg1 == msg2)

    def test_verack_packet_reception(self):
        pass

    def test_getaddr_packet_reception(self):
        pass

    def test_ping_packet_reception(self):
        pass

    def test_pong_packet_reception(self):
        pass

    def test_addr_packet_reception(self):
        pass

    def test_version_packet_sending(self):
        pass

    def test_verack_packet_sending(self):
        pass

    def test_getaddr_packet_sending(self):
        pass

    def test_ping_packet_sending(self):
        pass

    def test_pong_packet_sending(self):
        pass

    def test_addr_packet_sending(self):
        pass


if __name__ == '__main__':
    unittest.main()
