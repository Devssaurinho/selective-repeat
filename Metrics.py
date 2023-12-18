import time
import matplotlib.pyplot as plt
import numpy as np

def format_time(val):
    f_time = time.strftime("%d-%m-%Y %H:%M:%S", time.gmtime(val/1000000000 - 3*60*60))
    us = (val//1000) % 1000000
    f_time += f".{us:3d} us" #microsseconds
    return f_time

class Metrics:
    def __init__(self, label=""):
        self.label = label # se é Client ou Servidor, "Sender / Receiver"

        self.start_time = None
        self.end_time = None

        # List of timestamps for all packet sent (timestamp, packet)
        self.packets_sent = []

        # List of timestamps for all packet resent (timestamp, packet)
        self.retransmissions_sent = []

        # List of timestamps for all received corrupted packets (timestamp)
        self.corrupted_received = []


    def set_start(self):
        # set at first call
        if (self.start_time == None):
            self.start_time = time.time_ns()

    def set_end(self):
        # override after several calls
        self.end_time = time.time_ns()

    def add_packet_sent(self, p):
        t = time.time_ns()
        self.packets_sent.append((t, p))

    def add_retransmission_sent(self, p):
        t = time.time_ns()
        self.retransmissions_sent.append((t, p))

    def add_corrupted_received(self):
        t = time.time_ns()
        self.corrupted_received.append(t)

    def plot_simulation_time(self):
        print("Start time: " + format_time(self.start_time) )
        print("End time: " + format_time(self.end_time ) )
        print(f"Difference: {(self.end_time-self.start_time)/1000000000 } (s) \n")
    
    def plot_corrupted(self):
        plt.figure(figsize=(12, 6))

        plt.title(f"Total de Pacotes Corrompidos")

        plt.xlabel("Tempo (us)")
        plt.ylabel("Corrupted Packets (unit)")

        corrupted = [(t/1000, i+1) for (i, t) in enumerate(self.corrupted_received)]
        print(corrupted)
        
        plt.plot(corrupted, marker="o", color="blue")
        
        plt.grid(True)
        plt.tight_layout()
        plt.show()