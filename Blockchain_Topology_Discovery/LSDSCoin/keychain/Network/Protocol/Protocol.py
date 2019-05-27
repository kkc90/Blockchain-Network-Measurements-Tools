from .Util import *
from .Bitcoin_Messages import *
from .ProtocolException import *

COMMAND = {"version": Version_Message.treat_version_packet, "verack": Verack_Message.treat_verack_packet,
           "getaddr": GetAddr_Message.treat_getaddr_packet, "addr": Addr_Message.treat_addr_packet,
           "ping": Ping_Message.treat_ping_packet, "pong": Pong_Message.treat_pong_packet,
           "inv": Inv_Message.treat_inv_packet, "getdata": GetData_Message.treat_getdata_packet,
           "getheader" : GetHeader_Message.treat_getheader_packet,"getblock": GetBlock_Message.treat_getblock_packet,
           "tx": Tx_Message.treat_tx_packet, "block": Block_Message.treat_block_packet,
           "mempool": MemPool_Message.treat_mempool_packet}

"""
                TREAT A PACKET THAT HAS BEEN RECEIVED
"""


def treat_packet(command_bytes, length, checksum, payload):
    global COMMAND

    payload_sha = get_first_4_bytes_payload_checksum(payload)
    payload_length = int.from_bytes(length, byteorder="little")

    if len(payload) != payload_length:
        raise DiscardedPacketException((
            "DiscardedPacket Exception : The length of the payload is not the one mentionned.\n " + "Payload Length = ",
            len(payload), " | Packet's Payload length = ", payload_length))

    if payload_sha != checksum:
        raise DiscardedPacketException((
            "DiscardedPacket Exception : The payload of the packet has been modified (wrong checksum).\n" +
            "Calculated Checksum = ", payload_sha, " | Packet's Checksum = ", checksum))

    command = get_command(command_bytes)

    if command in COMMAND:
        result, payload_left = COMMAND[command](payload)
    else:
        raise UnsupportedBitcoinCommandException(
            ("UnsupportedBitcoinCommand Exception : Command " + command + " is not supported."))

    return result


"""
                RETURN THE BYTES THAT SHOULD BE SENT
"""


# Return a bitcoin packet ready to be sent to a peer
def get_packet(Bitcoin_Message, origin_network):
    command = get_command_field(Bitcoin_Message.getCommand())
    payload = Bitcoin_Message.getPayload()

    bitcoin_msg = bytearray()

    # Origin Network ID (4 bytes)
    if origin_network == "mainnet":
        # Magic Value indicating message origin network : Mainnet
        bitcoin_msg.append(249)
        bitcoin_msg.append(190)
        bitcoin_msg.append(180)
        bitcoin_msg.append(217)
    elif origin_network == "testnet":
        # Magic Value indicating message origin network : testnet
        bitcoin_msg.append(250)
        bitcoin_msg.append(191)
        bitcoin_msg.append(181)
        bitcoin_msg.append(218)
    elif origin_network == "testnet3":
        # Magic Value indicating message origin network : testnet3
        bitcoin_msg.append(11)
        bitcoin_msg.append(17)
        bitcoin_msg.append(9)
        bitcoin_msg.append(7)
    else:
        raise UnknownOriginNetworkException("Unvalid bitcoin network - Valid networks are mainnet/testnet/testnet3")
    # Command ID (12 bytes)
    counter = 0
    for i in command:
        bitcoin_msg.append(i)
        if counter > 12:
            raise ProtocolException("Error Bitcoin Protocol not respected : command must be a 12 bytes value")
        counter = counter + 1

    # Payload length (4 bytes)
    counter = 0
    length_payload = get_first_4_bytes_payload_length(payload)
    for i in length_payload:
        bitcoin_msg.append(i)
        if counter > 3:
            raise ProtocolException("Error Bitcoin Protocol not respected : payload_length must be a 4 bytes value")
        counter = counter + 1

    # Payload Checksum sha256(sha256(payload)) (4 bytes)
    counter = 0
    checksum_payload = get_first_4_bytes_payload_checksum(payload)
    for i in checksum_payload:
        bitcoin_msg.append(i)
        if counter > 3:
            raise ProtocolException(
                "Error Bitcoin Protocol not respected : payload_checksum must be a 4 bytes value")
        counter = counter + 1

    # Payload (4 bytes)
    counter = 0
    for i in payload:
        bitcoin_msg.append(i)
        if counter > int.from_bytes(length_payload, byteorder='little'):
            raise ProtocolException(
                "Error Bitcoin Protocol not respected : payload must be of length equal to payload_length")
        counter = counter + 1

    return bitcoin_msg
