import time

STEP = 5
MAX_NB_PROCESS = 50
MIN_NB_PROCESS = 1


class Crawler_Calibrator:
    def __init__(self, crawling_time, min_nb_thread=None, max_nb_thread=None):
        self.min_nb_thread = min_nb_thread
        self.max_nb_thread = max_nb_thread
        self.crawling_time = crawling_time

    def calibrate(self):
        start = time.time()


def main():
    pass


if __name__ == "__main__":
    main()
