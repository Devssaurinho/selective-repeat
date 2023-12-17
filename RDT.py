import Network
import argparse
import time
from time import sleep
import hashlib

debug = True    
# default = False


def debug_log(message):
    if debug:
        print(message)


class Packet:
    # packet = [size, seq_num, checksum, data ]

    # the number of bytes(chars) used to store the size of the packet
    size_len = 8

    # the number of bytes(chars) used to store sequence number
    seq_num_len = 8
    
    # the number of bytes(chars) of md5 checksum in hex
    checksum_len = 32

    # Object Variables
    size = None
    size_str = None
    seq_num = None
    seq_num_str = None
    checksum = None
    msg = None
    packet = None

    # Receive packet format settings at initialization
    def __init__(self, size_len=8, seq_num_len=8, checksum_len=32):
        self.size_len = size_len
        self.seq_num_len = seq_num_len
        self.checksum_len = checksum_len


    def code(self, seq_num, msg):

        # create size (int and str)
        self.size = self.size_len + self.seq_num_len + self.checksum_len + len(msg)
        self.size_str = str(self.size).zfill(self.size_len)

        # create seq_num (int and str)
        self.seq_num = seq_num
        self.seq_num_str = str(seq_num).zfill(self.seq_num_len)

        # compute the checksum (str)
        self.checksum = hashlib.md5((self.size_str + self.seq_num_str + msg).encode('utf-8')).hexdigest()

        # save message (str)
        self.msg = msg

        # compile into a string
        self.packet = self.size_str + self.seq_num_str + self.checksum + self.msg

        return self.packet
    

    def split(self, packet):

        # split packet into respective variables
        limits = [self.size_len, self.size_len+self.seq_num_len, self.size_len+self.seq_num_len+self.checksum_len]
        
        size_str = packet[0 : limits[0]]
        seq_num_str = packet[limits[0] : limits[1]]
        checksum = packet[limits[1] : limits[2]]
        msg = packet[limits[2] : ]

        return size_str, seq_num_str, checksum, msg


    def corrupt(self, packet):

        # extract the fields
        size_str, seq_num_str, checksum, msg = self.split(packet)

        # compute the checksum locally
        computed = hashlib.md5(str(size_str + seq_num_str + msg).encode('utf-8')).hexdigest()

        # and check if they are the same
        return checksum != computed


    def decode(self, packet):

        if self.corrupt(packet):
            raise RuntimeError('Cannot extract packet: it is corrupted')

        # extract the fields
        size_str, seq_num_str, checksum, msg = self.split(packet)
        
        # save into object variables
        self.size = int(size_str)
        self.size_str = size_str

        self.seq_num = int(seq_num_str)
        self.seq_num_str = seq_num_str

        self.checksum = checksum

        self.msg = msg

        self.packet = packet

        # split packet into its components
        return size_str, seq_num_str, checksum, msg
    

    def get_ack(self):
        # when ACK is sent, it is formated as ACK.XX, XX = seq_num
        if "ACK" == self.msg:
            return self.seq_num
        
        return -1


# for the sender
class RDT:
    # parameters of the protocol
    window_len = 4
    modulo = 8
    timeout = 3
    
    def __init__(self, role_str, server_str, port):
        # self.network = Network.NetworkLayer(role_str, server_str, port)
        pass
    
    def disconnect(self):
        self.network.disconnect()

    def rdt_4_0_send(self, msgs):

        queue = list(msgs)
        # next sequence number [0 to 7] to be sent
        nxt = 0
        
        # sequence number of the last not acknowledge packet inside window
        base = 0

        # window = {idx : [wasACK?, packet, timer] }
        window = {}

        while(True):
            
            # stop condition: no more packet to send
            if (len(queue) == 0 and len(window) == 0):
                break

            # Data received from above and inside window boundary
            if (len(queue) > 0 and len(window) < self.window_len):

                # create packet, buffer it into window
                msg = queue.pop(0)
                p = Packet()
                p.code(nxt, msg)
                window[nxt] = [False, p, time.time()]
                nxt = (nxt + 1) % self.modulo

                # send it!
                # self.network.udt_send(p.packet)
                print(p.packet)

            # Check for timeouts
            for seq in window.keys():
                wasAck, p, timer = window[seq]

                if (not wasAck) and (timer + self.timeout < time.time()):
                    # resend packet and update timer
                    window[seq][2] = time.time()
                    # self.network.udt_send(p.packet)
                    print(p.packet)

            # Check for received ack packet
            received = None
            wait_time = time.time()
            while (received == None and (time.time() < (wait_time + self.timeout))):
                # received = self.network.udt_receive()
                received = input()
                if ("ACK" in received):
                    num = received[3]
                    p = Packet()
                    p.code(num, "ACK")
                    received = p.packet

            if (received != None):
                p = Packet()
                if (not p.corrupt(received)):
                    p.decode(received)
                    ack_num = p.get_ack()
                    if (ack_num != -1 and ack_num in window):
                        window[ack_num][0] = True

                        if (ack_num == base):
                            idx = base
                            while(idx in window and window[idx][0]):
                                window.pop(idx)
                                idx = (idx + 1) % self.modulo
                            base = idx

    def rdt_4_0_receive(self):
        pass

if __name__ == '__main__':
    msgs = [
        'teste1',
        'teste2',
        'teste3',
        ]

    rdt = RDT('Client', 'localhost', 5000)
    rdt.rdt_4_0_send(msgs)
        
