import binascii
import socket
import sys
import time
import struct
import array

class HIL:
	### Globals
	SENDER_HASH_ID = 3364240679
	SERVER_TCP_IP = '172.100.1.100'	# DevSim IP address
	SERVER_TCP_PORT = 31
	SENDER_CLIENT_NAME = 'HiLClientOne\0'
	BUFFER_SIZE = 1024
	CONNECTED = False
	REG_ACKNW = False
	SCENARIO_STATE_RUNNING = False
	SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	TICK_RATE = 0.5 # in seconds
	TICK_TIME = time.time()
	TICK_COUNT = 1
	VEHICLE_UPDATE_RATE = 5 # in seconds
	VEHICLE_UPDATE_TIME = time.time()
	MESSAGE = ''

	### Messages
	regMsgIDBytes = (0xFFFF0016).to_bytes(4, byteorder = 'little')
	tickMsgIDBytes = (0xFFFF0010).to_bytes(4, byteorder = 'little')
	regAckwMsgBytes = (0xFFFF0017).to_bytes(4, byteorder = 'little')
	runMsgIDBytes = (0xFFFF000C).to_bytes(4, byteorder = 'little')
	runAckwMsgIDBytes = (0xFFFF000E).to_bytes(4, byteorder = 'little')
	stopMsgIDBytes = (0xFFFF000D).to_bytes(4, byteorder = 'little')
	stopAckwMsgIDBytes = (0xFFFF000F).to_bytes(4, byteorder = 'little')
	VEHICLE_UPDATE_MESSAGE = (0xFFFF0005).to_bytes(4, byteorder = 'little')
	VEHICLE_OWN_ID = (0xFFFFFFFF).to_bytes(4, byteorder = 'little')
	clientNameBytes = b'HiLClientOne\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0'
	senderHashIDBytes = (SENDER_HASH_ID).to_bytes(4, byteorder = 'little')
	BitPad6 = (0x000000).to_bytes(6, byteorder = 'little')
	BitPad8 = (0x00000000).to_bytes(8, byteorder = 'little')
	BitPad4 = (0x0000).to_bytes(4, byteorder = 'little')
	BitPad2 = (0x00).to_bytes(2, byteorder = 'little')
	BitPad50 = (0x00).to_bytes(50, byteorder = 'little')
	clientNameLenBytes = (len('HiLClientOne')).to_bytes(8, byteorder = 'little')

	### Message sizes
	regMsgSize = (len(BitPad4 + regMsgIDBytes + senderHashIDBytes + BitPad4 + bytes(array.array('d', [time.clock()])) + clientNameLenBytes + clientNameBytes)).to_bytes(4, byteorder = 'little')
	tickMsgSize = (len(BitPad4 + BitPad8 + tickMsgIDBytes + senderHashIDBytes + BitPad4 + bytes(array.array('d', [time.clock()])))).to_bytes(4, byteorder = 'little')
	runAckwMsgSize = (len(BitPad4 + runAckwMsgIDBytes + senderHashIDBytes + BitPad4 + bytes(array.array('d', [time.clock()])))).to_bytes(4, byteorder = 'little')
	stopAckwMsgSize = (len(BitPad4 + stopAckwMsgIDBytes + senderHashIDBytes + BitPad4 + bytes(array.array('d', [time.clock()])))).to_bytes(4, byteorder = 'little')
	regMsgBytes = regMsgSize + regMsgIDBytes + senderHashIDBytes + BitPad4 + bytes(array.array('d', [time.clock()])) + clientNameLenBytes + clientNameBytes 
	
	### Functions
	def connect(self):
		try:
			print("SOCKET: Connecting to server " + self.SERVER_TCP_IP + ":" + str(self.SERVER_TCP_PORT))
			self.SOCKET.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
			self.SOCKET.connect((self.SERVER_TCP_IP, socket.htons(31)))
			self.SOCKET.setblocking(False)
			self.CONNECTED = True
			print("SOCKET: Connected")
		except TypeError:
			print("SOCKET: Connection failed")
			self.disconnect()
			
	def disconnect(self):
		self.SOCKET.close()
	
	def registerClient(self):
		print("HIL: Attempting to register")
		while self.REG_ACKNW == False:
			self.SOCKET.sendall(self.regMsgBytes)
			self.readMessage()
			if self.MESSAGE[4:8] == self.regAckwMsgBytes:
				print('HIL: Acknowledgement received')
				self.REG_ACKNW = True
				
	def readMessage(self):
		try:
			self.MESSAGE = self.SOCKET.recv(self.BUFFER_SIZE)
			#print("HIL: Message received " + str(self.MESSAGE))
		except (socket.error):
			# Process message read errors
			return
			
	def processMessages(self):
		messageSize = self.MESSAGE[0:4]
		messageId = self.MESSAGE[4:8]
		messageSender = self.MESSAGE[8:12]
		messagePadding = self.MESSAGE[12:16]
		messageTimestamp = self.MESSAGE[16:24]
		
		if self.SCENARIO_STATE_RUNNING == False:
			if messageId == self.runMsgIDBytes:
				print("HIL: Scenario RUN message received " + str(self.MESSAGE))
				runAckwMsgBytes = self.runAckwMsgSize + self.runAckwMsgIDBytes + self.senderHashIDBytes + self.BitPad4 + bytes(array.array('d', [time.clock()]))
				self.SOCKET.sendall(runAckwMsgBytes)
				print('HIL: Scenario RUN acknowledgement sent')
				self.SCENARIO_STATE_RUNNING = True
		else:
			if messageId == self.stopMsgIDBytes:
				print("HIL: Scenario STOP message received " + str(self.MESSAGE))
				stopAckwMsgBytes = self.stopAckwMsgSize + self.stopAckwMsgIDBytes + self.senderHashIDBytes + self.BitPad4 + bytes(array.array('d', [time.clock()]))
				self.SOCKET.sendall(stopAckwMsgBytes)
				print('HIL: Scenario STOP acknowledgement sent')
				self.SCENARIO_STATE_RUNNING = False
			elif messageId == self.VEHICLE_UPDATE_MESSAGE:
				if time.time() - self.VEHICLE_UPDATE_TIME >= self.VEHICLE_UPDATE_RATE:
					print('HIL: Vehicle update received')
					self.VEHICLE_UPDATE_TIME = time.time()
					#print(self.MESSAGE)
		
		self.MESSAGE = ''
		
	def tick(self):
		if time.time() - self.TICK_TIME >= self.TICK_RATE:
			print("TICK: " + str(self.TICK_COUNT))
			self.TICK_TIME = time.time()
			self.TICK_COUNT += 1
			countBytes = (self.TICK_COUNT).to_bytes(8, byteorder = 'little')
			tickMsgBytes = self.tickMsgSize + self.tickMsgIDBytes + self.senderHashIDBytes + self.BitPad4 + bytes(array.array('d', [time.clock()])) + countBytes
			self.SOCKET.sendall(tickMsgBytes)
			
	def mainLoop(self):
		while self.CONNECTED == True:
			self.registerClient()
			while self.REG_ACKNW == True:
				self.readMessage()
				self.processMessages()
				self.tick()
				
### Main
print("--------------------------------------------------------------")
print("3xD HIL Client written in python")
print("Developed by Vadim Melnicuk")
print("2017")
print("--------------------------------------------------------------\n")

client = HIL()
client.connect()
client.mainLoop()
