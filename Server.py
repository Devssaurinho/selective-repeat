import argparse
import RDT
import time
from Metrics import Metrics

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
        rdt.mark_start()

        msgs = rdt.rdt_4_0_receive()

        reply = [upperCase(msg) for msg in msgs]
        
        rdt.rdt_4_0_send(reply)
        
        rdt.mark_end()

        # Instantiate Metrics class with RDT times
        metrics = Metrics(start_time=rdt.get_start_time(), end_time=rdt.get_end_time(), label="Server")
        
        metrics.start_timer()
        time.sleep(0.1)
        # Use the packet sizes recorded in RDT
        for total_size, payload_size in rdt.packet_sizes:
            metrics.add_bytes_sent(total_size, payload_size)

        metrics.end_timer()
        metrics.plot_throughput_and_goodput()

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