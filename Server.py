import argparse
import RDT
from Metrics import Metrics
import time

def upperCase(message):
    capitalizedSentence = message.upper()
    return capitalizedSentence


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='UPPER CASE server.')
    parser.add_argument('port', help='Port.', type=int)
    args = parser.parse_args()

    rdt = RDT.RDT('server', None, args.port)
    transport = RDT.Transport()

    last_received_time = time.time()
    timeout_limit = 30

    try:

        while(True):
            
            if (last_received_time + timeout_limit < time.time()):
                break

            metricsServerSender = Metrics("Server - Sender")
            metricsServerReceiver = Metrics("Server - Receiver")

            text = transport.receive(rdt, metricsServerReceiver)

            if (text):

                last_received_time = time.time()

                reply = upperCase(text)
                transport.send(rdt, reply, metricsServerSender)

                print("||||||||||||||||||||||||||||||||||||||||||||||||||")
                print(f'Server: Original Sentence: \n\t{text}')
                print(f'Server: Converted Sentence Received: \n\t{reply}')
                print("||||||||||||||||||||||||||||||||||||||||||||||||||\n")

                # Receiver
                metricsServerReceiver.plot_simulation_time()
                # metricsServerReceiver.plot_corrupted(1)
                # metricsServerReceiver.plot_sentPacket(1)
                # metricsServerReceiver.plot_retransmissions(1)
                # metricsServerReceiver.plot_throughput(1)
                # metricsServerReceiver.plot_goodput(1)

                # Sender
                metricsServerSender.plot_simulation_time()
                # metricsServerSender.plot_corrupted(1)
                # metricsServerSender.plot_sentPacket(1)
                # metricsServerSender.plot_retransmissions(1)
                # metricsServerSender.plot_throughput(1)
                # metricsServerSender.plot_goodput(1)

    except (KeyboardInterrupt, SystemExit):
        rdt.disconnect()
        print("Ending connection...")

    except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
        rdt.disconnect()
        print("Ending connection...")
        
    finally:
        rdt.disconnect()
        print("Connection ended.")

    # close socket
    del rdt