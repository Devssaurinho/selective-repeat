import time
import matplotlib.pyplot as plt
import numpy as np

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
        if (self.start_time == None):
            self.start_time = time.time()

    def set_end(self):
        if (self.end_time == None):
            self.end_time = time.time()

    def add_packet_sent(self, p):
        t = time.time()
        self.packets_sent.append((t, p))

    def add_retransmission_sent(self, p):
        t = time.time()
        self.retransmissions_sent.append((t, p))

    def add_corrupted_received(self):
        t = time.time()
        self.corrupted_received.append(t)
