from threading import Thread
import os
import subprocess

class Monitor(Thread):
    def __init__(self,options, node_ip, displayer):
        Thread.__init__(self)
        self.options = options
        self.node_ip = node_ip
        self.displayer = displayer

    def run(self):
        self.tshark_monitoring(self.options, self.node_ip)

    def create_node_measurements_folder(self, node_ip):
        directory = "Measurements/tshark_" + node_ip + "/"
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            raise OSError("Error: Failed to create directory: ", directory)


    def tshark_monitoring(self,options, node_ip):
        tsharkCall = ["tshark","-i", "any", "-Q","-a","duration:3000"]

        for i in options:
            tsharkCall.append("-f")
            tsharkCall.append(i)

        self.create_node_measurements_folder(node_ip)

        #tshark_storage = ["-w",("Measurements/tshark_" + node_ip + "/tshark_" + node_ip + ".pcap"),"-T","json"]
        tshark_storage = ["-w",("Measurements/tshark_" + node_ip + "/tshark_" + node_ip + ".pcap")]
        tsharkCall = tsharkCall + tshark_storage

        self.stdouts = open(("Measurements/tshark_" + node_ip + "/tshark_" + node_ip + "_tshark_error.txt"), "w+")
        #stdout.write(output.decode("utf-8") )
        #self.process = subprocess.Popen(tsharkCall, stdout=self.stdouts, stderr=subprocess.DEVNULL)
        self.process = subprocess.Popen(tsharkCall, stdout=subprocess.DEVNULL, stderr=self.stdouts)

    def has_error(self):
        if os.stat(self.stdouts.name).st_size == 0:
            return False
        else:
            return True

    def join(self):
        #if hasattr(self, 'process'):
        self.process.terminate()
        self.process.kill()
        #if hasattr(self, 'stdouts'):
        name = self.stdouts.name
        self.stdouts.close()

        if not self.has_error():
            os.remove(name)
