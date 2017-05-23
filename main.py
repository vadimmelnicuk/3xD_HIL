import sys

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

#hilClient = hil.HIL()
#hilClient.connect()
#hilClient.mainLoop()
