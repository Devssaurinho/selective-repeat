import argparse
import RDT
from Metrics import Metrics

def upperCase(message):
    capitalizedSentence = message.upper()
    return capitalizedSentence


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='UPPER CASE server.')
    parser.add_argument('port', help='Port.', type=int)
    args = parser.parse_args()

    rdt = RDT.RDT('server', None, args.port)

    metricsServerSender = Metrics("Server - Sender")
    metricsServerReceiver = Metrics("Server - Receiver")

    try:
        msgs = rdt.rdt_4_0_receive(metricsServerReceiver)

        reply = [upperCase(msg) for msg in msgs]
        
        rdt.rdt_4_0_send(reply, metricsServerSender)

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