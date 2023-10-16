# PINGClient.py for CMSC 440 Programming Assignment 
#   by Jordan Dube, 11/16/2022

# imports, no outside libraries
from socket import *
import sys
import time
import signal


# signal handler method. Prints exit message and exits program gracefully
#       signal: signal to catch (in this case ctrl+c (SIGINT)) 
#       frame:  the current stack frame (not needed)
def signal_handler(signal, frame):
    print('\nCtrl+C detected. Thanks for playing :)')
    exit()
    sys.exit(0)


# utility method to print the contents of a packet
#       div_line_1: string denoting first dividing line
#       div_line_2: string denoting second dividing line
#       packet:     the packet to be printed
def print_packet(div_line_1, div_line_2, packet):

    # split the packet up by lines
    lines = packet.splitlines()

    # format the packet by lines: first 4 are in the header and last 3 are the payload. Also add separating '-' characters
    lines_to_print = [div_line_1] + lines[0:4] + [div_line_2] + lines[4:] + [f"{'-'*39}\n"]

    # the second line is encoded as a 1, but it gets changed here for display
    lines_to_print[1] = f"Version: 1.0"

    # prints the lines in an appealing manner
    for line in lines_to_print:
        print(line)


# utility function to make the header portion of a packet
#       seq_no:         sequence number of the packet being created
#       packet_payload: payload portion of the packet being created, used in calculating the size field
def make_packet_header(seq_no, packet_payload):

    # return a string representing the fields of the header
    return f"Version: 1\nSequence No.: {seq_no}\nTimestamp: {time.time()}\nPayload Size: {len(packet_payload.encode())}"


# utility method to create the payload portion of a packet
#       client_hostname:   IP address of the packet's source
def make_packet_payload(client_hostname):

    # return a string representing the fields of the payload
    return f'Host: {client_hostname}\nClass-name: VCU-CMSC440-FALL-2022\nUser-name: Dube, Jordan'


# utility method to make a reply packet
#       client_hostname:   IP address of the packet's source
#       seq_no:            sequence number of the packet being created
def make_packet(client_hostname, seq_no):

    # make the header for the packet from the provided hostname
    packet_payload = make_packet_payload(client_hostname)

    # make the payload for the packet from the provided sequence number and the packet_payload made above
    packet_header = make_packet_header(seq_no, packet_payload)

    # return a string combining the packet header and packet payload
    return f"{packet_header}\n{packet_payload}"


# wrapper function to handle sending a packet
#       packet:             packet made by the make_packet method. Object to be sent to the server
#       clientSocket:       UDP socket created by the client
#       server_hostname:    hostname of packet's destination
#       port:               port of packet's destination
def send(clientSocket, packet, server_hostname, port):
    
    # try to send the packet
    try:

        # send the packet encoded in utf-8 format (bytes) to the provided server address, quit if an exception occurs
        clientSocket.sendto(packet.encode(), (server_hostname, port))

    # if a packet cannot be sent to the server, then tell the user that it is not a valid address
    except Exception as e:

        print(f'EXCEPTION: not a valid destination: (address: {server_hostname}, port: {port})')
        sys.exit(0)


# wrapper function to handle receiving a packet
#       clientSocket: UDP socket created by the client
def receive(clientSocket, num_losses, RTTs):

    # set the timeout interval of the socket to 1 second
    clientSocket.settimeout(1)

    # try to receive from the server
    try:
        
        # try to receive from the server
        try:
            # try to receive a packet
            try:

                # If it does receive, captures the source of the packet as well as the packet
                received_packet, serverAddress = clientSocket.recvfrom(2048)

            except KeyboardInterrupt:
                
                # only handle ctrl+C, explicitly raises a Keyboard Interrupt exception which gets handled by the signal_handle method
                raise KeyboardInterrupt

            # store the arrival time of the reply
            end_time = time.time()

            # once a reply is received, decode it and print it 
            received_packet = received_packet.decode()
            print_packet('----------- Received Ping Reply Header ----------', '---------- Received Ping Reply Payload -------------', received_packet)

            # retrieve the start time of the current packet and calculate and print the RTT for the sent packet
            received_lines = received_packet.splitlines()
            start_time = float(received_lines[2].split(' ')[-1])
            RTT = end_time - start_time
            print(f'RTT = {RTT}')

            # add the RTT to the list
            RTTs.append(RTT)

        # if the socket doesnt receive a reply after sending the packet within 1 second, the socket raises a timeout exception
        except timeout:

            # increment the loss counter
            num_losses += 1
            print(f'\n{"-"*15} Ping Reply Timed out {"-"*18}\n')
            pass

        return num_losses, RTTs

    # if an exception other than a timeout is raised, exit
    except Exception as e:
        print(f'ERR - connection closed by Server.')
        sys.exit(0)

# utility function to return average (arithmetic mean) of a list of numbers
#       list_of_nums: list of integers or floats that are added and then divided by the lists length to return an average
def avg(list_of_nums):
    return float(sum(list_of_nums))/len(list_of_nums)

# utility method to check the validity of the provided arguments
#       args: list of user-provided arguments to be used by the client (does not include "python*" or "PINGServer.py")
def check_args(args):

    # if there is more or less than 2 arguments, inform user regarding usage and return 0, 0 
    if len(args) != 2:
        print("Usage: python PINGServer.py hostname port")
        return 0, 0

    # try to get the hostname of the server based on user input
    try:

        server_hostname = args[0]

        # get the IPv4 of the server. If it is invalid, then an exception is raised
        ip = gethostbyname(server_hostname)

    # if the hostname is invalid, print the error and set hostname = 0
    except:
        print(f'ERR - arg 1')
        server_hostname = 0

    # try to get the port number based on user input
    try:

        # parse the port argument as an integer
        port = int(args[1])

        # check if the number is valid with regard to the value. If not, raise an Exception to trigger the except: block
        if port >= 65536 or port <= 0:
            raise Exception

    # if an exception is raised, inform the user to enter a valid port number and set port to 0
    except:
        print(f'ERR - arg 2')
        port = 0

    # return a tuple of hostname, port
    return server_hostname, port


# main driver method
def main():

    # omit "PINGClient.py" from the list of system arguments
    args = sys.argv[1:]

    # check the arguments and store returned tuple
    server_hostname, port = check_args(args)

    # if 1 or more of the arguments is invaild, hostname or port will be 0, so exit
    if server_hostname == 0 or port == 0:
        sys.exit(0)

    # try to make a socket
    try:

        # Create client socket
        clientSocket = socket(AF_INET, SOCK_DGRAM)
        clientSocket.connect((server_hostname, port))

        # get the hostname of the client
        client_hostname = gethostname()

        # set the client socket to nonblocking. This is because when in blocking mode, the user cannot exit the program with a keyboard interruption
        clientSocket.setblocking(0)

        # set signal check, only needs to be set once
        signal.signal(signal.SIGINT, signal_handler)

    # if exception is raised, inform user that the socket could not be created and exit
    except Exception as e:
        print(f"ERR - cannot connect PINGClient socket to port number {port}")
        sys.exit(0)

    # set sequence number to 1, initialize the RTT list and the number of losses
    seq_no = 1
    num_losses = 0
    RTTs = list()

    # send 10 packets starting at sequence number 1 up to 10
    while(seq_no <= 10):

        # try to send and receive the packets/replies
        try:
            
            # make a packet with the user-provided hostname and the current value of sequence number
            packet_to_send = make_packet(client_hostname, seq_no)

            # print the initial ping packet before sending it
            print_packet(f'---------- Ping Packet Header ----------', f'--------- Ping Packet Payload ------------', packet_to_send)

            # use the send method to send the packet to the server
            send(clientSocket, packet_to_send, server_hostname, port)

            # use the receive method to receive the reply from the server and store the information back into the book-keeping variables
            num_losses, RTTs = receive(clientSocket, num_losses, RTTs)

            # increment the sequence number to make the next packet
            seq_no += 1

        # if any exceptions occur, exit the program
        except:
            sys.exit(0)

    # close the socket
    clientSocket.close()
    if RTTs:
        print(f'Summary:    {min(RTTs)} :: {max(RTTs)} :: {avg(RTTs)} :: {round(num_losses/10.0, 3) * 100}%')
    else:
        print(f'Summary:    n/a :: n/a :: n/a :: 100%')


# call main method
if __name__ == '__main__':
    main()    
    