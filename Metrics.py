import time
import matplotlib.pyplot as plt
import numpy as np
from RDT import Packet

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

        # List of timestamps for all packet sent for the first time (timestamp, packet)
        self.packets_first_sent = []

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

    def add_packet_first_sent(self, p):
        t = time.time_ns()
        self.packets_first_sent.append((t, p))

    def add_retransmission_sent(self, p):
        t = time.time_ns()
        self.retransmissions_sent.append((t, p))

    def add_corrupted_received(self):
        t = time.time_ns()
        self.corrupted_received.append(t)

    def plot_simulation_time(self):
        print(f"For {self.label}")
        print("Start time: " + format_time(self.start_time) )
        print("End time: " + format_time(self.end_time ) )
        print(f"Difference: {(self.end_time-self.start_time)/1000000000 } (s) \n")
    
    def plot_corrupted(self, isOrange=0):
        plt.figure(figsize=(12, 6))

        plt.title(f"Corrupted Packets in {self.label}")

        plt.xlabel("Time (us)")
        plt.ylabel("Corrupted Packets (unit)")

        x = []
        y = []
        for i, t in enumerate(self.corrupted_received):
            y.append(i+1)
            x.append((t - self.start_time)/1000)
        
        plt.plot(x, y, marker="o", color=("tab:orange" if isOrange else "tab:blue"))
        
        plt.grid(True)
        plt.tight_layout()

        plt.show()

    def plot_retransmissions(self, isOrange=0):
        plt.figure(figsize=(12, 6))

        plt.title(f"Retransmitted Packets in {self.label}")

        plt.xlabel("Time (us)")
        plt.ylabel("Retransmitted Packets (unit)")

        x = []
        y = []
        for i, (t, p) in enumerate(self.retransmissions_sent):
            y.append(i+1)
            x.append((t - self.start_time)/1000)
        
        plt.plot(x, y, marker="o", color=("tab:orange" if isOrange else "tab:blue"))
        
        plt.grid(True)
        plt.tight_layout()

        plt.show()
    
    def plot_sentPacket(self, isOrange=0):
        plt.figure(figsize=(12, 6))

        plt.title(f"All Transmitted Packets in {self.label}")

        plt.xlabel("Time (us)")
        plt.ylabel("Transmitted Packets (unit)")

        x = []
        y = []
        for i, (t, p) in enumerate(self.packets_sent):
            y.append(i+1)
            x.append((t - self.start_time)/1000)
        
        plt.plot(x, y, marker="o", color=("tab:orange" if isOrange else "tab:blue"))
        
        plt.grid(True)
        plt.tight_layout()

        plt.show()

    def plot_throughput(self, isOrange=0):
        plt.figure(figsize=(12, 6))

        plt.xlabel("Time (us)")
        plt.ylabel("Transmitted Data (Bytes)")

        x = []
        y = []

        acc = 0
        for t, p in self.packets_sent:
            n = len(p.packet)
            acc += n

            y.append(acc)
            x.append((t - self.start_time)/1000)
        
        plt.plot(x, y, marker="o", color=("tab:orange" if isOrange else "tab:blue"))
        
        throughput = acc * 1000000000 / (self.end_time - self.start_time)
        plt.title(f"Throughput in {self.label}: {throughput} (B/s)")

        plt.grid(True)
        plt.tight_layout()

        plt.show()

    def plot_goodput(self, isOrange=0):
        plt.figure(figsize=(12, 6))

        plt.xlabel("Time (us)")
        plt.ylabel("Transmitted Data (Bytes)")

        x = []
        y = []

        acc = 0
        for t, p in self.packets_first_sent:
            n = len(p.packet) - (Packet.size_len + Packet.seq_num_len + Packet.checksum_len + 1)
            acc += n

            y.append(acc)
            x.append((t - self.start_time)/1000)
        
        plt.plot(x, y, marker="o", color=("tab:orange" if isOrange else "tab:blue"))
        
        goodput = acc * 1000000000 / (self.end_time - self.start_time)
        plt.title(f"Goodput in {self.label}: {goodput} (B/s)")

        plt.grid(True)
        plt.tight_layout()

        plt.show()