import argparse
import RDT
from Metrics import Metrics

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Quotation client talking to a Pig Latin server.')
    parser.add_argument('server', help='Server.')
    parser.add_argument('port', help='Port.', type=int)
    args = parser.parse_args()

    document = [
        'The art of debugging is figuring out what you really told your program to do rather than what you thought you told it to do. -- Andrew Singer', 
    	'The good news about computers is that they do what you tell them to do. The bad news is that they do what you tell them to do. -- Ted Nelson', 
    	'It is hardware that makes a machine fast. It is software that makes a fast machine slow. -- Craig Bruce',
        'The art of debugging is figuring out what you really told your program to do rather than what you thought you told it to do. -- Andrew Singer',
        'The computer was born to solve problems that did not exist before. - Bill Gates'
    ]

    rdt = RDT.RDT('client', args.server, args.port)
    transport = RDT.Transport()

    try:

        # Send all messages
        for text in document:

            metricsClientSender = Metrics("Client - Sender")
            metricsClientReceiver = Metrics("Client - Receiver")

            transport.send(rdt, text, metricsClientSender)
            reply = transport.receive(rdt, metricsClientReceiver)
            
            # print the result
            print("||||||||||||||||||||||||||||||||||||||||||||||||||")
            print(f'Client: Original Sentence: \n\t{text}')
            print(f'Client: Converted Sentence Received: \n\t{reply}')
            print("||||||||||||||||||||||||||||||||||||||||||||||||||\n")

        # Sender
        metricsClientSender.plot_simulation_time()
        # metricsClientSender.plot_corrupted()
        # metricsClientSender.plot_sentPacket()
        # metricsClientSender.plot_retransmissions()
        # metricsClientSender.plot_throughput()
        # metricsClientSender.plot_goodput()

        # Receiver
        metricsClientReceiver.plot_simulation_time()
        # metricsClientReceiver.plot_corrupted()
        # metricsClientReceiver.plot_sentPacket()
        # metricsClientReceiver.plot_retransmissions()
        # metricsClientReceiver.plot_throughput()
        # metricsClientReceiver.plot_goodput()

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