# coding: utf-8
'''
Communicate with resistor
Ex) read resistor's ID, set ohm.

TODO:
    implement each functions.
    make docstrings about each functions.
'''

class Resistor(object):
    def __init__(self, devname: str):
        self.DEVNAME = devname
        self.statusRes = self.openComm()
    def __del__(self):
        self.endComm()

    def openComm(self):
        return True


    def endComm(self):
        pass


    def setRes(self, ohm: float):
        pass


    def readId(self):
        data = ['Maker', 'Model', 'S/N']
        return data
