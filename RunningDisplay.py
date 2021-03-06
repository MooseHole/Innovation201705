from tkinter import *
import tkinter.font as tkFont

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
        self.win.attributes("-fullscreen", True)
        self.cusFont = tkFont.Font(family="Helvetica", size=30)
        self.running = True
    def __addLabel(self, frame, lab, text, index):
        Label(frame, text=lab, font=self.cusFont).grid(row=index, column=0, sticky=N+S+E+W)
        self.items[lab] = StringVar(value=text)
        name = Entry(frame, textvariable=self.items[lab], state='readonly', font=self.cusFont)
        name.grid(row=index, column=1, sticky=N+S+E+W)
        Grid.columnconfigure(frame, 0, weight=1)
        Grid.columnconfigure(frame, 1, weight=1)
        Grid.rowconfigure(frame, index, weight=1)
        return index + 1
    def SetDevice(self, device):
        self.__frame1 = Frame(self.win)
        self.__frame1.pack(side="top", fill="both", expand=True)
        curIndex = 0
        self.device = device
        for lab, text in device.GetLabels().items():
            curIndex = self.__addLabel(self.__frame1, lab, text, curIndex)
        self.__rxCol = curIndex
        self.__txCol = curIndex + 1
        Grid.columnconfigure(self.__frame1, 0, weight=1)
        Grid.columnconfigure(self.__frame1, 1, weight=1)
        Grid.rowconfigure(self.__frame1, self.__txCol, weight=1)
        Grid.rowconfigure(self.__frame1, self.__rxCol, weight=1)
        Label(self.__frame1, text="RX", font=self.cusFont).grid(row=self.__rxCol, column=0, sticky=N+S+E+W)
        self.__rxStatus = Button(self.__frame1, text="       ", state=DISABLED, bg="red")
        self.__rxStatus.grid(row=self.__rxCol, column=1, sticky=N+S+E+W)
        Label(self.__frame1, text="TX", font=self.cusFont).grid(row=self.__txCol, column=0, sticky=N+S+E+W)
        self.__txStatus = Button(self.__frame1, text="       ", state=DISABLED, bg="red")
        self.__txStatus.grid(row=self.__txCol, column=1, sticky=N+S+E+W)
        self.win.protocol("WM_DELETE_WINDOW", self.onClose)
    def onClose(self):
        self.running = False
        self.win.destroy()
    def UpdateRXStatus(self, isConnected):
        if self.RXisConnected == isConnected:
            return

        self.RXisConnected = isConnected
        #self.__UpdateButtonRX(isConnected)
        self.rxQueue.put(isConnected)
    def UpdateTXStatus(self, isConnected):
        if self.TXisConnected == isConnected:
            return

        self.isConnected = isConnected
        #self.__UpdateButtonTX(isConnected)
        self.txQueue.put(isConnected)
    def __handleGUIRefresh(self):
        for lab, text in self.device.GetLabels().items():
            self.items[lab].set(text)
    def __UpdateButtonTX(self, isConnected):
        if isConnected:
            self.__txStatus.configure(bg="green")
        else:
            self.__txStatus.configure(bg="red")
    def __UpdateButtonRX(self, isConnected):
        if isConnected:
            self.__rxStatus.configure(bg="green")
        else:
            self.__rxStatus.configure(bg="red")
    def runLoop(self):
        if self.running:
            while not self.txQueue.empty():
                self.__UpdateButtonTX(self.txQueue.get(False))
            while not self.rxQueue.empty():
                self.__UpdateButtonRX(self.rxQueue.get(False))
            self.__handleGUIRefresh()
            self.win.update_idletasks()
            self.win.update()
