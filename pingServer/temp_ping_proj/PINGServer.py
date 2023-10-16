# PINGServer.py for CMSC 440 Programming Assignment 
# 	by Jordan Dube, 11/28/2022

# imports, no outside libraries
from socket import *
import sys
import time
import random
import signal


# signal handler method. Prints exit message and exits program gracefully
#		signal:	signal to catch (in this case ctrl+c (SIGINT)) 
#		frame:	the current stack frame (not needed)
def signal_handler(signal, frame):
	print('\nCtrl+C detected. Thanks for playing :)')
	exit()
	sys.exit(0)


# utility method to print the contents of a packet
#		div_line_1:	string denoting first dividing line
#		div_line_2:	string denoting second dividing line
#		packet:	the packet to be printed
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


# utility method to create the header portion of a reply packet
#		packet_header:	the header (first 4 lines) of the packet received from a client
def make_reply_header(packet_header):

	# return a string representing the fields of the header (copied from the received packet's header)
	return f"{packet_header[0]}\n{packet_header[1]}\n{packet_header[2]}\n{packet_header[3]}"


# utility method to create the payload portion of a reply packet
#		packet_payload:	the header (first 3 lines) of the packet received from a client  
def make_reply_payload(packet_payload):

	# empty string variable to accumulate new lines
	reply_payload_string = ''

	# for each line in the payload, change to uppercase and add it to the accumulation string
	for i in range(len(packet_payload)):
		packet_payload[i] = packet_payload[i].upper()
		reply_payload_string += f'{packet_payload[i]}\n'

	# return the accumulation string
	return reply_payload_string


# utility method to make a reply packet
#		client_packet: packet received from the client
def make_reply(client_packet):

	# split the packet into the header and the payload
	packet_header = client_packet.splitlines()[:4]
	packet_payload = client_packet.splitlines()[4:]

	# make the header and payload for the reply from the lists created above
	reply_payload = make_reply_payload(packet_payload)
	reply_header = make_reply_header(packet_header)

	# return a string combining the reply header and reply payload
	return f"{reply_header}\n{reply_payload}"


# wrapper function to handle sending a packet
#		server_packet: 	packet made by the make_reply method. Object to be sent back to the client
#		serverSocket:	UDP socket created by the server
# 		clientAddress:	host and port destination to send the reply to
def send(server_packet, serverSocket, clientAddress):
	
	# attempt to send the reply encoded in utf-8 format (bytes) to the provided client address, quit if an exception occurs
	try:
		serverSocket.sendto(server_packet.encode(), clientAddress)
	except Exception as e:
		print(e)
		exit()

	# print the reply packet that was sent
	print_packet(f'-----------Ping Reply Header ----------', f'---------- Ping Reply Payload -------------', server_packet)


# wrapper function to handle receiving a packet
#		serverSocket: UDP socket created by the server 
def receive(serverSocket):

	# try to receive a packet
	try:

		# If it does receive, captures the source of the packet as well as the packet
		client_packet, clientAddress = serverSocket.recvfrom(2048)

	except KeyboardInterrupt:

		# only handle ctrl+C, explicitly raises a Keyboard Interrupt exception which gets handled by the signal_handle method
		raise KeyboardInterrupt

	# decode the bytes received from the client
	client_packet = client_packet.decode()

	# the sequence number of the packet is captured to print the book-keeping string specified in the project manual (2nd line, last element after splitting on white space)
	seq_no = client_packet.splitlines()[1].split(' ')[-1]

	# randomly generate a number between 1 and 10, if 1, 2, or 3, the packet is dropped and the flag is set to DROPPED, otherwise it is RECEIVED
	drop_toggle = 'DROPPED' if (randint := random.randint(1, 10)) < 4 else 'RECEIVED'

	# print book-keeping string in "source host:source port:sequence number:DROPPED||RECEIVED"
	print(f'{clientAddress[0]}:{clientAddress[1]}:{seq_no}:{drop_toggle}')

	# print the recieved ping packet
	print_packet(f'----------Received Ping Packet Header----------', f'---------Received Ping Packet Payload------------', client_packet)

	# if the packet is not dropped, make the reply for the packet and call the send method to send it
	if drop_toggle == 'RECEIVED':
		server_packet = make_reply(client_packet)
		send(server_packet, serverSocket, clientAddress)


# utility method to check the validity of the provided arguments
# 		args: list of user-provided arguments to be used by the server (does not include "python*" or "PINGServer.py")
def check_args(args):

	# if there is more or less than one argument, inform user regarding usage and return 0
	if len(args) != 1:
		print("Usage: python PINGServer.py port")
		return 0

	# try to parse the single argument as an integer
	try:
		port = int(args[0])

		# check if the number is valid with regard to the value. If not, raise an Exception to trigger the except: block
		if port >= 65536 or port <= 0:
			raise Exception

	# if an exception is raised, inform the user to enter a valid port number and return 0
	except:
		print(f'ERR - arg 1')
		return 0

	# if the method has not ended by this point, then the port number is valid and it is returned
	return port


# main driver method
def main():

	# omit "PINGServer.py" from the list of system arguments
	args = sys.argv[1:]

	# Stores result of checking the provided arguments. If 0 is returned, the program will not proceed
	if (port := check_args(args)):

		# try to create a socket and bind it to the given port
		try:
			serverSocket = socket(AF_INET, SOCK_DGRAM)
			serverSocket.bind(('', port))

			# set signal check, only needs to be set once
			signal.signal(signal.SIGINT, signal_handler)

			# set the server socket to nonblocking. This is because when in blocking mode, the user cannot exit the program with a keyboard interruption
			serverSocket.setblocking(0)

		# exception is raised if the user attempts to use a port that is already occupied, prints error message and exits
		except Exception as e:
			print(f"ERR - cannot create PINGServer socket using port number <{port}>")
			exit()

		# gets the hostname
		hostname = gethostname()

		# uses hostname to get the IP address (IPv4)
		ip = gethostbyname(hostname)

		# prints the socket's information to the terminal
		print(f"PINGServer's socket is created using port number {port} with IP address {ip}...")
		
		# While loop to handle arbitrary sequence of clients making requests
		while 1:

			# sleep for .5ms to avoid effectively locking the user from using ctrl+c
			time.sleep(.0005)

			# Tries to recieve a packet, and raises an exception if it doesn't immediately receive a packet. This is due to the socket being in non-blocking mode
			try:
				receive(serverSocket)

			# if an exception is raised, pass so that the loop can continue waiting for a new packet
			except:
				pass


# call main method
if __name__ == '__main__':
	main()
	