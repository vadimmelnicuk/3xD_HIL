import sys
import bluetooth

class BLE:
	
	SERVER_UUID = "56e8a14a-80b3-11e5-8bcf-feff819cdc9f"
	SERVER_ADDR = None
	SERVER_PORT = None
	SERVER_NAME = None
	SERVER_HOST = None
	
	SOCKET = None
	
	def connect(self):
		print("BLE: Looking for the server")
		
		# Scan for bluetooth devices
		#nearby_devices = bluetooth.discover_devices(lookup_names=True)
		#print("found %d devices" % len(nearby_devices))

		#for addr, name in nearby_devices:
			#print("  %s - %s" % (addr, name))
		
		serviceMatches = bluetooth.find_service( uuid = self.SERVER_UUID, address = self.SERVER_ADDR )
		
		if len(serviceMatches) == 0:
			print("BLE: Couldn't find the specified server")
			sys.exit(0)
			
		firstMatch = serviceMatches[0]
		self.SERVER_PORT = firstMatch["port"]
		self.SERVER_NAME = firstMatch["name"]
		self.SERVER_HOST = firstMatch["host"]
		
		print("BLE: Connecting to \"%s\" on %s" % (self.SERVER_NAME, self.SERVER_HOST))
		
		# Create the client socket
		self.SOCKET = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
		self.SOCKET.connect((self.SERVER_HOST, self.SERVER_PORT))
		
		print("BLE: Connected")
		
		self.output()
		
	def output(self):
		while True:
			data = input()
			if len(data) == 0: break
			self.SOCKET.send(data)
			
	def send(self, message):
		self.SOCKET.send(message)

	def disconnect(self):
		self.SOCKET.close()
