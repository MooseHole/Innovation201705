from tkinter import *

import queue
from DeviceInterface import DeviceType

class RunningDisplay():
    def __init__(self):
        self.items = {}
        self.RXisConnected = False
        self.TXisConnected = False
        self.rxQueue = queue.Queue()
        self.txQueue = queue.Queue()
        self.win = Tk()
        self.running = True
    def __addLabel(self, frame, lab, text, index):
        Label(frame, text=lab).grid(row=index, column=0, sticky=W)
        self.items[lab] = StringVar(value=text)
        name = Entry(frame, textvariable=self.items[lab], state='readonly')
        name.grid(row=index, column=1, sticky=W)
        return index + 1
    def SetDevice(self, device):
        self.__frame1 = Frame(self.win)
        self.__frame1.pack()
        curIndex = 0
        self.device = device
        for lab, text in device.GetLabels().items():
            curIndex = self.__addLabel(self.__frame1, lab, text, curIndex)
        self.__rxCol = curIndex
        self.__txCol = curIndex + 1
        Label(self.__frame1, text="RX").grid(row=self.__rxCol, column=0, sticky=W)
        self.__rxStatus = Button(self.__frame1, text="       ", state=DISABLED, bg="red").grid(row=self.__rxCol, column=1, sticky=W)
        Label(self.__frame1, text="TX").grid(row=self.__txCol, column=0, sticky=W)
        self.__txStatus = Button(self.__frame1, text="       ", state=DISABLED, bg="red").grid(row=self.__txCol, column=1, sticky=W)
        self.win.protocol("WM_DELETE_WINDOW", self.onClose)
    def onClose(self):
        self.running = False
        self.win.destroy()
    def UpdateRXStatus(self, isConnected):
        if self.RXisConnected == isConnected:
            return

        self.RXisConnected = isConnected
        self.rxQueue.put(isConnected)
    def UpdateTXStatus(self, isConnected):
        if self.TXisConnected == isConnected:
            return

        self.isConnected = isConnected
        self.txQueue.put(isConnected)
    def __handleGUIRefresh(self):
        for lab, text in self.device.GetLabels().items():
            self.items[lab].set(text)
    def __UpdateButtonTX(self, isConnected):
        if isConnected:
            self.__txStatus = Button(self.__frame1, text="       ", state=DISABLED, bg="green").grid(row=self.__txCol, column=1, sticky=W)
        else:
            self.__txStatus = Button(self.__frame1, text="       ", state=DISABLED, bg="red").grid(row=self.__txCol, column=1, sticky=W)
    def __UpdateButtonRX(self, isConnected):
        if isConnected:
            self.__rxStatus = Button(self.__frame1, text="       ", state=DISABLED, bg="green").grid(row=self.__rxCol, column=1, sticky=W)
        else:
            self.__rxStatus = Button(self.__frame1, text="       ", state=DISABLED, bg="red").grid(row=self.__rxCol, column=1, sticky=W)
    def runLoop(self):
        if self.running:
            while not self.txQueue.empty():
                self.__UpdateButtonTX(self.txQueue.get())
            while not self.rxQueue.empty():
                self.__UpdateButtonRX(self.rxQueue.get())
            self.__handleGUIRefresh()
            self.win.update_idletasks()
            self.win.update()
