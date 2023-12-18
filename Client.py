import argparse
import RDT
from Metrics import Metrics

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Quotation client talking to a Pig Latin server.')
    parser.add_argument('server', help='Server.')
    parser.add_argument('port', help='Port.', type=int)
    parser.add_argument('messages', help='Number of Messages', type=int, default=11)
    args = parser.parse_args()

    msgs = [f'teste{i}' for i in range(args.messages)]

    rdt = RDT.RDT('client', args.server, args.port)

    metricsClientSender = Metrics("Client - Sender")
    metricsClientReceiver = Metrics("Client - Receiver")

    try:

        # Send all messages
        rdt.rdt_4_0_send(msgs, metricsClientSender)
            
        # Receive all messages
        msgs = rdt.rdt_4_0_receive(metricsClientReceiver)

        # print the result
        for msg in msgs:
            print(f'Client: Received the converted sentence {msg}')
        
        # Sender
        metricsClientSender.plot_simulation_time()
        metricsClientSender.plot_corrupted()
        metricsClientSender.plot_sentPacket()
        metricsClientSender.plot_retransmissions()
        metricsClientSender.plot_throughput()
        metricsClientSender.plot_goodput()

        # Receiver
        metricsClientReceiver.plot_simulation_time()
        metricsClientReceiver.plot_corrupted()
        metricsClientReceiver.plot_sentPacket()
        metricsClientReceiver.plot_retransmissions()
        metricsClientReceiver.plot_throughput()
        metricsClientReceiver.plot_goodput()

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