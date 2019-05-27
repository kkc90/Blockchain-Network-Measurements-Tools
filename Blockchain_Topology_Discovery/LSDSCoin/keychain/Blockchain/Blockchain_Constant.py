import datetime


class Blockchain_Constant():

    DIFFICULTY_INCREASE = 1
    GENESIS_PREV_HASH = ("00000000000000000000000000000000").encode("utf-8")

    # Mining NB_BLOCK_BEFORE_DIFFICULTY_UPDATE blocks should take around 4-5 minutes
    # --> otherwise update of the difficulty
    NB_BLOCK_BEFORE_DIFFICULTY_UPDATE = 10

    MINING_TIME = datetime.timedelta(0, 3, 0)

    MAX_NB_TRANSACTION = 10
    MIN_NB_TRANSACTION = 1
