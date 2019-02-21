import hashlib
import ipaddress
import time
import math
from Protocol.ProtocolException import *
from Protocol.Bitcoin_Messages import *

COMMAND = {"version", "verack", "getaddr", "addr", "ping", "pong"}

# Service Flags
NODE_NONE = 0  # Nothing
NODE_NETWORK = (1 << 0)  # Node is capable of serving the complete Block Chain
NODE_GETUTXO = (1 << 1)  # Node is capable of responding to the getutxo protocol request
NODE_BLOOM = (1 << 2)  # Node is capable and willing to handle bloom-filtered connections
NODE_WITNESS = (1 << 3)  # Node can be asked for blocks and transactions including witness data
NODE_XTHIN = (1 << 4)  # Node supports Xtreme Thinblocks
NODE_NETWORK_LIMITED = (1 << 10)  # Node is capable of serving the last 288 blocks (2 days)


def bitcoin_treat_packet(net, bitcoin_command, length, checksum, payload):
    payload_sha = payload_checksum(payload)
    payload_length = int.from_bytes(length, byteorder="little")

    if len(payload) != payload_length:
        raise DiscardedPacketException((
                                       "DiscardedPacket Exception : The length of the payload is not the one mentionned.\n " + "Payload Length = ",
                                       len(payload), " | Packet's Payload length = ", payload_length))

    if payload_sha != checksum:
        raise DiscardedPacketException((
                                       "DiscardedPacket Exception : The payload of the packet has been modified (wrong checksum).\n" + "Calculated Checksum = ",
                                       payload_sha, " | Packet's Checksum = ", checksum))

    if bitcoin_command == "version":
        result = bitcoin_treat_version_packet(payload)
    elif bitcoin_command == "verack":
        result = bitcoin_treat_verack_packet(payload)
    elif bitcoin_command == "getaddr":
        result = bitcoin_treat_getaddr_packet(payload)
    elif bitcoin_command == "addr":
        result = bitcoin_treat_addr_packet(payload)
    elif bitcoin_command == "ping":
        result = bitcoin_treat_ping_packet(payload)
    elif bitcoin_command == "pong":
        result = bitcoin_treat_pong_packet(payload)
    else:
        raise UnsupportedBitcoinCommandException(
            ("UnsupportedBitcoinCommand Exception : Command " + bitcoin_command + " is not supported."))
    return result


def bitcoin_treat_version_packet(payload):
    version = payload[0:4]

    services = payload[4:12]

    timestamp = payload[12:20]

    addr_rcv = payload[20:46]

    receiver_info = treat_bitcoin_network_address_field(addr_rcv, version_msg=True)

    addr_from = payload[46:72]

    sender_info = treat_bitcoin_network_address_field(addr_from, version_msg=True)

    nonce = payload[72:80]

    return Version_Message.Version_Message("version", int.from_bytes(version, byteorder="little"), sender_info[0],
                                           sender_info[1], sender_info[2], receiver_info[0], receiver_info[1],
                                           receiver_info[2], int.from_bytes(nonce, byteorder="little"))


def bitcoin_treat_verack_packet(payload):
    return Verack_Message.Verack_Message("verack")


def bitcoin_treat_getaddr_packet(payload):
    return GetAddr_Message.Getaddr_Message("getaddr")


def bitcoin_treat_addr_packet(payload):
    if(len(payload) > 0):
        format = payload[0]

        if format == 0xFD:
            nb_entries = int.from_bytes(payload[1:3], byteorder="little")
            addr_list = payload[3::]

        elif format == 0xFE:
            nb_entries = int.from_bytes(payload[1:5], byteorder="little")
            addr_list = payload[5::]

        elif format == 0xFF:
            nb_entries = int.from_bytes(payload[1:9], byteorder="little")
            addr_list = payload[9::]
        else:
            nb_entries = format
            addr_list = payload[1::]

        return treat_addr_list(nb_entries, addr_list)
    else:
        raise ProtocolException("Protocol Exception: ADDR Packet must contain a payload.")

def treat_addr_list(nb_entries, addr_list):
    i = 0
    addr_msg = Addr_Message.Addr_Message("addr")

    while i < nb_entries:
        net_addr = addr_list[i * 30:i * 30 + 30]  # Net Addr is 30 Bytes -> Bitcoin Protocol
        treat_net_addr(net_addr, addr_msg)
        i = i + 1

    return addr_msg


def treat_net_addr(net_addr, addr_msg):
    timestamp = net_addr[0:4]

    service = net_addr[4:12]

    ip = net_addr[12:28]

    port = net_addr[28:30]

    addr_msg.add_IP_Service(decode_ip(ip), int.from_bytes(service, byteorder="little"))
    addr_msg.add_IP_Table(decode_ip(ip), int.from_bytes(port, byteorder="big"))


def bitcoin_treat_ping_packet(payload):
    if len(payload) > 8:
        raise DiscardedPacketException((
                                                   "DiscardedPacket Exception : The length of the PING payload is not expected (" + str(
                                               len(payload)) + " != 8."))

    return Ping_Message.Ping_Message("ping", ping_nonce=int.from_bytes(payload, byteorder="little"))


def bitcoin_treat_pong_packet(payload):
    if len(payload) > 8:
        raise DiscardedPacketException((
                                                   "DiscardedPacket Exception : The length of the PONG payload is not expected (" + str(
                                               len(payload)) + " != 8."))

    return Pong_Message.Pong_Message("pong", pong_nonce=int.from_bytes(payload, byteorder="little"))


# Return a bitcoin Msg ready to be sent to a peer
def bitcoin_msg(Bitcoin_Message, origin_network):
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
    length_payload = payload_length(payload)
    for i in length_payload:
        bitcoin_msg.append(i)
        if counter > 3:
            raise ProtocolException("Error Bitcoin Protocol not respected : payload_length must be a 4 bytes value")
        counter = counter + 1

    # Payload Checksum sha256(sha256(payload)) (4 bytes)
    counter = 0
    checksum_payload = payload_checksum(payload)
    for i in checksum_payload:
        bitcoin_msg.append(i)
        if counter > 3:
            raise ProtocolException("Error Bitcoin Protocol not respected : payload_checksum must be a 4 bytes value")
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


def get_variable_length_integer(value):
    if value < 0xFD:
        var_int = value.to_bytes(1, byteorder='little')
    elif value <= 0xFFFF:
        var_int = 0xFD.to_bytes(1, byteorder='little') + value.to_bytes(3, byteorder='little')
    elif value <= 0xFFFFFFFF:
        var_int = 0xFE.to_bytes(1, byteorder='little') + value.to_bytes(5, byteorder='little')
    else:
        var_int = 0xFF.to_bytes(1, byteorder='little') + value.to_bytes(9, byteorder='little')

    return var_int


def treat_bitcoin_network_address_field(net_addr, version_msg=False):
    if version_msg:
        service = int.from_bytes(net_addr[0:8], byteorder="little")
        addr = decode_ip(net_addr[8:24])
        port = int.from_bytes(net_addr[24:26], byteorder="little")
        result = [service, addr, port]
    else:
        time = int.from_bytes(net_addr[0:4], byteorder="little")
        service = int.from_bytes(net_addr[4:12], byteorder="little")
        addr = decode_ip(net_addr[12:28])
        port = int.from_bytes(net_addr[28:30], byteorder="little")
        result = [time, service, addr, port]

    return result


def encode_ip(ip):
    if get_ip_type(ip) == "ipv4":
        result = bytearray()
        result = result + 0x00.to_bytes(10, byteorder='little') + 0xFFFF.to_bytes(2, byteorder='little')
        ip_parsed = ip.split(".")
        for i in ip_parsed:
            result.append(int(i))

    else:
        ip_add = ipaddress.ip_address(ip)
        result = bytearray()
        result = result + int(ip_add).to_bytes(16, byteorder="big")
    return result


def decode_ip(ip):
    if int.from_bytes(ip[0:10], byteorder="little") == 0:
        ip_add = ip[12:16]
        result = ""
        for i in ip_add:
            result = result + str(i) + "."
    else:
        i = 0
        result = ""
        while i < len(ip):
            byte = int.from_bytes(ip[i:i + 2], byteorder="big")
            result = result + hex(byte).split("0x")[1] + ":"
            i = i + 2

    result = str(ipaddress.ip_address(result[0:len(result) - 1]))
    return result


def bitcoin_network_address_field(service, ip_address, port, is_version=False, advertising=False,
                                  timestamp=float("nan")):
    net_addr = bytearray()
    if not is_version:
        if advertising:
            timestamp = int(time.time()).to_bytes(4, byteorder='little')
        else:
            if math.isnan(timestamp):
                raise MissingTimestampExeception(
                    "MissingTimestamp Exception : You have to mention the last time you connect to the node.")

    # Service Fields mentionning the service offer by the device associated to the IP Address
    service_byte = service.to_bytes(8, byteorder='little')
    for i in service_byte:
        net_addr.append(i)

    ip_address_bytes = encode_ip(ip_address)
    # to_pad = 16 - len(ip_address_bytes)

    # ip_address_bytes = ip_address_bytes + (0x00).to_bytes((to_pad), byteorder='little')

    for i in ip_address_bytes:
        net_addr.append(i)

    port_bytes = port.to_bytes(2, byteorder='big')

    for i in port_bytes:
        net_addr.append(i)
    return net_addr


def get_origin_network(net):
    if len(net) != 4:
        raise UnknownOriginNetworkException(
            "UnknownOriginNetwork Exception : The Origin Network must be a 4 bytes value.")
    elif net[3] == 217 and net[2] == 180 and net[1] == 190 and net[0] == 249:
        return "mainnet"
    elif net[3] == 218 and net[2] == 181 and net[1] == 191 and net[0] == 250:
        return "testnet"
    elif net[3] == 7 and net[2] == 9 and net[1] == 17 and net[0] == 11:
        return "testnet3"
    else:
        raise UnknownOriginNetworkException(
            "UnknownOriginNetwork Exception : The Origin Network mentionned is not known.")


# Return the first 4 bytes of the Payload's length
def payload_length(payload):
    length = len(payload)
    return length.to_bytes(4, byteorder='little')


# Return the first 4 bytes of the Payload's Checksum
def payload_checksum(payload):
    sha_signature = hashlib.sha256(hashlib.sha256(payload).digest()).digest()
    return sha_signature[0:4]


def get_command_field(command):
    if command in COMMAND:
        result = bytearray()
        result.extend(map(ord, command))
        to_pad = 12 - len(result)

        result = result + 0x00.to_bytes(to_pad, byteorder='little')

        return result
    else:
        raise UnsupportedBitcoinCommandException(
            ("UnsupportedBitcoinCommand Exception : The command " + command + " is not supported."))


def get_command(command_byte):
    result = command_byte.decode("utf-8")

    if "version" in result:
        return "version"
    elif "verack" in result:
        return "verack"
    elif "addr" in result:
        return "addr"
    elif "getaddr" in result:
        return "getaddr"
    elif "ping" in result:
        return "ping"
    elif "pong" in result:
        return "pong"
    else:
        raise UnsupportedBitcoinCommandException(
            ("UnsupportedBitcoinCommand Exception : The command " + result + " is not supported."))


# INV Message transmits one or more inventories of obkects known to the transmitting peer.
def bitcoin_inv_payload():
    payload = bytearray()

    return payload


# TX Message transmits a single transaction.
def bitcoin_tx_payload():
    payload = bytearray()

    return payload


# HEADERS Message transmits one or more block headers to a node which previously requestes certain headers with a GETHEADERS Message.
def bitcoin_header_payload():
    payload = bytearray()

    return payload


# BLOCK Message transmit a single serialized block.
def bitcoin_block_payload():
    payload = bytearray()

    return payload


# MEMPOOL Message request the TXID's of transactions that the receiving node has verified as valid but which have not yet appeared in a block.
def bitcoin_mempool_payload():
    payload = bytearray()

    return payload


# NOTFOUND Message is a reply to a GETDATA Message which requested an obkect the receiving node does not have available for relay.
def bitcoin_notfound_payload():
    payload = bytearray()

    return payload


# REJECT Message informs the receiving node that one of its previous messages has been rejected
def bitcoin_reject_payload():
    payload = bytearray()

    return payload


# BLOCKTXN Message is a reply to a preiously sent GETBLOCKTXN Message which contains a BlockTransactions
def bitcoin_blocktxn_payload():
    payload = bytearray()

    return payload


# MERKLEBLOCK Message is a reply to a GETDATA Message which requested a block using the inventory type MSG_MERKLEBLOCK.
def bitcoin_merkleblock_payload():
    payload = bytearray()

    return payload


# GETDATA Message requests one or more data objects from another node.
def bitcoin_getdata_payload():
    payload = bytearray()

    return payload


# GETBLOCKS Message requests an INV Message that provides block header hashes starting from a particular point in the block chain.
def bitcoin_getblocks_payload():
    payload = bytearray()

    return payload


# GETHEADERS Message requests a headers message that provides block headers starting from a particular point in the block chain.
def bitcoin_getheaders_payload():
    payload = bytearray()

    return payload


# GETBLOCKTXN Message requests a BlockTransaction to the receiving node. It contains a BlockTransactionRequest.
def bitcoin_getblocktxn_payload():
    payload = bytearray()

    return payload


def get_ip_type(ip_addr):
    try:
        ip = ipaddress.ip_address(ip_addr)
    except ValueError:
        error = "UnknownIPAddressType Exception : Unknown IP Address type of " + ip_addr + "."
        raise UnknownIPAddressTypeException(error)

    version = ip.version
    if version == 4:
        return "ipv4"
    if version == 6:
        return "ipv6"
