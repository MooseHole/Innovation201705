from testGui import statusUpdate

# A printer supporting the TCL (Thermal Control Language) protocol
class Tcl:
	# Constructor
	# comm = communication parameters formatted like 9600 8N1 (speed; data bits; parity; stop bits)
	# status (optional) = Initial status (see UpdateStatus)
	def __init__(self, comm, status=""):
		self.comm = comm
		self.status = status
		self.fversion = ""
		self.lastTemplate = ""
		self.message = ""

		self.ResetErrors()

		if status != "":
			self.UpdateStatus(status)
			self.UpdateMessage()
			
	def Update(self, message)
		self.UpdateStatus(message)
		self.UpdateMessage()
		statusUpdate(GetLabels())

	# Get ready to read the new status: reset all errors.
	def ResetErrors(self):
		# Byte 0
		self.error = False
		self.voltageError = False   			# Bit 0
		self.headError = False  				# Bit 1
		self.paperOut = False   				# Bit 2
		self.drawerOpen = False 				# Bit 3
		self.systemError = False				# Bit 4
		self.busy = False   					# Bit 5
		# Byte 1
		self.jobMemoryOverflow = False  		# Bit 0
		self.bufferOverflow = False 			# Bit 1
		self.libraryLoadError = False   		# Bit 2
		self.prDataError = False				# Bit 3
		self.libraryRefError = False			# Bit 4
		self.temperatureError = False   		# Bit 5
		# Byte 2
		self.missingSupplyIndex = False 		# Bit 0
		self.printerOffline = False 			# Bit 1
		self.flashProgError = False 			# Bit 2
		self.paperInChute = False   			# Bit 3
		self.printLibrariesCorrupted = False	# Bit 4
		self.commandError = False   			# Bit 5
		#Byte 3
		self.paperLow = False   				# Bit 0
		self.paperJam = False   				# Bit 1
		self.cutterError = False				# Bit 2
		self.journalPrinting = False			# Bit 3
		# Byte 4
		self.powerUp = False					# Bit 0 => FutureLogic only
		self.barcodeDataProcessed = False   	# Bit 1 => FutureLogic only
		self.printerOpen = False				# Bit 2
		self.xoff = False   					# Bit 3
		self.topOfForm = False  				# Bit 4
		self.validationDone = False 			# Bit 5 => FutureLogic only

	def GetLabels():
		result = {"Message":self.message, "Com":self.comm, "Status":self.status}
		return result

	# Updates the printer status
	# status = the status received from the printer formatted like "*S|0|GURUSAG18|@|@|@|@|A|Px|*"
	#	There are 9 fields separated by '|'; the entire message is delimited by '*':
	#	1) Message type (S = status)
	#	2) Unit address (almost always 0)
	#	3) Software version (see DecodeVersion)
	#	4-8) Status
	#	9) Last template printed. Starts with a P
	#   The "standard status" has only 7 fields, removing 2 from the status group
	def UpdateStatus(self, status):
		self.status = status
		parts = status.split("|")
		if len(parts) != 10:
			return

		self.fversion = parts[2]
		self.byte0 = ord(parts[3])
		self.byte1 = ord(parts[4])
		self.byte2 = ord(parts[5])
		self.byte3 = ord(parts[6])
		self.byte4 = ord(parts[7])
		self.lastTemplate = parts[8][1:] # skip the first character, P

		self.ResetErrors()

		if (self.byte0 & 0x01) != 0:
			self.voltageError = True
			self.error = True
		if (self.byte0 & 0x02) != 0:
			self.headError = True
			self.error = True
		if (self.byte0 & 0x04) != 0:
			self.paperOut = True
			self.error = True
		if (self.byte0 & 0x08) != 0:
			self.drawerOpen = True
			self.error = True
		if (self.byte0 & 0x10) != 0:
			self.systemError = True
			self.error = True
		if (self.byte0 & 0x20) != 0:
			self.busy = True

		if (self.byte1 & 0x01) != 0:
			self.jobMemoryOverflow = True
			self.error = True
		if (self.byte1 & 0x02) != 0:
			self.bufferOverflow = True
			self.error = True
		if (self.byte1 & 0x04) != 0:
			self.libraryLoadError = True
			self.error = True
		if (self.byte1 & 0x08) != 0:
			self.prDataError = True
			self.error = True
		if (self.byte1 & 0x10) != 0:
			self.libraryRefError = True
			self.error = True
		if (self.byte1 & 0x20) != 0:
			self.temperatureError = True
			self.error = True

		if (self.byte2 & 0x01) != 0:
			self.missingSupplyIndex = True
			self.error = True
		if (self.byte2 & 0x02) != 0:
			self.printerOffline = True
			self.error = True
		if (self.byte2 & 0x04) != 0:
			self.flashProgError = True
			self.error = True
		if (self.byte2 & 0x08) != 0:
			self.paperInChute = True
			self.error = True
		if (self.byte2 & 0x10) != 0:
			self.printLibrariesCorrupted = True
			self.error = True
		if (self.byte2 & 0x20) != 0:
			self.commandError = True
			self.error = True

		if (self.byte3 & 0x01) != 0:
			self.paperLow = True
		if (self.byte3 & 0x02) != 0:
			self.paperJam = True
			self.error = True
		if (self.byte3 & 0x04) != 0:
			self.cutterError = True
			self.error = True
		if (self.byte3 & 0x08) != 0:
			self.journalPrinting = True

		if (self.byte4 & 0x01) != 0:
			self.powerUp = True
		if (self.byte4 & 0x02) != 0:
			self.barcodeDataProcessed = True
		if (self.byte4 & 0x04) != 0:
			self.printerOpen = True
			self.error = True
		if (self.byte4 & 0x08) != 0:
			self.xoff = True
		if (self.byte4 & 0x10) != 0:
			self.topOfForm = True
			self.error = True
		if (self.byte4 & 0x20) != 0:
			self.validationDone = True

	def UpdateMessage(self):
		if self.systemError:
			if self.libraryRefError:
				self.message = "Ready to print, a previous error (unknown library)"
			elif self.drawerOpen:
				self.message = "Print head is up"
			elif self.paperOut:
				self.message = "Paper is out"
			elif self.prDataError:
				self.message = "Improper batch data in one of the Print Regions"
			elif self.busy and self.voltageError:
				self.message = "Power supply error while printing"
			elif self.missingSupplyIndex:
				self.message = "Cannot find supply index mark"
			elif self.bufferOverflow:
				if self.libraryLoadError:
					self.message = "Memory overflow"
				else:
					self.message = "Communications buffer overflow"
			elif self.prDataError:
				self.message = "Data within a Print Region was truncated"
			elif self.headError:
				self.message = "Bad connection with the print head"
			elif self.commandError:
				self.message = "Garbled or unrecognized command was received"
			else:
				self.message = "Generic error"
		else:
			if self.paperInChute:
				self.message = "Paper in the chute"
			elif self.busy:
				self.message = "Loading new font into memory"
			else:
				self.message = "Ready to print, no previous errors"

	def DecodeVersion(self, fversion):
		self.fversion = fversion

#################################
# Unit tests
#################################
if __name__ == '__main__':
	test_speed = "9600"
	test_data = "8"
	test_parity = "N"
	test_stop = "1"
	test_comm = test_speed + " " + test_data + test_parity + test_stop
	printer = Tcl(test_comm)
	if printer.comm != test_comm:
		print "Error: wrong communication data; expected '" + test_comm + "'; actual '" + printer.comm

	############################
	def TestStatus(flags, expectedMessage, lastTemplate):




	test_status = "*S|0|GURUSAG18|P|@|@|@|A|Px|*"
	expectedMessage = "Generic error"
	printer.UpdateStatus(test_status)
	printer.UpdateMessage()
	if printer.status != test_status:
		print "Error: wrong status; expected '" + test_status + "'; actual '" + printer.status
	if not printer.error:
		print "Error: should have found an error for |P|@|@|@|A|"
	if not printer.powerUp:
		print "Error: should have detected Power Up for |P|@|@|@|A|"
	if printer.byte0 != ord("P"):
		print "Error splitting: should have ord('P') = 0x40 as byte 0 for |P|@|@|@|A|"
	if printer.byte1 != ord("@"):
		print "Error splitting: should have ord('@') = 0x40 as byte 1 for |P|@|@|@|A|"
	if printer.byte2 != ord("@"):
		print "Error splitting: should have ord('@') = 0x40 as byte 2 for |P|@|@|@|A|"
	if printer.byte3 != ord("@"):
		print "Error splitting: should have ord('@') = 0x40 as byte 3 for |P|@|@|@|A|"
	if printer.byte4 != ord("A"):
		print "Error splitting: should have ord('A') = 0x41 as byte 4 for |P|@|@|@|A|"
	if printer.lastTemplate != "x":
		print "Error: Didn't detect last template from Px; found '" + printer.lastTemplate + "'"
	if printer.message != expectedMessage:
		print "Error: Wrong message for |P|@|@|@|A|: found '" + printer.message + "'; expected '" + expectedMessage + "'"

	#----------------
	test_noError = "*S|0|GURUSAG18|@|@|@|@|@|P#8000|*"
	expectedMessage = "Ready to print, no previous errors"
	printer.UpdateStatus(test_noError)
	printer.UpdateMessage()
	if printer.error:
		print "Error: should not have found an error for |@|@|@|@|@|"
	if printer.byte0 != ord("@"):
		print "Error splitting: should have ord('@') = 0x40 as byte 0 for |@|@|@|@|@|"
	if printer.byte1 != ord("@"):
		print "Error splitting: should have ord('@') = 0x40 as byte 1 for |@|@|@|@|@|"
	if printer.byte2 != ord("@"):
		print "Error splitting: should have ord('@') = 0x40 as byte 2 for |@|@|@|@|@|"
	if printer.byte3 != ord("@"):
		print "Error splitting: should have ord('@') = 0x40 as byte 3 for |@|@|@|@|@|"
	if printer.byte4 != ord("@"):
		print "Error splitting: should have ord('@') = 0x40 as byte 4 for |@|@|@|@|@|"
	if printer.lastTemplate != "#8000":
		print "Error: Didn't detect last template from P#8000; found '" + printer.lastTemplate + "'"
	if printer.message != expectedMessage:
		print "Error: Wrong message for |@|@|@|@|@|: found '" + printer.message + "'; expected '" + expectedMessage + "'"

	test_previousBatchError = "*S|0|GURUSAG18|P|P|@|@|@|P0|*"
	expectedMessage = "Ready to print, a previous error (unknown library)"
	printer.UpdateStatus(test_previousBatchError)
	printer.UpdateMessage()
	if not printer.error:
		print "Error: should have found an error for |P|P|@|@|@|"
	if not printer.error:
		print "Error: should have found an error for |P|P|@|@|@|"
	if not printer.systemError:
		print "Error: should have detected System Error for |P|P|@|@|@|"
	if not printer.libraryRefError:
		print "Error: should have detected Library Reference Error for |P|P|@|@|@|"
	if printer.byte0 != ord("P"):
		print "Error splitting: should have ord('P') = 0x50 as byte 0 for |P|P|@|@|@|"
	if printer.byte1 != ord("P"):
		print "Error splitting: should have ord('P') = 0x50 as byte 1 for |P|P|@|@|@|"
	if printer.byte2 != ord("@"):
		print "Error splitting: should have ord('@') = 0x40 as byte 2 for |P|P|@|@|@|"
	if printer.byte3 != ord("@"):
		print "Error splitting: should have ord('@') = 0x40 as byte 3 for |P|P|@|@|@|"
	if printer.byte4 != ord("@"):
		print "Error splitting: should have ord('@') = 0x40 as byte 4 for |P|P|@|@|@|"
	if printer.lastTemplate != "0":
		print "Error: Didn't detect last template from P0; found '" + printer.lastTemplate + "'"
	if printer.message != expectedMessage:
		print "Error: Wrong message for |P|P|@|@|@|: found '" + printer.message + "'; expected '" + expectedMessage + "'"

	test_memoryOverflow = "*S|0|GURUSAG18|P|F|@|@|@|P0|*"
	expectedMessage = "Memory overflow"
	printer.UpdateStatus(test_memoryOverflow)
	printer.UpdateMessage()
	if not printer.error:
		print "Error: should have found an error for |P|F|@|@|@|"
	if not printer.systemError:
		print "Error: should have detected System Error for |P|F|@|@|@|"
	if not printer.bufferOverflow:
		print "Error: should have detected Buffer Overflow for |P|F|@|@|@|"
	if not printer.libraryLoadError:
		print "Error: should have detected Library Load Error for |P|F|@|@|@|"
	if printer.byte0 != ord("P"):
		print "Error splitting: should have ord('P') = 0x50 as byte 0 for |P|F|@|@|@|"
	if printer.byte1 != ord("F"):
		print "Error splitting: should have ord('F') = 0x46 as byte 1 for |P|F|@|@|@|"
	if printer.byte2 != ord("@"):
		print "Error splitting: should have ord('@') = 0x40 as byte 2 for |P|F|@|@|@|"
	if printer.byte3 != ord("@"):
		print "Error splitting: should have ord('@') = 0x40 as byte 3 for |P|F|@|@|@|"
	if printer.byte4 != ord("@"):
		print "Error splitting: should have ord('@') = 0x40 as byte 4 for |P|F|@|@|@|"
	if printer.lastTemplate != "0":
		print "Error: Didn't detect last template from P0; found '" + printer.lastTemplate + "'"
	if printer.message != expectedMessage:
		print "Error: Wrong message for |P|F|@|@|@|: found '" + printer.message + "'; expected '" + expectedMessage + "'"

	print "End of test"


