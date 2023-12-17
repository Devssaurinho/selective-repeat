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
        while True:
            
            msg = rdt.rdt_4_0_receive()

            if (msg == None):

                # timeout event
                if (time_of_last_data + timeout < time.time()):
                    break

                continue

            # received a message
            time_of_last_data = time.time()
            reply = upperCase(msg)
            print(f'Server: converted{msg} to {reply}')
            rdt.rdt_4_0_send(reply)

    except (KeyboardInterrupt, SystemExit):
        print("Ending connection...")

    except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
        print("Ending connection...")
        
    finally:
        rdt.disconnect()
        print("Connection ended.")


