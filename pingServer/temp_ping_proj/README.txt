# Jordan Dube V#00946473 #
# PING programming Assignment, CMSC 440 Fall 2022 #
# README.txt #

## Packets ##
#
	Packets have the following format: 
		Version: <Version field>
		Sequence No.: <SequenceNo field>
		Time: <Timestep field>
		Payload Size: <Size field>
		Host: <hostname>
		Class-name: VCU-CMSC440-FALL-2022
		User-name: <your last name>, <your first name>

	The dividing lines (---*---, -------) are only seen when the print_packet method is used 
	Packets are encoded to bytes using the utf-8 charset before they are sent
	Packets are decoded to String using the utf-8 charset after they are received
	There are 4 variations of packets: Ping, Received Ping, Ping Reply, and Received Ping Reply
	The 4 variants are distinguishable by the dividing lines described above

	Example: The client makes its 1st packet, and the String representation of it is below:
		"Version: 1
		Sequence No.: 1
		Time: 37464.900
		Payload Size: 420
		Host: egr-v-cmsc440-2.rams.adp.vcu.edu
		Class-name: VCU-CMSC440-FALL-2022
		User-name: Dube, Jordan"

	When the above packet is printed:
		"---- Ping Packet Header ----" will be displayed above the Version line
		"Version 1" will be printed as "Version 1.0"
		"---- Ping Packet Payload ----" will be displayed between the Payload Size and Host lines
		"----------" will be displayed below the User-name line

	The packet is then encoded to bytes and sent to the server where is it decoded and printed, using "Received Ping Packet" instead of "Ping Packet" in the dividing lines
	The server makes a reply and prints it using "Ping Reply" instead of "Received Ping Packet" in the dividing lines
	The reply is encoded and sent to the client
	The client recieves the reply and prints it using "Received Ping Reply" instead of "Ping Reply" in the dividing lines
#

## Notes ##
#
	To run both server and client on a single machine, 2 or more terminal windows will need to be opened, with 1 running PINGServer.py and the other(s) running PINGClient.py with the same port

	Multiple servers cannot be bound to the same port. An error will occur if multiple server programs are run on the same port

	Multiple clients can connect to a single server
#

## PINGServer.py ##
#
	Usage: python3 PINGServer.py <port>
		<port>:	the port number where the server will be located. Can be a positive integer less than 65536 

	This program creates a socket on the specified port. When the socket is created (in non-blocking mode to allow graceful termination), the program enters an infinite loop:
		sleep for .5ms to allow the termination handler to exit without printing extra lines,
		try to receive any packets coming. Since the socket is non-blocking, an exception is raised immediately due to there not being packets sent to the socket, but the exception is ignored and the loop continues. 
	Thus, the server is always listening for packets and can only be closed by SIGINT (ctrl+c)
	
	Example: Let us assume that port 10500 is unused and we want to host a UDP Ping server on this port. 
		Given this parameter, we run PINGServer.py with "python3 PINGServer.py 10500"
		The server will proceed to listen on the port for packets from clients until the user raises a SIGINT signal (ctrl+c)
		

	## Methods ##
	#
		signal_handler(signal, frame):		signal handler method. Prints exit message and exits program gracefully
			
			signal:	signal to catch (in this case ctrl+c (SIGINT)) 
			frame:	the current stack frame (not needed)

		
		print_packet(div_line_1, div_line_2, packet):		utility method to print the contents of a packet
			
			div_line_1:	string denoting first dividing line
			div_line_2:	string denoting second dividing line
			packet:			the packet to be printed
	
		
		make_reply_header(packet_header):		utility method to create the header portion of a reply packet
			
			packet_header:	the header (first 4 lines) of the packet received from a client


		make_reply_payload(packet_payload):		utility method to create the payload portion of a reply packet

			packet_payload:	the header (first 3 lines) of the packet received from a client


		make_reply(client_packet):		utility method to make a reply packet

			client_packet: 	packet received from the client


		send(server_packet, serverSocket, clientAddress):		wrapper function to handle sending a packet

			server_packet: 	packet made by the make_reply method. Object to be sent back to the client
			serverSocket:	UDP socket created by the server
			clientAddress:	host and port destination to send the reply to


		receive(serverSocket):		wrapper function to handle receiving a packet

			serverSocket: 	UDP socket created by the server


		check_args(args):		utility method to check the validity of the provided arguments

			args: list of user-provided arguments to be used by the server (does not include "python*" or "PINGServer.py")
	#

	## Errors ##
	#
		ERR - cannot create PINGServer socket using port number <port>
			given when a server socket attempts to bind to the user-given port number. This means the port is in use
		Usage: python PINGServer.py port
			given when the user gives more than 1 argument to the program
		ERR -arg 1
			given when the port argument given by the user is not an integer or outside the range of valid port numbers
	#

#

## PINGClient.py ##
#
	Usage: python3 PINGClient.py <hostname> <port>
		<hostname>: 	the hostname of the server you want to connect to. Can be either a server hostname or a server IP address
		<port>:			the port number where the server is located. Can be an integer less than 65536

	This program sends 10 packets to the server specified by the hostname and port specified by the user in the command line.
	When a packet is sent to the server, the packet is either received or dropped. If it is dropped, then a reply will not be sent by the server.
	The timeout interval for the client's socket is 1 second, so when a packet is dropped, the socket waits 1 second before timing out and sending the next packet.
	This program keeps track of how many packets are lost, as well as the Round Trip Times (RTTs) taken by each packet. 
	After the conclusion of the program, a summary is displayed in this format: 'Summary:	<minimum RTT> :: <maximum RTT> :: <average RTT> :: <packet loss rate>'
	
	Example: Let us assume there is a PINGServer.py program running on port 10500 with an IPv4 address of 10.0.0.2, and 10.0.0.2 maps to the hostname egr-v-cmsc440-2.rams.adp.vcu.edu.
		Given these parameters, we can run the PINGClient.py program with "python3 PINGClient.py 10.0.0.2 10500" or "python3 PINGClient.py egr-v-cmsc440-2.rams.adp.vcu.edu 10500"
		The client will proceed to send 1 packet at a time to the server in the manner described above, waiting each time for a reply to arrive before sending the next packet


	## Methods ##
	#
		signal_handler(signal, frame):		signal handler method. Prints exit message and exits program gracefully
			
			signal:			signal to catch (in this case ctrl+c (SIGINT)) 
			frame:			the current stack frame (not needed)

		
		print_packet(div_line_1, div_line_2, packet):		utility method to print the contents of a packet
			
			div_line_1:	string denoting first dividing line
			div_line_2:	string denoting second dividing line
			packet:			the packet to be printed


		make_packet_header(seq_no, packet_payload):		utility function to make the header portion of a packet

			seq_no:         sequence number of the packet being created
			packet_payload: payload portion of the packet being created, used in calculating the size field


		make_packet_payload(client_hostname):		utility method to create the payload portion of a packet

			client_hostname:IP address of the packet's source


		make_packet(client_hostname, seq_no):		utility method to make a reply packet

			client_hostname:IP address of the packet's source
			seq_no:     	sequence number of the packet being created


		send(clientSocket, packet, server_hostname, port):		wrapper function to handle sending a packet

			packet:       	packet made by the make_packet method. Object to be sent to the server
			clientSocket:   UDP socket created by the client
			server_hostname:hostname of packet's destination
			port:           port of packet's destination


		receive(clientSocket, num_losses, RTTs):		wrapper function to handle receiving a packet

			clientSocket: UDP socket created by the client


		avg(list_of_nums):		utility function to return average (arithmetic mean) of a list of numbers

			list_of_nums: 	list of integers or floats that are added and then divided by the lists length to return an average


		check_args(args):		utility method to check the validity of the provided arguments

			args: list of user-provided arguments to be used by the client (does not include "python*" or "PINGServer.py")
	#

	## Errors ##
	#
		EXCEPTION: not a valid destination: (address: <server_hostname>, port: <port>)
			given when a packet cannot be sent to the server
		------- Ping Reply Timed out ------
			given when a reply to a sent Ping packet is not received within 1 second of sending. This happens when the server "drops" a packet
		ERR - connection closed by Server.
			given when the client cannot recieve from the server's socket because the socket was closed on the server's side
		Usage: python PINGServer.py hostname port
			given when an incorrect number of arguments is provided
		ERR -arg 1
			given when the hostname or IP address given is invalid
		ERR -arg 2
			given when the port argument given by the user is not an integer or outside the range of valid port numbers
		ERR - cannot connect PINGClient socket to port number <port>
			given when the socket cannot connect to the server socket given by the user
	#
#
