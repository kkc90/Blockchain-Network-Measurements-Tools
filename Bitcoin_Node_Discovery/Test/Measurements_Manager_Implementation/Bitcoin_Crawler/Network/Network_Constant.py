class Network_Constant():
    # Time in seconds

    PROTOCOL_VERSION = 70015  # Protocol Version used by the peer.

    DEFAULT_PORT = 8333

    MAX_NUMBER_OF_OBJECT_IN_INV_MESSAGE = 1000

    QUERY_TIMEOUT = 30  # Time before considering that an unanswered request can be queried again.

    SOCKET_TIMEOUT = 1/2  # Socket Timeout (cfr. "socket" library documentation).

    HANDSHAKE_TIMEOUT = 5  # Time before considering that a handshake failed.

    PING_TIMEOUT = 10  # Time before considering that a peer didn't answer a PING message.

    ADDR_TIMEOUT = 20  # Time before considering that a peer didn't answer a ADDR message.

    GETADDR_TIMEOUT = 20  # Time before considering that a peer didn't answer a GETADDR message.

    TIMEOUT_BEFORE_ASK_ALIVE = 15  # The number of seconds before asking a peer if it's alive.

    NB_TIMEOUT_BEFORE_UNACTIVE = 2  # Number of Timeouts before considering that a peer is not active anymore.

    TIMEOUT_RETRY_ASK_NEW_PEER = 0  # Time before asking peers for other peers' IPs.
