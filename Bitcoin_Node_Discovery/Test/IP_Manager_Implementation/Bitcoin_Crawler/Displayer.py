import datetime
import time
import sys
import os
from threading import Lock, Thread, Event


def print_there(x, y, text):
    sys.stdout.write("\x1b7\x1b[%d;%df%s\x1b8" % (x + 1, y + 1, text))
    sys.stdout.flush()


class Displayer(Thread):

    def __init__(self, measurements_manager, nb_thread, network_to_crawl, display_prog):
        Thread.__init__(self)
        self.measurements_manager = measurements_manager
        self.nb_thread = nb_thread
        self.fixed_message_nb = 9
        self.network_to_crawl = network_to_crawl
        self.display_prog = display_prog
        self.start_time = None

        tmp = os.popen('stty size', 'r').read().split()
        (self.terminal_rows, self.terminal_column) = (int(tmp[0]), int(tmp[1]))

        self._thread_output = list()
        self._messages = list()

        self.__message_locker = Lock()
        self.__thread_output_locker = Lock()

        self.__stop_event = Event()
        self.__pause_event = Event()
        self.__error_event = Event()

        self.init_terminal()

    def run(self):
        self.start_time = self.measurements_manager.measurements.get_start_time()
        os.system('clear')

        if not self.display_prog:
            self.__pause_event.set()

        self.display_progression()

    def init_terminal(self):
        i = 0
        while i < self.nb_thread:
            self._thread_output.append(
                ("THREAD " + str(i) + " - " + time.asctime(time.localtime(time.time())) + " :  Initialization ..."))
            i = i + 1

    def display_progression(self):
        empty_line = ""

        i = 0
        while i < self.terminal_column - 1:
            empty_line = empty_line + " "
            i = i + 1

        while not self.__stop_event.isSet():
            tmp = os.popen('stty size', 'r').read().split()
            (self.terminal_rows, self.terminal_column) = (int(tmp[0]), int(tmp[1]))
            i = 0

            thread_output_length = len(self._thread_output)

            while i < thread_output_length:
                string = self._thread_output[i]

                nb_message_to_display = len(self._messages)
                message_to_display = list(self._messages)

                if (self.terminal_rows - 1 - self.fixed_message_nb - nb_message_to_display) <= 0:
                    os.system('clear')
                    print_there(0, 0, "Increase the Size of your Terminal")
                    break
                elif i % (self.terminal_rows - 1 - self.fixed_message_nb - nb_message_to_display) == 0 \
                        or i == thread_output_length:

                    nb_ipv4_to_read = self.measurements_manager.measurements.get_nb_to_read("ipv4")
                    nb_ipv6_to_read = self.measurements_manager.measurements.get_nb_to_read("ipv6")
                    nb_being_read = self.measurements_manager.measurements.get_nb_being_read()
                    nb_readed = self.measurements_manager.measurements.get_nb_readed()
                    nb_active = self.measurements_manager.measurements.get_nb_active_peers()
                    process_time_stat = self.measurements_manager.measurements.get_process_ip_stat_per_query_nb()

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
                        self.display_message("Measurements Storage Task Failed.")

                    j = 0
                    while j < nb_message_to_display:
                        print_there(self.fixed_message_nb + j, 0, empty_line)
                        print_there(self.fixed_message_nb + j, 0, message_to_display[j])
                        j = j + 1

                cursor = self.fixed_message_nb + nb_message_to_display + i % (
                        self.terminal_rows - 1 - self.fixed_message_nb - nb_message_to_display)

                print_there(cursor, 0, empty_line)
                print_there(cursor, 0, string)

                if (i + 1) % (self.terminal_rows - 1 - self.fixed_message_nb - nb_message_to_display) == 0 or (
                        i + 1) == thread_output_length:
                    if thread_output_length > self.terminal_rows - 1 - self.fixed_message_nb - nb_message_to_display:
                        time.sleep(5)

                i = i + 1

    def kill(self):
        self.__stop_event.set()
        os.system('clear')

    def join(self, **kwargs):
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
        if self.__thread_output_locker.acquire(blocking=False):
            self._thread_output[thread_nb] = (
                    "THREAD " + str(thread_nb) + " - " + time.asctime(time.localtime(time.time())) + " :  " + string)

            self.__thread_output_locker.release()

    def display_error_message(self, string):
        if not self.__error_event.is_set():
            self.__error_event.set()
            self.display_message(string)

    def display_message(self, string):
        if self.__message_locker.acquire(blocking=False):
            if len(self._messages) > self.nb_thread + 50 - 1 - self.fixed_message_nb:

                while len(self._messages) > 0:
                    self._messages.pop()

            self._messages.append(string)

            self.__message_locker.release()
