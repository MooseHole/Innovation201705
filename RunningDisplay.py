from tkinter import *

from DeviceInterface import DeviceType

class RunningDisplay():
    def __init__(self):
        self.win = Tk()
    @staticmethod
    def __addLabel(frame, lab, text, index):
        Label(frame, text=lab).grid(row=index, column=0, sticky=W)
        name = Entry(frame, textvariable=text, state='readonly')
        name.grid(row=index, column=1, sticky=W)
        return index + 1
    def SetDevice(self, device):
        self.__frame1 = Frame(self.win)
        self.__frame1.pack()
        curIndex = 0
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
        self.win.destroy()
    def UpdateRXStatus(self, isConnected):
        if isConnected:
            self.__rxStatus = Button(self.__frame1, text="       ", state=DISABLED, bg="green").grid(row=self.__rxCol, column=1, sticky=W)
        else:
            self.__rxStatus = Button(self.__frame1, text="       ", state=DISABLED, bg="red").grid(row=self.__rxCol, column=1, sticky=W)
    def UpdateTXStatus(self, isConnected):
        if isConnected:
            self.__txStatus = Button(self.__frame1, text="       ", state=DISABLED, bg="green").grid(row=self.__txCol, column=1, sticky=W)
        else:
            self.__txStatus = Button(self.__frame1, text="       ", state=DISABLED, bg="red").grid(row=self.__txCol, column=1, sticky=W)
    def runLoop(self):
        self.win.update_idletasks()
        self.win.update()
