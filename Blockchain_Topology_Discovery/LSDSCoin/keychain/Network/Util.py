from .NetworkException import *
from .Network_Constant import *
from .Protocol.Bitcoin_Messages import *
from ..Blockchain import *
from ..Util import *


def transaction_to_tx_message(transaction):
    key = transaction.getKey()
    value = transaction.getValue()
    public_key = transaction.getOrigin()
    timestamp = transaction.getTimestamp()
    signature = transaction.getSignature()

    return Tx_Message.Tx_Message(key, value, public_key, timestamp, signature=signature)


def tx_message_to_transaction(tx_message):
    key = tx_message.get_key()
    value = tx_message.get_value()
    public_key = tx_message.get_public_key()
    timestamp = tx_message.get_timestamp()
    signature = bytes(tx_message.get_signature())

    return Transaction.Transaction(key, value, public_key, timestamp, signature=signature)


def transaction_to_bitcoin_tx_message(transaction):
    version = Network_Constant.PROTOCOL_VERSION

    prev_output = dict()
    prev_output["hash"] = transaction.get_key()
    prev_output["index"] = 0

    tx_in = dict()
    tx_in["previous_output"] = prev_output
    tx_in["signature_script"] = repr(transaction.getSignature())
    tx_in["sequence"] = Network_Constant.PROTOCOL_VERSION

    tx_in_list = [tx_in]

    tx_out = dict()

    tx_out["value"] = transaction.get_value()
    tx_out["pk_script"] = public_key_to_bytes(transaction.getOrigin()).decode("utf-8")

    tx_out_list = [tx_out]
    tx_witness_list = []
    lock_time = int(transaction.get_timestamp())

    tx_msg = Bitcoin_Tx_Message.Bitcoin_Tx_Message(version, tx_in_list, tx_out_list, tx_witness_list, lock_time)

    return tx_msg


def bitcoin_tx_message_to_transaction(bitcoin_tx_msg):
    tx_in_list = bitcoin_tx_msg.get_tx_in_list()
    tx_out_list = bitcoin_tx_msg.get_tx_out_list()

    tx_in = tx_in_list[0]
    tx_out = tx_out_list[0]

    key = tx_in["previous_output"]["hash"]
    value = tx_out["value"]

    origin = bytes_to_public_key(tx_out["pk_script"])

    timestamp = bitcoin_tx_msg.get_lock_time()

    return Transaction(key, value, origin, timestamp)


def block_to_block_message(block):
    version = block.getIndex()

    prev_block = block.getPrevBlockHash()
    merkle_root = block.getMerkleRoot()

    timestamp = block.getTimestamp()
    bits = block.getDifficulty()
    nonce = block.getBlockNonce()
    transaction_list = block.getTransactions()

    txn_list = list()
    for transaction in transaction_list:
        tx_msg = transaction_to_tx_message(transaction)
        txn_list.append(tx_msg)

    return Block_Message.Block_Message(version, prev_block, merkle_root, timestamp, bits, nonce, txn_list)


def block_message_to_block(block_msg):

    index = block_msg.get_version()
    prev_block_hash = block_msg.get_prev_block()
    merkle_root = block_msg.get_merkle_root()
    txn_list = block_msg.get_txn_list()

    transaction_list = list()

    for tx in txn_list:
        transaction = tx_message_to_transaction(tx)
        transaction_list.append(transaction)

    difficulty = block_msg.get_bits()
    timestamp = block_msg.get_timestamp()
    nonce = block_msg.get_nonce()

    block = Block.Block(index, prev_block_hash, transaction_list, difficulty, timestamp=timestamp, nonce=nonce,
                        hash=merkle_root)

    return block
