from tkinter import *
from RunningDisplay import RunningDisplay
from DeviceInterface import DeviceType

# A printer supporting the TCL (Thermal Control Language) protocol
class Tcl(DeviceType):
	# Constructor
	# comm = communication parameters formatted like 9600 8N1 (speed; data bits; parity; stop bits)
	# status (optional) = Initial status (see UpdateStatus)
	def __init__(self, comm, status=""):
		self.comm = comm
		self.status = status
		self.fversion = ""
		self.lastTemplate = ""
		self.message = ""
		self.model = ""
		self.revision = ""

		self.ResetErrors()

		if status != "":
			self.UpdateStatus(status)
			self.UpdateMessage()

	def Update(self, message):
		print ("Update(\"" + message + "\")");
		self.UpdateStatus(message)
		self.UpdateMessage()
		#statusUpdate(self.GetLabels())

	def GetLabels(self):
		return {
			"Model": self.model,
			"Firmware": self.fversion,
			"Com": self.comm,
			"Message": self.message,
			"Status": self.status
		}

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

		fversion = parts[2]
		byte0 = ord(parts[3])
		byte1 = ord(parts[4])
		byte2 = ord(parts[5])
		byte3 = ord(parts[6])
		byte4 = ord(parts[7])
		self.lastTemplate = parts[8][1:] # skip the first character, P

		self.DecodeVersion(fversion)
		self.ResetErrors()

		if (byte0 & 0x01) != 0:
			self.voltageError = True
			self.error = True
		if (byte0 & 0x02) != 0:
			self.headError = True
			self.error = True
		if (byte0 & 0x04) != 0:
			self.paperOut = True
			self.error = True
		if (byte0 & 0x08) != 0:
			self.drawerOpen = True
			self.error = True
		if (byte0 & 0x10) != 0:
			self.systemError = True
			self.error = True
		if (byte0 & 0x20) != 0:
			self.busy = True

		if (byte1 & 0x01) != 0:
			self.jobMemoryOverflow = True
			self.error = True
		if (byte1 & 0x02) != 0:
			self.bufferOverflow = True
			self.error = True
		if (byte1 & 0x04) != 0:
			self.libraryLoadError = True
			self.error = True
		if (byte1 & 0x08) != 0:
			self.prDataError = True
			self.error = True
		if (byte1 & 0x10) != 0:
			self.libraryRefError = True
			self.error = True
		if (byte1 & 0x20) != 0:
			self.temperatureError = True
			self.error = True

		if (byte2 & 0x01) != 0:
			self.missingSupplyIndex = True
			self.error = True
		if (byte2 & 0x02) != 0:
			self.printerOffline = True
			self.error = True
		if (byte2 & 0x04) != 0:
			self.flashProgError = True
			self.error = True
		if (byte2 & 0x08) != 0:
			self.paperInChute = True
		if (byte2 & 0x10) != 0:
			self.printLibrariesCorrupted = True
			self.error = True
		if (byte2 & 0x20) != 0:
			self.commandError = True
			self.error = True

		if (byte3 & 0x01) != 0:
			self.paperLow = True
		if (byte3 & 0x02) != 0:
			self.paperJam = True
			self.error = True
		if (byte3 & 0x04) != 0:
			self.cutterError = True
			self.error = True
		if (byte3 & 0x08) != 0:
			self.journalPrinting = True

		if (byte4 & 0x01) != 0:
			self.powerUp = True
		if (byte4 & 0x02) != 0:
			self.barcodeDataProcessed = True
		if (byte4 & 0x04) != 0:
			self.printerOpen = True
			self.error = True
		if (byte4 & 0x08) != 0:
			self.xoff = True
		if (byte4 & 0x10) != 0:
			self.topOfForm = True
			self.error = True
		if (byte4 & 0x20) != 0:
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


	# Converts the "software version" into useful information.
	# For Gen2, the version looks like "GURUSAG18":
	#   GU - Gen2 Universal
	#   R - RS232 (i.e. serial, not USB) model
	#   USA - Firmware country/type: e.g. USA, CL2 (class 2), LOT (lottery)
	#   G - Machine OEM: e.g. V (VGT), G (generic)
	#   18 - Revision
	# For Gen2B and Gen3, the version looks like "3RUSAGE05":
	#   3 or 5 - Gen3 and Gen2 Rev. B (formerly Gen5), respectively
	#   R - RS232 (i.e. serial, not USB) model
	#   USA - Firmware country/type: e.g. USA, CL2 (class 2), LOT (lottery)
	#   GE - Machine OEM: e.g. VT (VGT), GE (generic)
	#   05 - Revision
	# Notice that, except for the model (2 letters in Gen2, one number in Gen3 and Gen2B)
	# and the OEM (1 character in Gen2 and 2 in Gen3 and Gen2B) the firmware structure
	# match exactly. Moreover, the length ends up being the same.
	def DecodeVersion(self, fversion):
		if fversion[0:2] == "GU": # Gen2
			self.model = "Gen2"
		elif fversion[0:1] == "3":
			self.model = "Gen3"
		elif fversion[0:1] == "3":
			self.model = "Gen2B"
		else:
			self.model = "Unknown TCL"

		self.revision = fversion[7:9]
		self.fversion = fversion

#################################
# Unit tests
#################################
if __name__ == '__main__' and False:

	#myFiles = RunningDisplay()

	test_speed = "9600"
	test_data = "8"
	test_parity = "N"
	test_stop = "1"
	test_comm = test_speed + " " + test_data + test_parity + test_stop
	printer = Tcl(test_comm)
	if printer.comm.get() != test_comm:
		print("Error: wrong communication data; expected '" + test_comm + "'; actual '" + printer.comm.get() + "'")

	############################
	def TestStatus(flags, expectedMessage, lastTemplate):
		test_status = "*S|0|GURUSAG18|" + flags + "|P" + lastTemplate + "|*"
		printer.UpdateStatus(test_status)
		printer.UpdateMessage()
		if printer.status != test_status:
			print("Error: wrong status; expected '" + test_status + "'; actual '" + printer.status)
		if printer.lastTemplate != lastTemplate:
			print("Error: Didn't detect last template from P" + lastTemplate + "; found '" + printer.lastTemplate + "'")
		if printer.message.get() != expectedMessage:
			print("Error: Wrong message for " + flags + ": found '" + printer.message.get() + "'; expected '" + expectedMessage + "'")
		return

	test_flags = "P|@|@|@|A"
	test_message = "Generic error"
	test_template = "x"
	TestStatus(test_flags, test_message, test_template)
	if not printer.error:
		print("Error: should have found an error for " + test_flags)
	if not printer.powerUp:
		print("Error: should have detected Power Up for " + test_flags)

	#----------------
	test_flags = "@|@|@|@|@"
	test_message = "Ready to print, no previous errors"
	test_template = "#8000"
	TestStatus(test_flags, test_message, test_template)
	if printer.error:
		print("Error: should not have found an error for " + test_flags)

	test_flags = "P|P|@|@|@"
	test_message = "Ready to print, a previous error (unknown library)"
	test_template = "0"
	TestStatus(test_flags, test_message, test_template)
	if not printer.error:
		print("Error: should have found an error for " + test_flags)
	if not printer.error:
		print("Error: should have found an error for " + test_flags)
	if not printer.systemError:
		print("Error: should have detected System Error for " + test_flags)
	if not printer.libraryRefError:
		print("Error: should have detected Library Reference Error for " + test_flags)

	test_flags = "X|@|@|@|@"
	test_message = "Print head is up"
	test_template = "0"
	TestStatus(test_flags, test_message, test_template)
	if not printer.error:
		print("Error: should have found an error for " + test_flags)
	if not printer.drawerOpen:
		print("Error: should have detected Drawer Open for " + test_flags)
	#

	test_flags = "T|@|@|@|@"
	test_message = "Paper is out"
	test_template = "0"
	TestStatus(test_flags, test_message, test_template)
	if not printer.error:
		print("Error: should have found an error for " + test_flags)
	if not printer.paperOut:
		print("Error: should have detected Paper Out for " + test_flags)
	#

	test_flags = "`|@|@|@|@"
	test_message = "Loading new font into memory"
	test_template = "0"
	TestStatus(test_flags, test_message, test_template)
	if printer.error:
		print("Error: should not have found an error for " + test_flags)
	if not printer.busy:
		print("Error: should have detected Printer Busy for " + test_flags)
	#

	test_flags = "P|H|@|@|@"
	test_message = "Improper batch data in one of the Print Regions"
	test_template = "0"
	TestStatus(test_flags, test_message, test_template)
	if not printer.error:
		print("Error: should have found an error for " + test_flags)
	if not printer.prDataError:
		print("Error: should have detected PR data error for " + test_flags)
	#

	test_flags = "q|@|@|@|@"
	test_message = "Power supply error while printing"
	test_template = "0"
	TestStatus(test_flags, test_message, test_template)
	if not printer.error:
		print("Error: should have found an error for " + test_flags)
	if not printer.busy:
		print("Error: should have detected Printer Busy for " + test_flags)
	if not printer.voltageError:
		print("Error: should have detected Voltage Error for " + test_flags)
	#

	test_flags = "P|@|A|@|@"
	test_message = "Cannot find supply index mark"
	test_template = "0"
	TestStatus(test_flags, test_message, test_template)
	if not printer.error:
		print("Error: should have found an error for " + test_flags)
	if not printer.missingSupplyIndex:
		print("Error: should have detected Missing Supply Index for " + test_flags)
	#

	test_flags = "P|F|@|@|@"
	test_message = "Memory overflow"
	test_template = "0"
	TestStatus(test_flags, test_message, test_template)
	if not printer.error:
		print("Error: should have found an error for " + test_flags)
	if not printer.systemError:
		print("Error: should have detected System Error for " + test_flags)
	if not printer.bufferOverflow:
		print("Error: should have detected Buffer Overflow for " + test_flags)
	if not printer.libraryLoadError:
		print("Error: should have detected Library Load Error for " + test_flags)
	#

	test_flags = "@|@|H|@|@"
	test_message = "Paper in the chute"
	test_template = "0"
	TestStatus(test_flags, test_message, test_template)
	if printer.error:
		print("Error: should not have found an error for " + test_flags)
	if not printer.paperInChute:
		print("Error: should have detected Paper in Chute for " + test_flags)
	#

	print("End of test")
