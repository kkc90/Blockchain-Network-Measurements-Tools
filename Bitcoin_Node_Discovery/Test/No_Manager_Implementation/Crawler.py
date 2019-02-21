import getip
from Protocol import Protocol
from IP_Lookup import IP_Lookup


class Crawler:
    def __init__(self, measurements, measurements_manager, network_to_crawl, nb_thread, displayer):
        self.measurements_manager = measurements_manager
        self.measurements = measurements
        self.network_to_crawl = network_to_crawl
        self.src_port = 8333
        self.dst_port = 8333
        self.displayer = displayer

        self.src_ip = getip.get()

        self.target_service = Protocol.NODE_NETWORK
        self.nb_thread = nb_thread
        self.threads = []

    def start(self):
        i = 0

        while i < self.nb_thread:
            thread = IP_Lookup(self.measurements_manager, self.network_to_crawl, self.src_ip, self.target_service, i,
                               self.displayer)
            thread.start()
            self.threads.append(thread)
            i = i + 1

    def isFinish(self):
        i = 0
        while i < self.nb_thread:
            if self.threads[i].isTerminated() is False:
                return False
            i = i + 1
        return True

    def kill(self):
        i = 0

        while i < self.nb_thread:
            self.threads[i].kill()
            i = i + 1


    def join(self):
        i = 0

        while i < self.nb_thread:
            self.threads[i].join()
            i = i + 1

