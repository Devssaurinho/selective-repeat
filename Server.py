import argparse
import RDT
import time


def upperCase(message):
    capitalizedSentence = message.upper()
    return capitalizedSentence


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='UPPER CASE server.')
    parser.add_argument('port', help='Port.', type=int)
    args = parser.parse_args()

    timeout = 1000
    time_of_last_data = time.time()

    rdt = RDT.RDT('server', None, args.port)

    try:
        msgs = rdt.rdt_4_0_receive()

        reply = [upperCase(msg) for msg in msgs]
        
        rdt.rdt_4_0_send(reply)

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