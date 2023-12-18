import Network
import time
import hashlib

debug = True    
# default = False


def debug_log(message):
    if debug:
        print(message)

def format_time(val):
    f_time = time.strftime("%d-%m-%Y %H:%M:%S", time.gmtime(val/1000000000 - 3*60*60))
    us = (val//1000) % 1000000
    f_time += f".{us:3d} us" #microsseconds
    return f_time

class Packet:
    # packet = [size, seq_num, ackFlag, checksum, data]

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
    ack = None
    ack_str = None
    checksum = None
    msg = None
    packet = None

    # Receive packet format settings at initialization
    def __init__(self, size_len=8, seq_num_len=8, checksum_len=32):
        self.size_len = size_len
        self.seq_num_len = seq_num_len
        self.checksum_len = checksum_len

    # create packet from augments
    def code(self, seq_num, msg, is_ack=0):

        # create size (int and str)
        self.size = self.size_len + self.seq_num_len + self.checksum_len + 1 + len(msg)
        self.size_str = str(self.size).zfill(self.size_len)

        # create seq_num (int and str)
        self.seq_num = seq_num
        self.seq_num_str = str(seq_num).zfill(self.seq_num_len)

        # save ack (0 or 1 bool)
        self.ack = is_ack
        self.ack_str = str(self.ack)

        # compute the checksum (str)
        self.checksum = hashlib.md5((self.size_str + self.seq_num_str + self.ack_str + msg).encode('utf-8')).hexdigest()

        # save message (str)
        self.msg = msg

        # compile into a string
        self.packet = self.size_str + self.seq_num_str + self.ack_str + self.checksum + self.msg

        return self.packet
    

    def split(self, packet):

        # split packet into respective variables
        limits = [self.size_len, 
                  self.size_len + self.seq_num_len, 
                  self.size_len + self.seq_num_len + 1, 
                  self.size_len + self.seq_num_len + 1 + self.checksum_len]
        
        size_str = packet[0 : limits[0]]
        seq_num_str = packet[limits[0] : limits[1]]
        ack_str = packet[limits[1] : limits[2]]
        checksum = packet[limits[2] : limits[3]]
        msg = packet[limits[3] : ]

        return size_str, seq_num_str, ack_str, checksum, msg


    def corrupt(self, packet):

        # extract the fields
        size_str, seq_num_str, ack_str, checksum, msg = self.split(packet)
 
        # compute the checksum locally
        computed = hashlib.md5(str(size_str + seq_num_str + ack_str + msg).encode('utf-8')).hexdigest()

        # and check if they are the same
        return checksum != computed


    def decode(self, packet):

        if self.corrupt(packet):
            raise RuntimeError('Cannot extract packet: it is corrupted')

        # extract the fields
        size_str, seq_num_str, ack_str, checksum, msg = self.split(packet)
        
        # save into object variables
        self.size = int(size_str)
        self.size_str = size_str

        self.seq_num = int(seq_num_str)
        self.seq_num_str = seq_num_str

        self.ack_str = ack_str
        self.ack = int(ack_str)

        self.checksum = checksum
        
        self.msg = msg

        self.packet = packet

        # split packet into its components
        return size_str, seq_num_str, ack_str, checksum, msg
    

    def get_ack(self):
        if self.ack:
            return self.seq_num
        
        return -1


class RDT:
    # parameters of the protocol
    window_len = 4
    modulo = window_len*2

    # packet timeout, maybe 3s is better, but system is already very fast
    timeout = 2

    # connection timeout:
    # if, for 5 seconds duration, receiver doesn't receive any packets, terminate connection
    connection_timeout = 10 
    
    def __init__(self, role_str, server_str, port):
        self.network = Network.NetworkLayer(role_str, server_str, port)
    
    def disconnect(self):
        self.network.disconnect()

    def rdt_4_0_send(self, msgs, metrics):

        queue = list(msgs)

        # next sequence number [0 to 7] to be sent
        nxt = 0
        
        # sequence number of the last not acknowledge packet inside window
        base = 0

        # window = {idx : [wasACK?, packet, timer] }
        window = {}

        debug_log("--------------------------------------------------")
        debug_log(f"Started sending packets at {format_time(time.time_ns())}")
        debug_log("--------------------------------------------------\n")

        while(True):
            
            # stop condition: no more packets to send
            if (len(queue) == 0 and len(window) == 0):

                # sleep for {connection_timeout} seconds to sync with receiver, so receiver can timeout
                time.sleep(self.connection_timeout)

                debug_log("##################################################")
                debug_log(f"Sent all packets, terminating at {format_time(time.time_ns())}")
                debug_log("##################################################\n")
                break

            # Data received from above and inside window boundary
            if ((len(queue) > 0) and (len(window) < self.window_len)):
                
                # create a packet, buffer it into window
                msg = queue.pop(0)
                p = Packet()
                p.code(nxt, msg, 0)
                window[nxt] = [False, p, time.time()]
                debug_log(f"First time: Sending packet {nxt}, at {format_time(time.time_ns())}" + f"\n\t {p.packet}\n")
                nxt = (nxt + 1) % self.modulo

                # send it!
                self.network.udt_send(p.packet)
                # add packet sent
                metrics.add_packet_sent(p)
                # add packet sent for the first time
                metrics.add_packet_first_sent(p)
                # if initialized, override end time for the last packet sent 
                metrics.set_end()
                # if not initialized, set start time for the first packet sent 
                metrics.set_start()

            # Check for timeouts
            for seq in window.keys():
                wasAck, p, timer = window[seq]

                if (not wasAck) and (timer + self.timeout < time.time()):
                    # resend packet and update timer
                    debug_log(f"Timeout: Resend packet {seq}, at {format_time(time.time_ns())}" + f"\n\t {p.packet}\n")
                    window[seq][2] = time.time()
                    self.network.udt_send(p.packet)
                    # add packet sent
                    metrics.add_packet_sent(p)
                    # add retransmission sent
                    metrics.add_retransmission_sent(p)
                    # if initialized, override end time for the last packet sent 
                    metrics.set_end()

            # Check for received ACK packet
            received = None
            start_timer = time.time()
            # try to read an packet from network for {self.timeout}/2 seconds
            while (received == None and (time.time() < (start_timer + self.timeout/2))):
                received = self.network.udt_receive()

            if (received):
                
                # buffer content read from network, it can contain more than 1 packet
                buffer = received
                
                while (len(buffer) >= Packet.size_len):

                    # length attribute may be corrupted
                    try:
                        length = int(buffer[0:Packet.size_len])
                    except:
                        debug_log(f"Received: CORRUPTED packet, at {format_time(time.time_ns())}" + f"\n\t {received}\n")
                        # add corrupted received
                        metrics.add_corrupted_received()
                        continue

                    if (len(buffer) >= length):

                        # extract first packet, leave the rest at the buffer
                        received = buffer[0:length]
                        buffer = buffer[length:]

                        p = Packet()
                        if (not p.corrupt(received)):
                            p.decode(received)
                            ack_num = p.get_ack()
                            debug_log(f"Received ACK: Reading non corrupted ACK {ack_num}, at {format_time(time.time_ns())}" + f"\n\t {p.packet}\n")
                            if (ack_num != -1 and ack_num in window):
                                window[ack_num][0] = True

                                # slide window
                                if (ack_num == base):
                                    idx = base
                                    while(idx in window and window[idx][0]):
                                        window.pop(idx)
                                        idx = (idx + 1) % self.modulo
                                    base = idx
                        else:
                            debug_log(f"Received: CORRUPTED packet, at {format_time(time.time_ns())}" + f"\n\t {received}\n")
                            # add corrupted received
                            metrics.add_corrupted_received()
                    else:
                        break

    def rdt_4_0_receive(self, metrics):

        # buffer that will be sent to the next layer
        msgs = []
        
        # sequence number of the last not acknowledge packet inside window
        base = 0

        # list of indexes in the range = [base-N, base-1] (arithmetic modular)
        # because the modulo chosen is twice the window's length, behind_window will be complementar to window
        behind = {4, 5, 6, 7}
        window_range = {0, 1, 2, 3}

        # window = {idx : packet}
        # window only supports idx in the range [base, base+N-1]
        window = {}

        last_timer = time.time()

        debug_log("--------------------------------------------------")
        debug_log(f"Started receiving packets at {format_time(time.time_ns())}")
        debug_log("--------------------------------------------------\n")

        while(True):

            # stop condition: no packets received for at least {connection_timeout} => timeout
            if (last_timer + self.connection_timeout < time.time()):
                debug_log("##################################################")
                debug_log(f"Time limit: Stopped receiving packets at {format_time(time.time_ns())}")
                debug_log("##################################################\n")
                break
            
            # check for received packet
            received = None
            start_timer = time.time()
            # try to read an packet from network for {self.timeout}/2 seconds
            while (received == None and (time.time() < (start_timer + self.timeout/2))):
                received = self.network.udt_receive()

            if (received):
                
                # received a packet, update last time 
                last_timer = time.time()

                # buffer content read from network, it can contain more than 1 packet
                buffer = received
                
                while (len(buffer) >= Packet.size_len):

                    # length attribute may be corrupted
                    try:
                        length = int(buffer[0:Packet.size_len])
                    except:
                        debug_log(f"Received: CORRUPTED packet, at {format_time(time.time_ns())}" + f"\n\t {received}\n")
                        # add corrupted received
                        metrics.add_corrupted_received()
                        continue

                    if (len(buffer) >= length):

                        # extract first packet, leave the rest at the buffer
                        received = buffer[0:length]
                        buffer = buffer[length:]
                                
                        p = Packet()
                        if (not p.corrupt(received)):
                            p.decode(received)
                            num = p.seq_num
                            debug_log(f"Received: Reading non corrupted packet {num}, at {format_time(time.time_ns())}" + f"\n\t {p.packet}\n")

                            # already received packet, but sender might be behind
                            # just send ack, don't buffer it
                            if num in behind:
                                a = Packet()
                                a.code(num, "", 1)
                                debug_log(f"Sending ACK: for packet {num}, at {format_time(time.time_ns())}" + f"\n\t {a.packet}\n")
                                self.network.udt_send(a.packet)
                                # if initialized, override end time for the last packet sent 
                                metrics.set_end()
                                # if not initialized, set start time for the first packet sent 
                                metrics.set_start()
                                # add packet sent (ack)
                                metrics.add_packet_sent(a)

                            # packed inside window range
                            # send ack and buffer it
                            elif num in window_range:
                                a = Packet()
                                a.code(num, "", 1)
                                debug_log(f"Sending ACK: for packet {num}, at {format_time(time.time_ns())}" + f"\n\t {a.packet}\n")
                                self.network.udt_send(a.packet)
                                # if initialized, override end time for the last packet sent 
                                metrics.set_end()
                                # if not initialized, set start time for the first packet sent 
                                metrics.set_start()
                                # add packet sent (ack)
                                metrics.add_packet_sent(a)

                                # buffer packet
                                window[num] = p

                                # slide window
                                if (num == base):
                                    idx = base
                                    while(idx in window):

                                        if (window[idx].msg != "FIN"):
                                            msgs.append(window[idx].msg)
                                        window.pop(idx)

                                        # update ranges
                                        behind.remove((idx-self.window_len+self.modulo) % self.modulo)
                                        behind.add(idx)
                                        window_range.remove(idx)
                                        window_range.add((idx+self.window_len) % self.modulo)

                                        idx = (idx + 1) % self.modulo

                                    base = idx

                        else:
                            debug_log(f"Received: CORRUPTED packet, at {format_time(time.time_ns())}" + f"\n\t {received}\n")
                            # add corrupted received
                            metrics.add_corrupted_received()
        return msgs