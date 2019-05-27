class Network_Constant():

    PROTOCOL_VERSION = 70015  # Protocol Version used by the peer.

    MAX_NUMBER_OF_OBJECT_IN_INV_MESSAGE = 1000

    # Time in seconds

    MIN_NUMBER_OF_CONNECTION = 5  # The number of connection that the peer will try to get.

    TIMEOUT_RETRY_UNACTIVE_PEER = 60  # Time before retrying to connect to a peer that has been considered as unactive.

    NB_TIMEOUT_BEFORE_UNACTIVE = 5  # Number of Timeouts before considering that a peer is not active anymore.

    TIMEOUT_RETRY_ASK_NEW_PEER = 10  # Time before asking peers for other peers' IPs.

    QUERY_TIMEOUT = 10  # Time before considering that an unanswered request can be queried again.

    SOCKET_TIMEOUT = 1/2  # Socket Timeout (cfr. "socket" library documentation).

    HANDSHAKE_TIMEOUT = 10  # Time before considering that a handshake failed.

    PING_TIMEOUT = 10  # Time before considering that a peer didn't answer a PING message.

    ADDR_TIMEOUT = 20  # Time before considering that a peer didn't answer a ADDR message.
