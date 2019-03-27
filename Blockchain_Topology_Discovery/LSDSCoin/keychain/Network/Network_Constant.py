class Network_Constant():
    PROTOCOL_VERSION = 70015

    MIN_NUMBER_OF_CONNECTION = 5
    TIMEOUT_RETRY_UNACTIVE_PEER = 600
    NB_TIMEOUT_BEFORE_UNACTIVE = 10



    # Timeouts
    SOCKET_TIMEOUT = 1/2
    HANDSHAKE_TIMEOUT = 5
    PING_TIMEOUT = 5
    ADDR_TIMEOUT = 20  # longuer because bigger packets
