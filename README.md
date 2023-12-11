# Selective Repeat 
Implementation of the rdt4.0 protocol. The primary enhancement is the incorporation of the selective repeat mechanism, allowing for the seamless flow of multiple packets between a client and a server.

## Project Details

### Objective

The main objective of this project is to work within a layered network architecture, implementing functions to optimize link utilization using pipelining techniques.

### Implemented Functionalities

- **rdt4.0 Protocol:** Extension/modification of the initial stop-and-wait code to support the transmission of multiple packets between the client and server.

- **Selective Repeat:** Implementation of the more advanced version of the protocol, introducing selective repeat mechanisms for sliding window operation.

### Provided Statistics

Upon execution/simulation, the code provides the following statistics:

- **Throughput (Network Layer):** Measurement of the transfer rate, considering packet headers.

- **Goodput (Application Layer Throughput):** Actual transfer rate excluding headers.

- **Total Transmitted Packets:** The overall count of packets sent during the simulation.

- **Total Retransmissions:** The count of packets retransmitted for each packet type.

- **Total Corrupted Packets:** The count of packets identified as corrupted for each packet type.

- **Simulation Time:** Elapsed time from the start of transmission to the last packet sent.

## Code Usage

The code is designed to allow the transmission of multiple messages between the client and server. The number of messages can be configured as a command-line argument for the client.

```bash
python server.py 5000
```
```bash
python client.py localhost 5000
```
---
