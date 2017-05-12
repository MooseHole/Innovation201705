import time
from tkinter import *

from DeviceInterface import DynamicDevice
from RunningDisplay import RunningDisplay

myFiles = RunningDisplay()

props = {"PrinterType": StringVar(value="Unknown"),
         "Firmware": StringVar(value="Unknown"),
         "Com": StringVar(value="NA NA NA"),
         "PaperStatus": StringVar(value="NA"),
         "Status": StringVar(value="Unknown")}

def randStatusUpdate(oldepoch):
    return false

"""    return time.time() - oldepoch >= 10 """

p = DynamicDevice(props)
myFiles.SetDevice(p)

lastTime = time.time()
lastRX = False
lastTX = False

def statusUpdate(data)
    for item in data:
        props[item] = data[item]

while TRUE:
    myFiles.runLoop()
	
    if randStatusUpdate(lastTime):
        lastTime = time.time()
        myFiles.UpdateRXStatus(~lastRX)
        lastRX = ~lastRX
        myFiles.UpdateTXStatus(~lastTX)
        lastTX = ~lastTX
		
        if lastTX:
            p.Status.set("OK")
            p.PrinterType.set("New Type")
            p.Firmware.set("New Firmware")
        else:
            p.Status.set("BAD")
            p.PrinterType.set("UnKnown")
            p.Firmware.set("UnKnown")
