import time
from context import *


def measure_throughput():
    test_key = 5
    test_value = 10
    for difficulty in range(1, 6):
        storage = Storage(bootstrap=None, miner=True, difficulty=difficulty, test=False, debug=False)
        test_key += 1
        start = time.time()
        storage.put(test_key, test_value, block=True)
        end = time.time()
        time_elapsed = end - start
        print("It took {} with difficulty {}".format(time_elapsed, difficulty))
        del storage


if __name__ == "__main__":
    measure_throughput()
