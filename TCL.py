from tkinter import *
from RunningDisplay import RunningDisplay
from DeviceInterface import DeviceType

# A printer supporting the TCL (Thermal Control Language) protocol
class Tcl(DeviceType):
	# Constructor
	# comm = communication parameters formatted like 9600 8N1 (speed; data bits; parity; stop bits)
	# status (optional) = Initial status (see UpdateStatus)
	def __init__(self, comm, status=""):
		self.comm = StringVar(value = comm)
		self.status = StringVar(value = status)
		self.fversion = StringVar(value = "")
		self.lastTemplate = StringVar(value = "")
		self.message = StringVar(value = "")

		self.ResetErrors()

		if status != "":
			self.UpdateStatus(status)
			self.UpdateMessage()

	def Update(self, message):
		self.UpdateStatus(status)
		self.UpdateMessage()
		#statusUpdate(self.GetLabels())

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

	def GetLabels(self):
		return {"Message":self.message, "Com":self.comm, "Status":self.status}

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
				self.message.set("Ready to print, a previous error (unknown library)")
			elif self.drawerOpen:
				self.message.set("Print head is up")
			elif self.paperOut:
				self.message.set("Paper is out")
			elif self.prDataError:
				self.message.set("Improper batch data in one of the Print Regions")
			elif self.busy and self.voltageError:
				self.message.set("Power supply error while printing")
			elif self.missingSupplyIndex:
				self.message.set("Cannot find supply index mark")
			elif self.bufferOverflow:
				if self.libraryLoadError:
					self.message.set("Memory overflow")
				else:
					self.message.set("Communications buffer overflow")
			elif self.prDataError:
				self.message.set("Data within a Print Region was truncated")
			elif self.headError:
				self.message.set("Bad connection with the print head")
			elif self.commandError:
				self.message.set("Garbled or unrecognized command was received")
			else:
				self.message.set("Generic error")
		else:
			if self.paperInChute:
				self.message.set("Paper in the chute")
			elif self.busy:
				self.message.set("Loading new font into memory")
			else:
				self.message.set("Ready to print, no previous errors")

	def DecodeVersion(self, fversion):
		self.fversion = fversion
