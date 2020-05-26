# coding: utf-8
'''
Communicate with checker MCU.
Ex) send some message, connect to MCU, ...

TODO:
    No item.
'''
# import from std
import sys
import time
# import from pypi
import serial
import serial.tools.list_ports
# import from selfmade
import src.serBitAssign as ba

# devName = 'Serial Port'
# br = 9600
# secTimeOut = 0.1

class Serial2Mcu(object):
    '''
    Communicate with checker MCU.

    Attributes
    ----------
    devname: str
        device name.
    boudrate: int
        boudrate of serial communication
    timeout: float
        wait time for response from MCU.
    port: object
        serial.Serial()
    '''
    def __init__(self):
        self.devname = 'Serial Port'
        self.boudrate = 9600
        self.timeout = 0.1
        self.port = self.openSeriPort()

    def __del__(self):
        self.closeSeriPort()

    def _seachCOMPort(self, devname: str) -> str:
        """
        Search number of COM port from device name

        Parameters
        ----------
            devname: str
                device name
        Returns
        ----------
            str
                COM port
        """
        # make list of all device name at each com ports
        ports = serial.tools.list_ports.comports()
        device = [info for info in ports if devname in info.description]
        # return
        if len(device) == 0:
            return None
        try:
            return str(serial.Serial(device[0].device).port)
        except:
            return None

    def openSeriPort(self) -> object:
        """
        open serial port about COM port

        Parameters
        ----------
            Nothing
        Returns
        ----------
            port: object
                Serial
        """
        # open port
        port_str = self._seachCOMPort(self.devname)
        if port_str is None:
            return None
        # setup serial comm
        ser = serial.Serial(port_str)
        try:
            ser.boudrate = self.boudrate
            ser.timeout = self.timeout
            # wait 2 sec
            time.sleep(3)
            # check port open already
            ser.isOpen()
        except:
            ser.close()
            ser.open()
        # comm check
        self.emptySeriBuf(ser)
        # rx = self.sendMsg(ba.chkComm, 0.1)
        # return port if rx==ba.chkComm else None
        return ser

    def emptySeriBuf(self, ser: object) -> None:
        """
        read serial buffer and set empty

        Parameters
        ----------
            Nothing

        Returns
        ----------
            Nothing
        """
        _ = ser.readline() # unused serial comm
        return

    def sendMsg(self, msg: str, waittime: float) -> str:
        """
        send message and receive return message

        Parameters
        ----------
            port: object
                Serial
            msg: str
                message for checker (only from bit assign)
            waittime: float
                time out second
        Returns
        ----------
            rx: str
                return message from checker
        """
        # check input
        if msg[0:2].isdecimal() and int(msg[0:2])<100:
            # only decimal, 0~99
            tx = msg
        else:
            print('Error : Serial Message header is only decimal in 0~99.')
            return None
        # comm
        # send msg as string
        self.port.write(tx.encode('utf-8'))
        # waiting rx
        start = time.time()
        elapsedTime = 0
        while elapsedTime<10:
            # read rx
            rxRaw = self.port.readline()
            # convert rx from bytes to string
            rx = ''.join(rxRaw.decode('utf-8').splitlines())
            if rx !='':
                return rx
            time.sleep(waittime)
            elapsedTime = time.time()-start
        if elapsedTime >= 10:
            return 'timeout'

    def sendAddInfo(self, sermsg: str, addmsg: str, waittime: float):
        """
        send additional message to checkers

        Parameters
        ----------
            port: object
                Serial
            sermsg: str
                message to checker (only from bit assign)
            addmsg: str
                additional message (not only from bit assign)
        Returns
        ----------
            rx: str
                return message from checker
        """
        # comm
        rx = self.sendMsg(sermsg, waittime)
        if rx == 'timeout':
            return 'order send error'
        if rx != ba.posRes:
            return 'additional info send error'
        else:
            # send msg as string
            self.port.write(addmsg.encode('utf-8'))
            # waiting rx
            start = time.time()
            elapsedTime = 0
            while elapsedTime<5:
                # read rx
                rxRaw = self.port.readline()
                # convert rx from bytes to string
                rx = ''.join(rxRaw.decode('utf-8').splitlines())
                if rx !='':
                    return rx
                time.sleep(waittime)
                elapsedTime = time.time()-start
            if elapsedTime >= 5:
                return 'timeout'

    def closeSeriPort(self) -> object:
        """
        Close serial port

        Parameters
        ----------
            Nothing

        Returns
        ----------
            ser: object
                Serial
        """
        if self.port is not None:
            self.port.close()
            self.port = None
        return self.port


class Serial2Mcu_Manual(Serial2Mcu):
    '''
    Communicate with checker MCU only for Manual Set Tub.

    Attributes
    ----------
    devname: str
        device name.
    boudrate: int
        boudrate of serial communication
    timeout: float
        wait time for response from MCU.
    port: object
        serial.Serial()
        Initial value = None
    '''
    def __init__(self):
        self.devname = 'Serial Port'
        self.boudrate = 9600
        self.timeout = 0.1
        # self.port = self.openSeriPort()
        self.port = None
    def __del__(self):
        self.closeSeriPort()

'''
----------
main
----------
'''
if __name__ == '__main__':
    pass
