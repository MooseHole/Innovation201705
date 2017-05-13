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
    return False

"""    return time.time() - oldepoch >= 10 """

lastTime = time.time()
lastRX = False
lastTX = False

def statusUpdate(data):
    for item in data:
        props[item] = data[item]
