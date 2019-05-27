import hashlib
import ipaddress
import time

import math

from .ProtocolException import *
from .Protocol_Constant import *

"""
                FUNCTION THAT ARE NEEDED FOR RECEIVING PACKETS
"""


def treat_variable_length_integer(payload):
    nb_entries = 0
    payload_left = payload

    if len(payload) > 0:
        format = payload[0]

        if format == 0xFD:
            nb_entries = int.from_bytes(payload[1:3], byteorder="little")
            payload_left = payload[3::]

        elif format == 0xFE:
            nb_entries = int.from_bytes(payload[1:5], byteorder="little")
            payload_left = payload[5::]

        elif format == 0xFF:
            nb_entries = int.from_bytes(payload[1:9], byteorder="little")
            payload_left = payload[9::]
        else:
            nb_entries = format
            payload_left = payload[1::]

    return nb_entries, payload_left


def treat_variable_length_list(payload):
    nb_entries = 0
    entries = bytearray()

    if len(payload) > 0:
        format = payload[0]

        if format == 0xFD:
            nb_entries = int.from_bytes(payload[1:3], byteorder="little")
            entries = payload[3::]

        elif format == 0xFE:
            nb_entries = int.from_bytes(payload[1:5], byteorder="little")
            entries = payload[5::]

        elif format == 0xFF:
            nb_entries = int.from_bytes(payload[1:9], byteorder="little")
            entries = payload[9::]
        else:
            nb_entries = format
            entries = payload[1::]

    return nb_entries, entries


def treat_variable_length_string(payload):
    nb_entries, payload_left = treat_variable_length_integer(payload)

    result = payload_left[0:nb_entries].decode(Protocol_Constant.STRING_ENCODING)

    return result, payload_left[nb_entries::]


def treat_bitcoin_tx_in_list_bytes(nb_entries, tx_in_bytes):
    tx_in_list = list()

    i = 0
    payload_left = tx_in_bytes
    while i < nb_entries:
        tx_in = dict()

        tx_in["previous_output"] = treat_outpoint_bytes(payload_left[0:36])

        script_length, payload_left = treat_variable_length_list(payload_left[36::])

        tx_in["signature_script"] = treat_signature_script_bytes(payload_left[0:script_length])

        tx_in["sequence"] = int.from_bytes(payload_left[script_length:script_length + 4], byteorder="little")

        payload_left = payload_left[script_length + 4::]

        tx_in_list.append(tx_in)

        i = i + 1

    return tx_in_list, payload_left


def treat_outpoint_bytes(outpoint_bytes):
    outpoint = dict()

    outpoint["hash"] = outpoint_bytes[0:32].decode(Protocol_Constant.STRING_ENCODING)
    outpoint["index"] = int.from_bytes(outpoint_bytes[32:36], byteorder="little")

    return outpoint


def treat_signature_script_bytes(signature_script_bytes):
    signature_script = signature_script_bytes.decode(Protocol_Constant.STRING_ENCODING)

    return signature_script


def treat_bitcoin_tx_out_list_bytes(nb_entries, tx_out_bytes):
    tx_out_list = list()

    i = 0
    payload_left = tx_out_bytes
    while i < nb_entries:
        tx_out = dict()

        tx_out["value"] = int.from_bytes(payload_left[0:8], byteorder="little")

        pk_script_length, payload_left = treat_variable_length_list(payload_left[8::])

        tx_out["pk_script"] = treat_pk_script_bytes(payload_left[0:pk_script_length])

        payload_left = payload_left[pk_script_length::]

        tx_out_list.append(tx_out)

        i = i + 1

    return tx_out_list, payload_left


def treat_pk_script_bytes(pk_script_bytes):
    pk_script = pk_script_bytes.decode(Protocol_Constant.STRING_ENCODING)

    return pk_script


def treat_tx_witness_list_bytes(nb_entries, tx_witness_bytes):
    tx_witness_list = list()

    i = 0
    payload_left = tx_witness_bytes
    while i < nb_entries:
        tx_witness = dict()

        witness_data_size, payload_left = treat_variable_length_list(payload_left)

        tx_witness["raw_witness_data"] = bytearray(payload_left[0:witness_data_size])

        payload_left = payload_left[witness_data_size::]

        tx_witness_list.append(tx_witness)

        i = i + 1

    return tx_witness_list, payload_left


def treat_inv_list(nb_entries, inv_list):
    inv_table = list()

    i = 0
    while i < nb_entries:
        inv = inv_list[
              i * Protocol_Constant.INVENTORY_VECTOR_SIZE:i * Protocol_Constant.INVENTORY_VECTOR_SIZE + Protocol_Constant.INVENTORY_VECTOR_SIZE]

        object_type = int.from_bytes(inv[0:4], byteorder="little")
        object_hash = int.from_bytes(inv[4:36], byteorder="little")

        inv_table.append((object_type, object_hash))

        i = i + 1

    return inv_table, inv_list[i*Protocol_Constant.INVENTORY_VECTOR_SIZE::]


def treat_network_address(net_addr, version_msg=False):
    if version_msg:
        service = int.from_bytes(net_addr[0:8], byteorder="little")
        ip = decode_ip(net_addr[8:24])
        port = int.from_bytes(net_addr[24:26], byteorder="big")
        result = [service, ip, port]
    else:
        time = int.from_bytes(net_addr[0:4], byteorder="little")
        service = int.from_bytes(net_addr[4:12], byteorder="little")
        ip = decode_ip(net_addr[12:28])
        port = int.from_bytes(net_addr[28:30], byteorder="big")
        result = [time, service, ip, port]

    return result


def treat_block_header(block_header_bytes):
    version = int.from_bytes(block_header_bytes[0:4], byteorder="little")
    prev_block_hash = int.from_bytes(block_header_bytes[4:36], byteorder="little")
    merkle_root = int.from_bytes(block_header_bytes[36:68], byteorder="little")
    timestamp = int.from_bytes(block_header_bytes[68:72], byteorder="little")
    bits = int.from_bytes(block_header_bytes[72:76], byteorder="little")
    nonce = int.from_bytes(block_header_bytes[76:80], byteorder="little")

    txn_count, payload_left = treat_variable_length_integer(block_header_bytes[80::])

    return version, prev_block_hash, merkle_root, timestamp, bits, nonce, txn_count


def treat_block_locator_bytes(payload):
    nb_entries, entries = treat_variable_length_list(payload)

    block_locator_list = list()

    i = 0
    while i < nb_entries:
        block_locator_hash_bytes = entries[0:Protocol_Constant.BLOCK_LOCATOR_HASH_SIZE]

        if len(block_locator_hash_bytes) < Protocol_Constant.BLOCK_LOCATOR_HASH_SIZE:
            return block_locator_list, entries

        block_locator_list.append(int.from_bytes(block_locator_hash_bytes, byteorder="little"))

        entries = entries[(Protocol_Constant.BLOCK_LOCATOR_HASH_SIZE + Protocol_Constant.BLOCK_LOCATOR_HASH_SIZE)::]

        i = i + 1

    return block_locator_list, entries


def decode_ip(ip):
    if ip[0:12] == (0x00.to_bytes(10, byteorder='little') + 0xFFFF.to_bytes(2, byteorder='little')):
        # IPv4 Address
        ip_add = ip[12:16]
        result = ""
        for i in ip_add:
            result = result + str(i) + "."
    else:
        # IPv6 Address
        i = 0
        result = ""
        while i < len(ip):
            byte = int.from_bytes(ip[i:i + 2], byteorder="big")
            result = result + hex(byte).split("0x")[1] + ":"
            i = i + 2

    result = str(ipaddress.ip_address(result[0:len(result) - 1]))

    return result


def get_origin_network(net):
    if len(net) != 4:
        raise UnknownOriginNetworkException(
            "UnknownOriginNetwork Exception : The Origin Network must be a 4 bytes value.")

    elif net[::-1] == Protocol_Constant.MAINNET_MAGIC_VALUE:
        return "mainnet"
    elif net[::-1] == Protocol_Constant.TESTNET_MAGIC_VALUE:
        return "testnet"
    elif net[::-1] == Protocol_Constant.TESTNET3_MAGIC_VALUE:
        return "testnet3"
    elif net[::-1] == Protocol_Constant.NAMECOIN_MAGIC_VALUE:
        return "namecoin"
    else:
        raise UnknownOriginNetworkException(
            "UnknownOriginNetwork Exception : The Origin Network mentionned is not known.")


def get_command(command_byte):
    result = command_byte.decode(Protocol_Constant.STRING_ENCODING).replace('\x00', '')

    return result


"""
                FUNCTION THAT ARE NEEDED FOR SENDING PACKETS
"""


def block_header_to_bytes(version, prev_block_hash, merkle_root, timestamp, bits, nonce, txn_count):
    block_header_bytes = bytearray()

    version_bytes = version.to_bytes(4, byteorder="little")
    prev_block_hash_bytes = int.from_bytes(prev_block_hash, byteorder="little")
    merkle_root_bytes = int.from_bytes(merkle_root, byteorder="little")
    timestamp_bytes = timestamp.to_bytes(4, byteorder="little")
    bits_bytes = bits.to_bytes(4, byteorder="little")
    nonce_bytes = nonce.to_bytes(4, byteorder="little")

    txn_count_bytes = get_variable_length_integer(txn_count)

    block_header_bytes = block_header_bytes + version_bytes + prev_block_hash_bytes + merkle_root_bytes + timestamp_bytes + bits_bytes + nonce_bytes + txn_count_bytes

    return block_header_bytes


def get_inv_list(inv_list):
    inv_list_bytes = bytearray()

    for type, hash in inv_list:
        inv_vector = type.to_bytes(4, byteorder="little") + hash.to_bytes(32, byteorder="little")
        inv_list_bytes = inv_list_bytes + inv_vector

    return inv_list_bytes


def bitcoin_tx_in_list_to_bytes(tx_in_list):
    tx_in_list_bytes = bytearray()

    for tx_in in tx_in_list:
        previous_output_bytes = outpoint_to_bytes(tx_in["previous_output"])

        signature_script_bytes = signature_script_to_bytes(tx_in["signature_script"])

        script_length_bytes = get_variable_length_integer(len(signature_script_bytes))

        sequence_bytes = tx_in["sequence"].to_bytes(4, byteorder="little")

        tx_in_list_bytes = tx_in_list_bytes + previous_output_bytes + script_length_bytes + signature_script_bytes + sequence_bytes

    return tx_in_list_bytes


def outpoint_to_bytes(outpoint):
    hash_bytes = outpoint["hash"].encode(Protocol_Constant.STRING_ENCODING)
    index_bytes = outpoint["index"].to_bytes(4, byteorder="little")

    outpoint_bytes = hash_bytes + index_bytes

    return outpoint_bytes


def signature_script_to_bytes(signature_script):
    signature_script_bytes = signature_script.encode(Protocol_Constant.STRING_ENCODING)

    return signature_script_bytes


def bitcoin_tx_out_list_to_bytes(tx_out_list):
    tx_out_list_bytes = bytearray()

    for tx_out in tx_out_list:
        value_bytes = tx_out["value"].to_bytes(8, byteorder="little")
        pk_script_bytes = pk_script_to_bytes(tx_out["pk_script"])
        pk_script_length = get_variable_length_integer(len(pk_script_bytes))

        tx_out_list_bytes = tx_out_list_bytes + value_bytes + pk_script_length + pk_script_bytes

    return tx_out_list_bytes


def pk_script_to_bytes(pk_script):
    pk_script_bytes = pk_script.encode(Protocol_Constant.STRING_ENCODING)

    return pk_script_bytes


def bitcoin_tx_witness_list_to_bytes(tx_witness_list):
    tx_witness_list_bytes = bytearray()

    for tx_witness in tx_witness_list:
        witness_data = tx_witness["raw_witness_data"]
        witness_data_length = get_variable_length_integer(len(witness_data))

        tx_witness_list_bytes = tx_witness_list_bytes + witness_data_length + witness_data

    return tx_witness_list_bytes


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


def block_locator_list_to_bytes(block_locator_list):
    block_locator_list_bytes = bytearray()

    for block_locator in block_locator_list:
        block_locator_bytes = block_locator.to_bytes(32, byteorder="little")
        block_locator_list_bytes = block_locator_list_bytes + block_locator_bytes

    return block_locator_list_bytes


def get_variable_length_integer(value):
    if value < 0xFD:
        var_int = value.to_bytes(1, byteorder='little')
    elif value <= 0xFFFF:
        var_int = 0xFD.to_bytes(1, byteorder='little') + value.to_bytes(2, byteorder='little')
    elif value <= 0xFFFFFFFF:
        var_int = 0xFE.to_bytes(1, byteorder='little') + value.to_bytes(4, byteorder='little')
    else:
        var_int = 0xFF.to_bytes(1, byteorder='little') + value.to_bytes(8, byteorder='little')

    return var_int


def get_variable_length_string(string):
    var_int = get_variable_length_integer(len(string))

    return var_int + string.encode(Protocol_Constant.STRING_ENCODING)


def get_network_address_field(service, ip_address, port, is_version=False, advertising=False,
                              timestamp=float("nan")):
    net_addr = bytearray()

    if not is_version:
        if advertising:
            net_addr = net_addr + int(time.time()).to_bytes(4, byteorder='little')
        else:
            net_addr = net_addr + int(timestamp).to_bytes(4, byteorder='little')
            if math.isnan(timestamp):
                raise MissingTimestampExeception(
                    "MissingTimestamp Exception : You have to mention the last time_to_crawl you connect to the node.")

    # Service Fields mentionning the service offer by the device associated to the IP Address
    service_byte = service.to_bytes(8, byteorder='little')

    ip_address_bytes = encode_ip(ip_address)

    port_bytes = port.to_bytes(2, byteorder='little')

    net_addr = net_addr + service_byte + ip_address_bytes + port_bytes

    return net_addr


def get_command_field(command):
    result = bytearray()
    result.extend(map(ord, command))
    to_pad = 12 - len(result)

    result = result + 0x00.to_bytes(to_pad, byteorder='little')

    return result


# Return the first 4 bytes of the Payload's length
def get_first_4_bytes_payload_length(payload):
    length = len(payload)
    return length.to_bytes(4, byteorder='little')


# Return the first 4 bytes of the Payload's Checksum
def get_first_4_bytes_payload_checksum(payload):
    sha_signature = hashlib.sha256(hashlib.sha256(payload).digest()).digest()
    return sha_signature[0:4]


"""
                    OTHER
"""


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
