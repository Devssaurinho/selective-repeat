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
        'The computer was born to solve problems that did not exist before. - Bill Gates']

    timeout = 1000  # send the next message if not response
    time_of_last_data = time.time()
    rdt = RDT.RDT('client', args.server, args.port)

    try:
        for msg in msgs:
            print('Client asking to change case: ' + msg)
            rdt.rdt_3_0_send(msg)

            # try to receive message before timeout
            msg = None
            while msg == None:
                msg = rdt.rdt_3_0_receive()
                if msg is None:
                    if time_of_last_data + timeout < time.time():
                        break
                    else:
                        continue
            time_of_last_data = time.time()

            # print the result
            if msg:
                print('Client: Received the converted frase to: ' + msg + '\n')
                
    except (KeyboardInterrupt, SystemExit):
        print("Ending connection...")

    except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
        print("Ending connection...")
        
    finally:
        rdt.disconnect()
        print("Connection ended.")
