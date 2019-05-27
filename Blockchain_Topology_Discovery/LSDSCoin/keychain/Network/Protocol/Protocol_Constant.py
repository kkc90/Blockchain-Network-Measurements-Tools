class Protocol_Constant():
    STRING_ENCODING = "utf-8"
    IMPLEMENTED_MESSAGES = ["Version_Message", "Addr_Message", "GetAddr_Message",
                            "Ping_Message", "Pong_Message", "Verack_Message", "Inv_Message", "GetData_Message",
                            "NotFound_Message", "GetBlock_Message", "GetHeader_Message", "Tx_Message",
                            "Bitcoin_Tx_Message", "Block_Message", "MemPool_Message"]

    NETWORK_ADDRESS_SIZE = 30  # bytes
    INVENTORY_VECTOR_SIZE = 36  # bytes
    BLOCK_LOCATOR_HASH_SIZE = 32  # bytes

    # Magic Values
    MAINNET_MAGIC_VALUE = bytearray([0xD9, 0xB4, 0xBE, 0xF9])
    TESTNET_MAGIC_VALUE = bytearray([0xDA, 0xB5, 0xBF, 0xFA])
    TESTNET3_MAGIC_VALUE = bytearray([0x07, 0x09, 0x11, 0x0B])
    NAMECOIN_MAGIC_VALUE = bytearray([0xFE, 0xB4, 0xBE, 0xF9])

    # Service Flags
    NODE_NONE = 0  # Nothing
    NODE_NETWORK = (1 << 0)  # Node is capable of serving the complete Block Chain
    NODE_GETUTXO = (1 << 1)  # Node is capable of responding to the getutxo protocol request
    NODE_BLOOM = (1 << 2)  # Node is capable and willing to handle bloom-filtered connections
    NODE_WITNESS = (1 << 3)  # Node can be asked for blocks and transactions including witness data
    NODE_XTHIN = (1 << 4)  # Node supports Xtreme Thinblocks
    NODE_NETWORK_LIMITED = (1 << 10)  # Node is capable of serving the last 288 blocks (2 days)

    # Inventory Vector Type Flags
    INV_VECTOR_ERROR = 0  # Any data of with this number may be ignored
    INV_VECTOR_MSG_TX = 1  # Hash is related to a transaction
    INV_VECTOR_MSG_BLOCK = 2  # Hash is related to a data block
    INV_VECTOR_MSG_FILTERED_BLOCK = 3  # NOT IMPLEMENTED

    # Hash of a block header; identical to MSG_BLOCK. Only to be used in getdata message.
    #                                  Indicates the reply should be a merkleblock message rather than a block message;
    #                                               this only works if a bloom filter has been set.

    INV_VECTOR_MSG_CMPCT_BLOCK = 4  # NOT IMPLEMENTED

    # Hash of a block header; identical to MSG_BLOCK. Only to be used in getdata message.
    #   Indicates the reply should be a cmpctblock message. See BIP 152 for more info
