import datetime


class Blockchain_Constant():

    DIFFICULTY_INCREASE = 0
    GENESIS_PREV_HASH = bytes(0)

    # Mining NB_BLOCK_BEFORE_DIFFICULTY_UPDATE blocks should take around 10 minutes
    # --> otherwise update of the difficulty
    NB_BLOCK_BEFORE_DIFFICULTY_UPDATE = 10
    MINING_TIME = datetime.timedelta(0, 1, 0)
    MAX_NB_TRANSACTION = 10
