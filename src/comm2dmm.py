# coding: utf-8
'''
Communicate with DMM.
Ex) read DMM's ID, measure each item, ...

TODO:
    if need, enable to function 'openComm()''s comment out.
'''
# import from std
import sys
sys.path.append('./')
import time
import ctypes as c

if sys.maxsize > 2 ** 32:
    ausb = c.windll.LoadLibrary('./lib/adcmt/x64/ausb.dll')
else:
    ausb = c.windll.LoadLibrary('./lib/adcmt/x86/ausb.dll')
clib = c.cdll.msvcrt

class DmmADCMT(object):
    '''
    Communicate with DMM.

    Attributes
    ----------
    USBID: int
        equal to DMM's setup
    hDev: ctypes.c_uint32
        usb handle
    '''
    def __init__(self, usbid=1):
        self.USBID = usbid
        self.hDev = self.openComm()
    def __del__(self):
        self.endComm()


    def openComm(self):
        """
        Start and open comm to DMM

        Parameters
        ----------
            Nothing
        Returns
        ----------
            hDev: ctypes.c_uint32
                usb handle
        """
        # variables
        TIMEOUT = 3
        dwTmout = c.c_uint32(TIMEOUT)
        dwMyid = c.c_uint32(self.USBID)
        hDev = c.c_uint32()
        # usb open
        res = ausb.ausb_start(dwTmout)
        if res != 0:
            return 1
        try:
            ausb.ausb_open(c.pointer(hDev), dwMyid)
            # _sendCommand('*RST') # reset
            # _sendCommand('OID0') # set read id to new method (only 7461A)
            # self._sendCommand('H0') # set output to no header
            # _sendCommand('IMP0') # set input Impedance to HiZ (only 7461A)
        except:
            print('cannot usb open.')
            return 1
        return hDev


    def endComm(self) -> int:
        """
        Close and end comm to DMM

        Parameters
        ----------
            Nothing

        Returns
        ----------
            int
                0: success, 1:irregular
        """
        # usb close
        try:
            ausb.ausb_close(self.hDev)
            ausb.ausb_end()
        except:
            print('cannot usb close.')
            return 1
        return 0


    def _sendCommand(self, msg: str):
        """
        [private] ausb write
        Parameters
        ----------
            msg: str
                message
        Returns
        ----------
            dwSize: ctypes.c_uint32
                size of send message
        """
        # declaration
        ausb.ausb_write.restype = c.c_uint32
        ausb.ausb_write.argtype = (c.c_uint32, c.c_void_p, c.c_uint32)
        wrtBuf = c.create_string_buffer(50)
        dwSize = c.c_uint32()
        # send message
        try:
            clib.strcpy_s(wrtBuf, 50, msg.encode('ascii'))
            dwSize = c.c_uint32(clib.strlen(wrtBuf))
            res = ausb.ausb_write(self.hDev, wrtBuf, dwSize)
        except:
            print('cannot send message.')
            return 1
        # return
        return dwSize if res==0 else 1


    def _readData(self, dwSize) -> str:
        """
        [private] ausb read

        Parameters
        ----------
            dwSize: str
                size of send message
        Returns
        ----------
            str_meas: str
                measurement value
        """
        # declaration
        ausb.ausb_read.restype = c.c_uint32
        ausb.ausb_read.argtype = (c.c_uint32, c.c_void_p, c.c_uint32, c.c_uint32)
        rdBuf = c.create_string_buffer(64)
        # read data
        p_dwSize = c.pointer(dwSize)
        try:
            res = ausb.ausb_read(self.hDev, rdBuf, c.c_uint32(64), p_dwSize)
        except:
            print('cannot read data.')
            return 1
        # return
        str_meas = rdBuf.value.decode('utf-8').rstrip()
        return str_meas if res==0 else 1


    def measOhm(self) -> float:
        """
        Measure Resistance (auto range)
        Parameters
        ----------
            Nothing

        Returns
        ----------
            float_meas: float
                measurement value
        """
        dwSize = self._sendCommand('F3')
        dwSize = self._sendCommand('R0')
        time.sleep(0.05)
        result = self._readData(dwSize)
        float_meas = float(result)
        return float_meas


    def measDCI(self):
        """
        Measure Current (auto range)

        Parameters
        ----------
            Nothing

        Returns
        ----------
            result: float
                measurement value
        """
        dwSize = self._sendCommand('F5')
        dwSize = self._sendCommand('R0')
        time.sleep(0.05)
        result = self._readData(dwSize)
        float_meas = float(result)
        return float_meas


    def measDCV(self):
        """
        Measure Voltage (auto range)

        Parameters
        ----------
            Nothing
        Returns
        ----------
            result: float
                measurement value
        """
        dwSize = self._sendCommand('F1')
        dwSize = self._sendCommand('R0')
        time.sleep(0.05)
        result = self._readData(dwSize)
        float_meas = float(result)
        return float_meas


    def readId(self):
        """
        Read DMM's ID

        Parameters
        ----------
            Nothing
        Returns
        ----------
            result: list
                0: maker, 1: model, 2: S/N, 3: softversion
        """
        # send message
        dwSize = self._sendCommand('*IDN?')
        result = self._readData(dwSize).split(',')
        # return
        return result

"""
----------
main
----------
"""
if __name__ == '__main__':
    pass
