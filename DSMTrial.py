import binascii
import socket
import sys
import time
import struct
import array

### Globals
SENDER_HASH_ID = 3364240679
SERVER_TCP_IP = '172.100.1.100'	# DevSim IP address
SERVER_TCP_PORT = 31
SENDER_CLIENT_NAME = 'HiLClientOne\0'
BUFFER_SIZE = 1024
B_REG_ACKNW = False
B_FIRST_MSG = False
COUNT = 1
TIME_OLD = time.time()
TIME_NEW = time.time()

### Messages
regMsgIDBytes = (0xFFFF0016).to_bytes(4, byteorder = 'little')
tickMsgIDBytes = (0xFFFF0010).to_bytes(4, byteorder = 'little')
regAckwMsgBytes = (0xFFFF0017).to_bytes(4, byteorder = 'little')
runMsgIDBytes = (0xFFFF000C).to_bytes(4, byteorder = 'little')
runAckwMsgIDBytes = (0xFFFF000E).to_bytes(4, byteorder = 'little')
stopMsgIDBytes = (0xFFFF000D).to_bytes(4, byteorder = 'little')
stopAckwMsgIDBytes = (0xFFFF000F).to_bytes(4, byteorder = 'little')
AIBrakeIDBytes = (0xFFFF0020).to_bytes(4, byteorder = 'little')
clientNameBytes = b'HiLClientOne\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0'
senderHashIDBytes = (SENDER_HASH_ID).to_bytes(4, byteorder = 'little')
BitPad6 = (0x000000).to_bytes(6, byteorder = 'little')
BitPad8 = (0x00000000).to_bytes(8, byteorder = 'little')
BitPad4 = (0x0000).to_bytes(4, byteorder = 'little')
BitPad2 = (0x00).to_bytes(2, byteorder = 'little')
BitPad50 = (0x00).to_bytes(50, byteorder = 'little')
clientNameLenBytes = (len('HiLClientOne')).to_bytes(8, byteorder = 'little')
AIOvrdBoolBytes = (True).to_bytes(8, byteorder = 'little')
AINOOvrdBoolBytes = (False).to_bytes(8, byteorder = 'little')
AccelOvrdBytes = bytes(array.array('d', [0.0]))
AccelNOOvrdBytes = bytes(array.array('d', [-0.01]))
brakeOvrdBytes = bytes(array.array('d', [1.0]))
brakeNOOvrdBytes = bytes(array.array('d', [0.0]))

### Message sizes
regMsgSize = (len(BitPad4 + regMsgIDBytes + senderHashIDBytes + BitPad4 + bytes(array.array('d', [time.clock()])) + clientNameLenBytes + clientNameBytes)).to_bytes(4, byteorder = 'little')
tickMsgSize = (len(BitPad4 + BitPad8 + tickMsgIDBytes + senderHashIDBytes + BitPad4 + bytes(array.array('d', [time.clock()])))).to_bytes(4, byteorder = 'little')
runAckwMsgSize = (len(BitPad4 + runAckwMsgIDBytes + senderHashIDBytes + BitPad4 + bytes(array.array('d', [time.clock()])))).to_bytes(4, byteorder = 'little')
stopAckwMsgSize = (len(BitPad4 + stopAckwMsgIDBytes + senderHashIDBytes + BitPad4 + bytes(array.array('d', [time.clock()])))).to_bytes(4, byteorder = 'little')
AIBrakeRtnMsgSize = (len(BitPad4 + AIBrakeIDBytes + senderHashIDBytes + BitPad4 + bytes(array.array('d', [-0.01])))).to_bytes(4, byteorder = 'little')
AIBrakeOvrdMsgSize = (len(BitPad4 + AIBrakeIDBytes + senderHashIDBytes + bytes(array.array('d', [-0.01])) + BitPad4 + AIOvrdBoolBytes + AccelOvrdBytes + brakeOvrdBytes)).to_bytes(4, byteorder = 'little')
AIBrakeNOOvrdMsgSize = (len(BitPad4 + AIBrakeIDBytes + senderHashIDBytes + bytes(array.array('d', [-0.01])) + BitPad4 + AINOOvrdBoolBytes + AccelNOOvrdBytes + brakeNOOvrdBytes)).to_bytes(4, byteorder = 'little')
AIBrakeOvrdMsgPayloadBytes = AIOvrdBoolBytes + AccelOvrdBytes + brakeOvrdBytes
AIBrakeNOOvrdMsgPayloadBytes = AINOOvrdBoolBytes + AccelOvrdBytes + brakeNOOvrdBytes
regMsgBytes = regMsgSize + regMsgIDBytes + senderHashIDBytes + BitPad4 + bytes(array.array('d', [time.clock()])) + clientNameLenBytes + clientNameBytes 

### Main
print("Reg Msg Size: " + str(len(regMsgBytes)))

try:
	print("Connecting to server: " + SERVER_TCP_IP + ":" + str(SERVER_TCP_PORT))
	clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	clientSock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
	clientSock.connect((SERVER_TCP_IP, socket.htons(31)))
	clientSock.setblocking(False)
	bConnected = True
	print("Connected.")
	while bConnected == True:
		print("meow")
except TypeError:
	clientSock.close()
	print("Connection Failed.")
