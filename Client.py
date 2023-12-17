import argparse
import RDT
import time

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Quotation client talking to a Pig Latin server.')
    parser.add_argument('server', help='Server.')
    parser.add_argument('port', help='Port.', type=int)
    args = parser.parse_args()

    msgs = [
    	'The art of debugging is figuring out what you really told your program to do rather than what you thought you told it to do. -- Andrew Singer', 
    	'The good news about computers is that they do what you tell them to do. The bad news is that they do what you tell them to do. -- Ted Nelson', 
    	'It is hardware that makes a machine fast. It is software that makes a fast machine slow. -- Craig Bruce',
        'The art of debugging is figuring out what you really told your program to do rather than what you thought you told it to do. -- Andrew Singer',
        'The computer was born to solve problems that did not exist before. - Bill Gates',
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
        ]

    rdt = RDT.RDT('client', args.server, args.port)

    try:
        # Send all messages
        for msg in msgs:
            print('Client asking to change case: \n\t' + msg)
            
            # rdt_send can refuse data, return False
            # so, until the msg was sent, it will be locked in a loop
            while(not rdt.rdt_4_0_send(msg)):
                pass
            

        # Receive all messages
        for i in range(len(msgs)):
            msg = None

            while msg == None:
                msg = rdt.rdt_4_0_receive()

            # print the result
            print('Client: Received the converted frase to: ' + msg + '\n')
                
    except (KeyboardInterrupt, SystemExit):
        print("Ending connection...")

    except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
        print("Ending connection...")
        
    finally:
        rdt.disconnect()
        print("Connection ended.")
