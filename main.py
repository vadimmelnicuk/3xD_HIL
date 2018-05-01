import sys
import time

import hil
import ble

### Main
print("--------------------------------------------------------------")
print("3xD HIL Client written in Python v1.0")
print("Developed by Vadim Melnicuk & Siddartha Khastgir")
print("2017")
print("--------------------------------------------------------------\n")

bleClient = ble.BLE()
bleClient.connect()

hilClient = hil.HIL()
hilClient.connect()

# Main loop
while hilClient.CONNECTED == True:
	hilClient.registerClient()
	
	while hilClient.REG_ACKNW == True:
		hilClient.readMessage()
		message = hilClient.processMessages()
		
		if message != None:
			bleClient.send(message)
			
		inputStream = bleClient.receive()
	
		if hilClient.SCENARIO_RUNNING and inputStream == b'100':
			inputStream = ''
			hilClient.manualControlMessage()
			
		hilClient.tick()
