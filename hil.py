import binascii
import socket
import sys
import time
import struct
import array

class HIL:
	### Globals
	SENDER_HASH_ID = 3364240679
	SERVER_TCP_IP = '172.100.1.99'	# DevSim or MainSim IP address, 100 for Dev and 99 for Main
	SERVER_TCP_PORT = 31
	SENDER_CLIENT_NAME = 'HiLClientOne\0'
	BUFFER_SIZE = 1024
	CONNECTED = False
	REG_ACKNW = False
	SCENARIO_RUNNING = False
	SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	TICK_RATE = 0.5 # in seconds
	TICK_TIME = time.time()
	TICK_COUNT = 1
	VEHICLE_UPDATE_RATE = 0.033 # in seconds
	VEHICLE_UPDATE_TIME = time.time()
	VEHICLE_ID = 3268448171 # Change this to suit your scenario; the vehicle id can be found in IOS->Tools->Object List->Look for top record
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
	EVENT_IN_V2 = (0xFFFF0015).to_bytes(4, byteorder = 'little')
	MANUAL_CONTROL_ID = (0xFFFF0019).to_bytes(4, byteorder = 'little')
	MANUAL_CONTROL_DELAY = (0).to_bytes(8, byteorder = 'little')
	clientNameBytes = b'HiLClientOne\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0'
	senderHashIDBytes = (SENDER_HASH_ID).to_bytes(4, byteorder = 'little')
	BitPad6 = (0x000000).to_bytes(6, byteorder = 'little')
	BitPad8 = (0x00000000).to_bytes(8, byteorder = 'little')
	BitPad4 = (0x0000).to_bytes(4, byteorder = 'little')
	BitPad2 = (0x00).to_bytes(2, byteorder = 'little')
	BitPad50 = (0x00).to_bytes(50, byteorder = 'little')
	clientNameLenBytes = (len('HiLClientOne')).to_bytes(8, byteorder = 'little')
	MANUAL_CONTROL_MESSAGE_SIZE = (len(BitPad4 + MANUAL_CONTROL_ID + senderHashIDBytes + BitPad4 + bytes(array.array('d', [time.clock()])) + MANUAL_CONTROL_DELAY)).to_bytes(4, byteorder = 'little')

	### Message sizes
	regMsgSize = (len(BitPad4 + regMsgIDBytes + senderHashIDBytes + BitPad4 + bytes(array.array('d', [time.clock()])) + clientNameLenBytes + clientNameBytes)).to_bytes(4, byteorder = 'little')
	tickMsgSize = (len(BitPad4 + BitPad8 + tickMsgIDBytes + senderHashIDBytes + BitPad4 + bytes(array.array('d', [time.clock()])))).to_bytes(4, byteorder = 'little')
	runAckwMsgSize = (len(BitPad4 + runAckwMsgIDBytes + senderHashIDBytes + BitPad4 + bytes(array.array('d', [time.clock()])))).to_bytes(4, byteorder = 'little')
	stopAckwMsgSize = (len(BitPad4 + stopAckwMsgIDBytes + senderHashIDBytes + BitPad4 + bytes(array.array('d', [time.clock()])))).to_bytes(4, byteorder = 'little')
	regMsgBytes = regMsgSize + regMsgIDBytes + senderHashIDBytes + BitPad4 + bytes(array.array('d', [time.clock()])) + clientNameLenBytes + clientNameBytes 

	
	### Functions
	def connect(self):
		try:
			print("CLIENT: Connecting to the HIL server " + self.SERVER_TCP_IP + ":" + str(self.SERVER_TCP_PORT))
			self.SOCKET.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
			self.SOCKET.connect((self.SERVER_TCP_IP, socket.htons(31)))
			self.SOCKET.setblocking(False)
			self.CONNECTED = True
			print("HIL: Connected")
		except TypeError:
			print("HIL: Connection failed")
			self.disconnect()
			
	def disconnect(self):
		self.SOCKET.close()
	
	def registerClient(self):
		print("CLIENT: Attempting to register")
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
		messageSizeBytes = self.MESSAGE[0:4]
		messageIdBytes = self.MESSAGE[4:8]
		messageSenderBytes = self.MESSAGE[8:12]
		messageTimestampBytes = self.MESSAGE[16:24]
		
		messageId = struct.unpack('<I', messageIdBytes)[0]
		
		if self.SCENARIO_RUNNING == False:
			if messageIdBytes == self.runMsgIDBytes:
				print("HIL: Scenario RUN message received ")
				runAckwMsgBytes = self.runAckwMsgSize + self.runAckwMsgIDBytes + self.senderHashIDBytes + self.BitPad4 + bytes(array.array('d', [time.clock()]))
				self.SOCKET.sendall(runAckwMsgBytes)
				print('CLIENT: Scenario RUN acknowledgement sent')
				self.SCENARIO_RUNNING = True
				message = str(messageId)
				return message
		else:
			if messageIdBytes == self.stopMsgIDBytes:
				print("HIL: Scenario STOP message received ")
				stopAckwMsgBytes = self.stopAckwMsgSize + self.stopAckwMsgIDBytes + self.senderHashIDBytes + self.BitPad4 + bytes(array.array('d', [time.clock()]))
				self.SOCKET.sendall(stopAckwMsgBytes)
				print('CLIENT: Scenario STOP acknowledgement sent')
				self.SCENARIO_RUNNING = False
				message = str(messageId)
				return message
			elif messageIdBytes == self.EVENT_IN_V2:
				# avoid multiple triggers from single event trigger hence, delay this for a second after an initial detection
				print("HIL: Scenario event in v2 triggered")
				messageParam1 = struct.unpack('<I', self.MESSAGE[24:28])[0]
				messageParam2 = struct.unpack('<I', self.MESSAGE[28:32])[0]
				messageParam3 = struct.unpack('<d', self.MESSAGE[32:40])[0]
				message = str(messageId)+","+str(messageParam1)+","+str(messageParam2)+","+str(messageParam3)
				return message
			elif messageIdBytes == self.VEHICLE_UPDATE_MESSAGE:
				messageVehicleId = struct.unpack('<I', self.MESSAGE[24:28])[0]
				# Check if a message arrived from the trainee vehicle
				# Also check against data rate
				if messageVehicleId == self.VEHICLE_ID and time.time() - self.VEHICLE_UPDATE_TIME >= self.VEHICLE_UPDATE_RATE:
					#print('HIL: Vehicle update received')
					self.VEHICLE_UPDATE_TIME = time.time()
					
					messageFlags = struct.unpack('<I', self.MESSAGE[28:32])[0]
					messageFlagBits = bin(messageFlags)
					messageHeadLight = messageFlagBits[-1]
					messageBrakeLight = messageFlagBits[-2]
					messageReverseLight = messageFlagBits[-3]
					messageFogLight = messageFlagBits[-4]
					messageLeftIndicator = messageFlagBits[-5]
					messageRightIndicator = messageFlagBits[-6]
					messageHordOn = messageFlagBits[-7]
					messageEngineOn = messageFlagBits[-8]
					messageWheelScreeching = messageFlagBits[-9]
					messageHiBeamOn = messageFlagBits[-10]
					messageHandBrake = messageFlagBits[-11]
					messagePositionLatitude = struct.unpack('<d', self.MESSAGE[32:40])[0]
					messagePositionLongitude = struct.unpack('<d', self.MESSAGE[40:48])[0]
					messagePositionElevation = struct.unpack('<d', self.MESSAGE[48:56])[0]
					messagePositionX = struct.unpack('<d', self.MESSAGE[56:64])[0]
					messagePositionY = struct.unpack('<d', self.MESSAGE[64:72])[0]
					messagePositionZ = struct.unpack('<d', self.MESSAGE[72:80])[0]
					messageOrientationX = struct.unpack('<d', self.MESSAGE[80:88])[0]
					messageOrientationY = struct.unpack('<d', self.MESSAGE[88:96])[0]
					messageOrientationZ = struct.unpack('<d', self.MESSAGE[96:104])[0]
					messageVelocityX = struct.unpack('<d', self.MESSAGE[104:112])[0]
					messageVelocityY = struct.unpack('<d', self.MESSAGE[112:120])[0]
					messageVelocityZ = struct.unpack('<d', self.MESSAGE[120:128])[0]
					messageAccelerationX = struct.unpack('<d', self.MESSAGE[128:136])[0]
					messageAccelerationY = struct.unpack('<d', self.MESSAGE[136:144])[0]
					messageAccelerationZ = struct.unpack('<d', self.MESSAGE[144:152])[0]
					messageAngularVelocityX = struct.unpack('<d', self.MESSAGE[152:160])[0]
					messageAngularVelocityY = struct.unpack('<d', self.MESSAGE[160:168])[0]
					messageAngularVelocityZ = struct.unpack('<d', self.MESSAGE[168:176])[0]
					messageSteeringAngle = struct.unpack('<d', self.MESSAGE[176:184])[0]
					messageRpm = struct.unpack('<d', self.MESSAGE[184:192])[0]
					messageAcceleratorPedal = struct.unpack('<d', self.MESSAGE[192:200])[0]
					messageBrakePedal = struct.unpack('<d', self.MESSAGE[200:208])[0]
					messageClutchPedal = struct.unpack('<d', self.MESSAGE[208:216])[0]
					messageSteeringWheelAngle = struct.unpack('<d', self.MESSAGE[216:224])[0]
 					# signed int, from 1 to 6 number coresponds to the gear, automatic park = 7, automatic drive = 8, reverse = -1
					messageGear = struct.unpack('<i', self.MESSAGE[224:228])[0]
 					
					#print("Vehicle id: " + str(messageVehicleId))
					#print("Vehicle flags: " + str(messageHandBrake))
					#print("Vehicle Acceleration: " + str(messageAcceleratorPedal))
					#print("Vehicle RPM: " + str(messageRpm))
					#print("Vehicle Steering Angle: " + str(messageSteeringWheelAngle))
					
					message = str(messageId)+","+str(messageVehicleId)+","+str(messageHeadLight)+","+str(messageBrakeLight)+","+str(messageReverseLight)+","+str(messageFogLight)+","+str(messageLeftIndicator)+","+str(messageRightIndicator)+","+str(messageHordOn)+","+str(messageEngineOn)+","+str(messageWheelScreeching)+","+str(messageHiBeamOn)+","+str(messageHandBrake)+","+str(messagePositionLatitude)+","+str(messagePositionLongitude)+","+str(messagePositionElevation)+","+str(messagePositionX)+","+str(messagePositionY)+","+str(messagePositionZ)+","+str(messageOrientationX)+","+str(messageOrientationY)+","+str(messageOrientationZ)+","+str(messageVelocityX)+","+str(messageVelocityY)+","+str(messageVelocityZ)+","+str(messageAccelerationX)+","+str(messageAccelerationY)+","+str(messageAccelerationZ)+","+str(messageAngularVelocityX)+","+str(messageAngularVelocityY)+","+str(messageAngularVelocityZ)+","+str(messageSteeringAngle)+","+str(messageRpm)+","+str(messageAcceleratorPedal)+","+str(messageBrakePedal)+","+str(messageClutchPedal)+","+str(messageSteeringWheelAngle)+","+str(messageGear)
					return message
		
	def tick(self):
		if time.time() - self.TICK_TIME >= self.TICK_RATE:
			#print("TICK: " + str(self.TICK_COUNT))
			self.TICK_TIME = time.time()
			self.TICK_COUNT += 1
			countBytes = (self.TICK_COUNT).to_bytes(8, byteorder = 'little')
			tickMsgBytes = self.tickMsgSize + self.tickMsgIDBytes + self.senderHashIDBytes + self.BitPad4 + bytes(array.array('d', [time.clock()])) + countBytes
			self.SOCKET.sendall(tickMsgBytes)
			
	def manualControlMessage(self):
		print('CLIENT: Manual control message sent')
		messageBytes = self.MANUAL_CONTROL_MESSAGE_SIZE + self.MANUAL_CONTROL_ID + self.senderHashIDBytes + self.BitPad4 + bytes(array.array('d', [time.clock()])) + self.MANUAL_CONTROL_DELAY
		self.SOCKET.sendall(messageBytes)
