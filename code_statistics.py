def throughput(size_packets: float, time_to_transfer: float):
    print(size_packets)
    print(time_to_transfer)
    throughput = size_packets / time_to_transfer
    print(f"throughput: {throughput}")


def goodput():
    print("goodput")


def total_transmitted_packets():
    print("ttp")


def total_retransmissions():
    print("Total Retransmissions")


def total_corrupted_packets():
    print("Total Corrupted Packets:")


def simulation_time():
    print("Simulation Time")
