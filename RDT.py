import Network
import argparse
import time
from time import sleep
import hashlib

debug = True    
# default = False
total_package_length = 0
total_package_count = 0


def debug_log(message):
    if debug:
        print(message)


class Packet:
    # New field to indicate if the packet is an ACK
    ack_flag_length = 1
    # the number of bytes used to store the packet length
    seq_num_S_length = 10
    length_S_length = 10
    # length of md5 checksum in hex
    checksum_length = 32

    def __init__(self, seq_num, msg_S, ack_flag=False):
        global total_package_length
        global total_package_count
        self.seq_num = seq_num
        self.msg_S = msg_S
        self.ack_flag = ack_flag
        total_package_length += (
            len(msg_S)
            + Packet.seq_num_S_length
            + Packet.checksum_length
            + Packet.length_S_length
        )
        total_package_count +=1

    @classmethod
    def from_byte_S(cls, byte_S):
        # Extract the fields from the byte string
        seq_num_S = byte_S[cls.length_S_length: cls.length_S_length + cls.seq_num_S_length]
        ack_flag_S = byte_S[cls.length_S_length + cls.seq_num_S_length: cls.length_S_length + cls.seq_num_S_length + cls.ack_flag_length]
        msg_S = byte_S[cls.length_S_length + cls.seq_num_S_length + cls.ack_flag_length + cls.checksum_length:]
        print(msg_S)
        # Check for corruption before initializing the packet
        if cls.corrupt(byte_S):
            raise RuntimeError('Cannot initialize Packet: byte_S is corrupt')

        # Initialize the packet object
        return cls(int(seq_num_S), msg_S, bool(int(ack_flag_S)))

    def get_byte_S(self):
        # Convert sequence number to a byte field of seq_num_S_length bytes
        seq_num_S = str(self.seq_num).zfill(self.seq_num_S_length)
        # Determine the ACK flag value
        ack_flag_S = '1' if self.ack_flag else '0'
        # Convert length to a byte field of length_S_length bytes
        length_S = str(self.length_S_length + len(seq_num_S) + len(ack_flag_S) + self.checksum_length + len(self.msg_S)).zfill(self.length_S_length)
        # print(length_S)
        # Compute the checksum
        checksum = hashlib.md5((length_S + seq_num_S + ack_flag_S + self.msg_S).encode('utf-8'))
        checksum_S = checksum.hexdigest()
        # print(checksum_S)
        # Compile into a byte string
        return length_S + seq_num_S + ack_flag_S + checksum_S + self.msg_S

    @staticmethod
    def corrupt(byte_S):
        # Extract the fields from the byte string
        length_S = byte_S[0:Packet.length_S_length]
        seq_num_S = byte_S[Packet.length_S_length: Packet.length_S_length + Packet.seq_num_S_length]
        ack_flag_S = byte_S[Packet.length_S_length + Packet.seq_num_S_length: Packet.length_S_length + Packet.seq_num_S_length + Packet.ack_flag_length]
        checksum_S = byte_S[Packet.length_S_length + Packet.seq_num_S_length + Packet.ack_flag_length: Packet.length_S_length + Packet.seq_num_S_length + Packet.ack_flag_length + Packet.checksum_length]
        msg_S = byte_S[Packet.length_S_length + Packet.seq_num_S_length + Packet.ack_flag_length + Packet.checksum_length:]

        # Compute the checksum locally
        checksum = hashlib.md5((length_S + seq_num_S + ack_flag_S + msg_S).encode('utf-8'))
        computed_checksum_S = checksum.hexdigest()

        # and check if the same
        return checksum_S != computed_checksum_S

    def is_ack_pack(self):
        return self.ack_flag
    

class RDT:
    # latest sequence number used in a packet
    seq_num = 0
    # buffer of bytes read from network
    byte_buffer = ''
    timeout = 3
    window_size = 6 

    def __init__(self, role_S, server_S, port):
        self.network = Network.NetworkLayer(role_S, server_S, port)
        self.expected_seq_num = 0
        self.sent_packets = {} # to store sent packets
        self.sent_unacknowledged = {} # to store sent but unacknowledged packets

    def disconnect(self):
        self.network.disconnect()

    def rdt_4_0_send(self, msg_S):
        current_seq = self.seq_num

        while current_seq == self.seq_num:
            # Send packets up to the window size
            for i in range(self.window_size):
                if current_seq + i not in self.sent_unacknowledged:
                    p = Packet(current_seq + i, msg_S)
                    self.sent_unacknowledged[current_seq + i] = p
                    self.network.udt_send(p.get_byte_S())

            # Wait for acknowledgments
            for i in range(self.window_size):
                response = ''
                timer = time.time()

                while response == '' and timer + self.timeout > time.time():
                    response = self.network.udt_receive()

                if response == '':
                    continue

                debug_log("SENDER: " + response)

                msg_length = int(response[:Packet.length_S_length])
                self.byte_buffer = response[msg_length:]

                if not Packet.corrupt(response[:msg_length]):
                    response_p = Packet.from_byte_S(response[:msg_length])
                    if response_p.seq_num in self.sent_unacknowledged:
                        if response_p.msg_S == "1":
                            debug_log("SENDER: Received ACK for seq_num {}".format(response_p.seq_num))
                            del self.sent_unacknowledged[response_p.seq_num]
                        elif response_p.msg_S == "0":
                            debug_log("SENDER: NAK received for seq_num {}".format(response_p.seq_num))
                            # Optionally handle NAK by resending the packet
                else:
                    debug_log("SENDER: Corrupted ACK")
                    self.byte_buffer = ''

            # Continue with the next sequence number
            current_seq += self.window_size

    def rdt_4_0_receive(self):
        ret_S = None
        current_seq = self.seq_num

        while current_seq == self.seq_num:
            # Receive packets up to the window size
            for i in range(self.window_size):
                byte_S = self.network.udt_receive()
                self.byte_buffer += byte_S

                # Check if we have received enough bytes
                if len(self.byte_buffer) < Packet.length_S_length:
                    break  # Not enough bytes to read packet length

                # Extract the length of the packet
                length = int(self.byte_buffer[:Packet.length_S_length])
                print(length)

                # Check if there are enough bytes to read the whole packet
                if len(self.byte_buffer) < length:
                    break

                # Check if the packet is corrupt
                if Packet.corrupt(self.byte_buffer):
                    # Send a NAK
                    debug_log("RECEIVER: Corrupt packet, sending NAK.")
                    answer = Packet(self.seq_num, "0")
                    self.network.udt_send(answer.get_byte_S())
                else:
                    # Create a packet from buffer content
                    p = Packet.from_byte_S(self.byte_buffer[:length])

                    # Check if the packet is an ACK
                    if p.is_ack_pack():
                        self.byte_buffer = self.byte_buffer[length:]
                        continue

                    # Process the received packet
                    if p.seq_num < self.seq_num:
                        debug_log('RECEIVER: Already received packet.  ACK again.')
                        # Send another ACK
                        answer = Packet(p.seq_num, "1")
                        self.network.udt_send(answer.get_byte_S())
                    elif p.seq_num == self.seq_num:
                        debug_log('RECEIVER: Received new.  Send ACK and increment seq.')
                        # SEND ACK
                        answer = Packet(self.seq_num, "1")
                        self.network.udt_send(answer.get_byte_S())
                        debug_log("RECEIVER: Incrementing seq_num from {} to {}".format(self.seq_num, self.seq_num + 1))
                        self.seq_num += 1

                    # Add contents to the return string
                    ret_S = p.msg_S if (ret_S is None) else ret_S + p.msg_S

                # Remove the packet bytes from the buffer
                self.byte_buffer = self.byte_buffer[length:]

            # If this was the last packet, return on the next iteration
        return ret_S


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RDT implementation.')
    parser.add_argument('role', help='Role is either client or server.', choices=['client', 'server'])
    parser.add_argument('server', help='Server.')
    parser.add_argument('port', help='Port.', type=int)
    args = parser.parse_args()

    rdt = RDT(args.role, args.server, args.port)
    if args.role == 'client':
        rdt.rdt_4_0_send('MSG_FROM_CLIENT')
        sleep(2)
        print(rdt.rdt_4_0_receive())
        rdt.disconnect()


    else:
        sleep(1)
        print(rdt.rdt_4_0_receive())
        rdt.rdt_4_0_send('MSG_FROM_SERVER')
        rdt.disconnect()
        
