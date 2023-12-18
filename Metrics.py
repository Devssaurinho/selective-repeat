import time
import matplotlib.pyplot as plt
import RDT
import numpy as np

class Metrics:
    def __init__(self, start_time=None, end_time=None, label=""):
        self.label = label 
        self.start_time = start_time
        self.end_time = end_time
        self.time_points = []  # List to store time points
        self.total_bytes_sent = 0 # Initializing total_bytes_sent
        self.total_payload_bytes = 0  # Initializing total_payload_bytes
        self.network_throughput_values = []  # List to store throughput values
        self.application_throughput_values = []  # List to store goodput values

    def start_timer(self):
        self.start_time = time.time()

    def end_timer(self):
        self.end_time = time.time()

    def add_bytes_sent(self, size, payload_size=0):
        self.total_bytes_sent += size
        self.total_payload_bytes += payload_size
        if self.start_time is None:
            self.start_time = time.time()  # Fallback if not set by RDT
        current_time = time.time() - self.start_time
        if self.start_time is not None:
            current_time = time.time() - self.start_time
            self.time_points.append(current_time)
            self.network_throughput_values.append(self.total_bytes_sent / current_time)
            self.application_throughput_values.append(self.total_payload_bytes / current_time)

    def plot_throughput_and_goodput(self): 
        cumulative_bytes = np.cumsum(self.network_throughput_values)  # Cumulative sum of bytes
        cumulative_payload_bytes = np.cumsum(self.application_throughput_values)  # Cumulative sum of payload bytes

        plt.figure(figsize=(12, 6))

        # Graph for Throughput at the network layer
        plt.subplot(1, 2, 1)
        plt.plot(self.time_points, cumulative_bytes, marker='o', color='blue')
        plt.xlabel('Tempo (s)')
        plt.ylabel('Throughput (bytes)')
        plt.title(f'Throughput na Camada de Rede de {self.label}')
        plt.grid(True)

        # Graph for Goodput in the application layer
        plt.subplot(1, 2, 2)
        plt.plot(self.time_points, cumulative_payload_bytes, marker='o', color='green')
        plt.xlabel('Tempo (s)')
        plt.ylabel('Goodput (bytes)')
        plt.title(f'Goodput na Camada de Aplicação de {self.label}')
        plt.grid(True)

        plt.tight_layout()
        plt.show()

    def add_retransmission(self):
        self.total_retransmissions += 1

    def add_corrupted_packet(self):
        self.total_corrupted_packets += 1

    def get_total_packets_transmitted(self):
        # Return the total packets transmitted
        pass

    def get_total_retransmissions(self):
        return self.total_retransmissions

    def get_total_corrupted_packets(self):
        return self.total_corrupted_packets

    def get_simulation_time(self):
        return self.end_time - self.start_time if self.end_time and self.start_time else 0

