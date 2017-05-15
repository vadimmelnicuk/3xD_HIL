import RPi.GPIO as GPIO
import binascii
import socket
import sys
import time
import struct
import array


#class myThread(threading.Thread)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(7,GPIO.OUT)

GPIO.output(7,True)

########################
###    Defining variables

senderHashID = 3364240679
ServerTCP_IP = '172.100.1.100'
ServerTCP_PORT = 31

BUFFER_SIZE = 1024

senderClientName = 'HiLClientOne\0'
print(ServerTCP_PORT)
print(ServerTCP_IP)


#########################  Creating Message bytes

regMsgIDBytes = (0xFFFF0016).to_bytes(4, byteorder = 'little')
tickMsgIDBytes = (0xFFFF0010).to_bytes(4, byteorder = 'little')
regAckwMsgBytes = (0xFFFF0017).to_bytes(4, byteorder = 'little')
runMsgIDBytes = (0xFFFF000C).to_bytes(4, byteorder = 'little')
runAckwMsgIDBytes = (0xFFFF000E).to_bytes(4, byteorder = 'little')
stopMsgIDBytes = (0xFFFF000D).to_bytes(4, byteorder = 'little')
stopAckwMsgIDBytes = (0xFFFF000F).to_bytes(4, byteorder = 'little')
AIBrakeIDBytes = (0xFFFF0020).to_bytes(4, byteorder = 'little')

clientNameBytes = b'HiLClientOne\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0'
senderHashIDBytes = (senderHashID).to_bytes(4, byteorder = 'little')
BitPad6 =(0x000000).to_bytes(6, byteorder = 'little')
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

#########################  Size of messages
regMsgSize = (len(BitPad4 + regMsgIDBytes + senderHashIDBytes + BitPad4 + bytes(array.array('d', [time.clock()])) + clientNameLenBytes + clientNameBytes)).to_bytes(4, byteorder = 'little')

tickMsgSize = (len(BitPad4 + BitPad8 + tickMsgIDBytes + senderHashIDBytes + BitPad4 + bytes(array.array('d', [time.clock()])))).to_bytes(4, byteorder = 'little')
runAckwMsgSize = (len(BitPad4 + runAckwMsgIDBytes + senderHashIDBytes + BitPad4 + bytes(array.array('d', [time.clock()])))).to_bytes(4, byteorder = 'little')
stopAckwMsgSize = (len(BitPad4 + stopAckwMsgIDBytes + senderHashIDBytes + BitPad4 + bytes(array.array('d', [time.clock()])))).to_bytes(4, byteorder = 'little')
AIBrakeRtnMsgSize = (len(BitPad4 + AIBrakeIDBytes + senderHashIDBytes + BitPad4 + bytes(array.array('d', [-0.01])))).to_bytes(4, byteorder = 'little')
AIBrakeOvrdMsgSize = (len(BitPad4 + AIBrakeIDBytes + senderHashIDBytes + bytes(array.array('d', [-0.01])) + BitPad4 + AIOvrdBoolBytes + AccelOvrdBytes + brakeOvrdBytes)).to_bytes(4, byteorder = 'little')
AIBrakeNOOvrdMsgSize = (len(BitPad4 + AIBrakeIDBytes + senderHashIDBytes + bytes(array.array('d', [-0.01])) + BitPad4 + AINOOvrdBoolBytes + AccelNOOvrdBytes + brakeNOOvrdBytes)).to_bytes(4, byteorder = 'little')


AIBrakeOvrdMsgPayloadBytes = AIOvrdBoolBytes + AccelOvrdBytes + brakeOvrdBytes
AIBrakeNOOvrdMsgPayloadBytes = AINOOvrdBoolBytes + AccelOvrdBytes + brakeNOOvrdBytes


######################### Creating series of bytes for the messages to be sent

regMsgBytes = regMsgSize + regMsgIDBytes + senderHashIDBytes + BitPad4 + bytes(array.array('d', [time.clock()])) + clientNameLenBytes + clientNameBytes 
print(len(regMsgBytes))

bRegAcknw = False
bRegAcknw = False
count = 1
buttonCnt = 0
bButton = True
bFirstMsg = False

timeOld = time.time()
timeNew = time.time()

try:
    print("Trying to connect...\n")
    clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
    clientSock.connect((ServerTCP_IP,socket.htons(31)))
    clientSock.setblocking(False)
    bConnected = True
    print(bConnected)
    print("Connected!")

    #count = count + 1
    while bConnected == True:
        #rcvdMsg4mServer = clientSock.recv(1024)
        #count = count + 1
        #print(count)
        
        while bRegAcknw == False:
            print("Trying to register")
            clientSock.sendall(regMsgBytes)
            #time.sleep(0.2)
            print('tick')
            
            rcvdMsg4mServer = clientSock.recv(24)

            if rcvdMsg4mServer[4:8] == regAckwMsgBytes:
                bRegAcknw = True
                print(bRegAcknw)
                print('Reg Acknw received')
                rcvdMsg4mServer = ''

        while bRegAcknw == True:
            #rcvdMsg4mServer = clientSock.recv(24)
            # sending ticks every 100ms
            if timeNew - timeOld > 0.1:
                timeOld = timeNew
                count = count + 1
                countBytes = (count).to_bytes(8, byteorder = 'little')
                tickMsgBytes = tickMsgSize + tickMsgIDBytes + senderHashIDBytes + BitPad4 + bytes(array.array('d', [time.clock()])) + countBytes
                clientSock.sendall(tickMsgBytes)
            else:
                timeNew = time.time()

            #try:
                #rcvdMsg4mServer = clientSock.recv(1024)
                #print(rcvdMsg4mServer)

            #except (socket.error):
                #continue
                #err = e.args[0]
                #if err == errno.EAGAIN or err ==errno.EWOULDBLOCK:
                    #time.sleep(1)
                    #print("no data")
                    #contnue

            #print(rcvdMsg4mServer)
            #if not rcvdMsg4mServer: break
            if rcvdMsg4mServer[4:8] == stopMsgIDBytes:
                stopAckwMsgBytes = stopAckwMsgSize + stopAckwMsgIDBytes + senderHashIDBytes + BitPad4 + bytes(array.array('d', [time.clock()]))
                print('STOP Ackw SENT')
                rcvdMsg4mServer = ''            
            
            if rcvdMsg4mServer[4:8] == runMsgIDBytes:
                runAckwMsgBytes = runAckwMsgSize + runAckwMsgIDBytes + senderHashIDBytes + BitPad4 + bytes(array.array('d', [time.clock()]))
                clientSock.sendall(runAckwMsgBytes)
                print('Run Ackw SENT')
                rcvdMsg4mServer = ''
                          
            if GPIO.input(12) == False:
                if bButton == True:
                    if buttonCnt%2 == 0:
                        print('Button Pressed Brake')
                        print(buttonCnt)
                        AIBrakeOvrdMsgBytes = AIBrakeOvrdMsgSize + AIBrakeIDBytes + senderHashIDBytes + BitPad4 + bytes(array.array('d', [time.clock()])) + AIBrakeOvrdMsgPayloadBytes
                        print(AIBrakeOvrdMsgBytes)
                        clientSock.sendall(AIBrakeOvrdMsgBytes)
                        GPIO.output(7,False)

                    if buttonCnt%2 == 1:
                        print('Button Pressed Return')
                        print(buttonCnt)
                        AIBrakeRtnMsgBytes = AIBrakeOvrdMsgSize + AIBrakeIDBytes + senderHashIDBytes + BitPad4 + bytes(array.array('d', [time.clock()])) + AIBrakeNOOvrdMsgPayloadBytes
                        print(AIBrakeRtnMsgBytes)
                        clientSock.sendall(AIBrakeRtnMsgBytes)
                        GPIO.output(7,True)

                    time.sleep(0.2)
                    buttonCnt = buttonCnt + 1
                    bButton = False
                
            if GPIO.input(12) == True:
                bButton =  True

except TypeError:
    clientSock.close()
    GPIO.cleanup()
    print("Connection Failed ! \n")
