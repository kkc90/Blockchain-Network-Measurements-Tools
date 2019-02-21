import datetime
import time
import sys
import os
from threading import Lock, Thread, Event

THREAD_OUTPUT_LOCKER = Lock()
MESSAGE_LOCKER = Lock()

THREAD_OUTPUT = list()
MESSAGE = list()


def print_there(x, y, text):
    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x + 1, y + 1, text))
    sys.stdout.flush()


class Displayer(Thread):

    def __init__(self, measurements, measurements_manager, nb_thread, network_to_crawl, display_prog):
        Thread.__init__(self)
        global THREAD_OUTPUT

        self.measurements = measurements
        self.measurements_manager = measurements_manager
        self.nb_thread = nb_thread
        self.fixed_message_nb = 9
        self.network_to_crawl = network_to_crawl
        self.display_prog = display_prog
        self.start_time = measurements.get_start_time()
        self.__stop_event = Event()
        self.__pause_event = Event()

        tmp = os.popen('stty size', 'r').read().split()
        (self.terminal_rows, self.terminal_column) = (int(tmp[0]), int(tmp[1]))

        i = 0
        while i < nb_thread:
            THREAD_OUTPUT.append(
                ("THREAD " + str(i) + " - " + time.asctime(time.localtime(time.time())) + " :  Initialization ..."))
            i = i + 1

    def run(self):
        os.system('clear')

        if not self.display_prog:
            self.__pause_event.set()

        self.display_progression()

    def display_progression(self):
        global THREAD_OUTPUT
        global MESSAGE

        empty_line = ""

        i = 0
        while i < self.terminal_column - 1:
            empty_line = empty_line + " "
            i = i + 1

        while not self.__stop_event.isSet():
            tmp = os.popen('stty size', 'r').read().split()
            (self.terminal_rows, self.terminal_column) = (int(tmp[0]), int(tmp[1]))
            i = 0

            thread_output_length = len(THREAD_OUTPUT)

            while i < thread_output_length:
                string = THREAD_OUTPUT[i]

                nb_message_to_display = len(MESSAGE)
                message_to_display = list(MESSAGE)

                if (self.terminal_rows - 1 - self.fixed_message_nb - nb_message_to_display) <= 0:
                    os.system('clear')
                    print_there(0, 0, "Increase the Size of your Terminal")
                    break
                elif i % (self.terminal_rows - 1 - self.fixed_message_nb - nb_message_to_display) == 0 or i == thread_output_length:
                    nb_ipv4_to_read = self.measurements.get_nb_to_read("ipv4")
                    nb_ipv6_to_read = self.measurements.get_nb_to_read("ipv6")
                    nb_being_read = self.measurements.get_nb_being_read()
                    nb_readed = self.measurements.get_nb_readed()
                    nb_active = self.measurements.get_nb_active_peers()
                    process_time_stat = self.measurements.get_process_ip_stat_per_query_nb()

                    if -1 in process_time_stat:
                        no_connection_stat = process_time_stat[-1]
                    else:
                        no_connection_stat = -1

                    if 0 in process_time_stat:
                        zero_peer_stat = process_time_stat[0]
                    else:
                        zero_peer_stat = -1

                    if 1000 in process_time_stat:
                        thousand_peer_stat = process_time_stat[1000]
                    else:
                        thousand_peer_stat = -1

                    stop = datetime.datetime.now()

                    print_there(0, 0, empty_line)
                    print_there(0, 0, ("Crawling started at : " + self.start_time.strftime(
                        "%Y-%m-%d %H:%M:%S") + " - Elapsed Time : " + str(
                        (stop - self.start_time).total_seconds()) + " seconds."))
                    print_there(1, 0, empty_line)
                    print_there(1, 0, (str(nb_ipv4_to_read) + " IPv4 Peers to process."))
                    print_there(2, 0, empty_line)
                    print_there(2, 0, (str(nb_ipv6_to_read) + " IPv6 Peers to process."))
                    print_there(3, 0, empty_line)
                    print_there(3, 0, (str(nb_being_read) + " Peers being processed."))
                    print_there(4, 0, empty_line)
                    print_there(4, 0, (str(nb_readed) + " Peers has been processed."))
                    print_there(5, 0, empty_line)
                    print_there(5, 0, (str(nb_active) + " Active peers."))
                    print_there(6, 0, empty_line)
                    print_there(6, 0, (str(no_connection_stat) + " seconds for connecting (connection aborted)."))
                    print_there(7, 0, empty_line)
                    print_there(7, 0, (str(zero_peer_stat) + " seconds for querying 0 peers."))
                    print_there(8, 0, empty_line)
                    print_there(8, 0, (str(thousand_peer_stat) + " seconds for querying 1000 peers."))

                    if self.measurements_manager.measurements_storage_task_failed():
                        print_there(9, 0, "Measurements Storage Task Failed.")
                        self.fixed_message_nb = 10

                    j = 0
                    while j < nb_message_to_display:
                        print_there(self.fixed_message_nb + j, 0, empty_line)
                        print_there(self.fixed_message_nb + j, 0, message_to_display[j])
                        j = j + 1

                    if self.__pause_event.isSet():
                        time.sleep(1)
                        break

                cursor = self.fixed_message_nb + nb_message_to_display + i % (
                            self.terminal_rows - 1 - self.fixed_message_nb - nb_message_to_display)

                print_there(cursor, 0, empty_line)
                print_there(cursor, 0, string)

                if (i + 1) % (self.terminal_rows - 1 - self.fixed_message_nb - nb_message_to_display) == 0 or (
                        i + 1) == thread_output_length:
                    if thread_output_length > self.terminal_rows - 1 - self.fixed_message_nb - nb_message_to_display:
                        time.sleep(5)
                    else:
                        time.sleep(1)

                i = i + 1

    def kill(self):
        self.__stop_event.set()
        os.system('clear')

    def join(self):
        self.__stop_event.set()
        os.system('clear')
        Thread.join(self)

    def pause(self):
        if self.__pause_event.isSet():
            self.__pause_event.clear()
        else:
            self.__pause_event.set()
        os.system('clear')

    def show_progression(self):
        self.__pause_event.clear()
        os.system('clear')

    def display_thread_progression(self, string, thread_nb):
        global THREAD_OUTPUT
        global THREAD_OUTPUT_LOCKER

        if THREAD_OUTPUT_LOCKER.acquire(blocking=False):
            THREAD_OUTPUT[thread_nb] = (
                    "THREAD " + str(thread_nb) + " - " + time.asctime(time.localtime(time.time())) + " :  " + string)
            THREAD_OUTPUT_LOCKER.release()

    def display_message(self, string):
        global MESSAGE
        global MESSAGE_LOCKER

        if MESSAGE_LOCKER.acquire(blocking=False):
            if len(MESSAGE) > self.nb_thread + 50 - 1 - self.fixed_message_nb:
                while len(MESSAGE) > 0:
                    MESSAGE.pop()

            MESSAGE.append(string)
            MESSAGE_LOCKER.release()
