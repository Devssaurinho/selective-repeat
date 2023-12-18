import argparse
import RDT
import time
from Metrics import Metrics 

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Quotation client talking to a Pig Latin server.')
    parser.add_argument('server', help='Server.')
    parser.add_argument('port', help='Port.', type=int)
    args = parser.parse_args()

    msgs = [
    	'teste0',
        'teste1',
        'teste2',
        'teste3',
        'teste4',
        'teste5',
        'teste6',
        'teste7',
        'teste8',
        'teste9',
        'teste10',
        'teste11',
        'teste12',
        'teste13',
        'teste14',
        'teste15',
        'teste16',
        'teste17',
        'teste18',
        'teste19',
        'teste20'
        ]

    rdt = RDT.RDT('client', args.server, args.port)

    try:
        rdt.mark_start()
        # Send all messages
        rdt.rdt_4_0_send(msgs)
            
        # Receive all messages
        msgs = rdt.rdt_4_0_receive()

        # print the result
        for msg in msgs:
            print(f'Client: Received the converted frase {msg}')

        rdt.mark_end()  

        # Instantiate Metrics class with RDT times
        metrics = Metrics(start_time=rdt.get_start_time(), end_time=rdt.get_end_time(), label="Client")
        metrics.start_timer()
        time.sleep(0.1)
 
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