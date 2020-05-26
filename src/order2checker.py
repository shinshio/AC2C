# coding: utf-8
'''
Order to checker.
Ex) set relay on/off, wait some seconds, ...

TODO:
    make class?
'''
# import from std
import os
import sys
sys.path.append('./')
import time
import math
# import from selfmade
import src.comm2checker
import src.serBitAssign as ba


INI_FILE_PATH = './settings/initial_ohm_setting.ini'
INIT_OHM = {'OPEN':0.0, 'SHORT':10.0, '+B-LEAK':5000.0, 'GND-LEAK':5000.0}


def odrIGON(recipe: list, mcu: object) -> str:
    """
    Order IGON to checker

    Parameters
    ----------
        recipe: list
            0: IGON
            1: None
        mcu: object
            comm2checker.Serial2Mcu

    Returns
    ----------
        str
            message from checker
    """
    return mcu.sendMsg(ba.igOn, 0.1)

def odrIGOFF(recipe: list, mcu: object) -> str:
    """
    Order IGOFF to checker

    Parameters
    ----------
        recipe: list
            0: IGOFF
            1: None
        mcu: object
            comm2checker.Serial2Mcu

    Returns
    ----------
        str
            message from checker
    """
    return mcu.sendMsg(ba.igOff, 0.1)

def odrRYON(recipe: list, mcu: object) -> str:
    """
    Order Relay On to checker

    Parameters
    ----------
        recipe: list
            0: RYON
            1-end: relay numbers
        mcu: object
            comm2checker.Serial2Mcu

    Returns
    ----------
        str
            message from checker
    """
    rx = [None for _ in range(len(recipe))]
    for i in range(len(recipe)-1):
        odr = recipe[i+1]
        ch = odr[0:2]
        rx[i] = mcu.sendMsg(ba.ryOn + ch, 0.1)
    if rx.count(ba.posRes)==len(recipe)-1:
        return ba.posRes
    else:
        return ba.negRes

def odrRYOFF(recipe: list, mcu: object) -> str:
    """
    Order Relay Off to checker

    Parameters
    ----------
        recipe: list
            0: RYOFF
            1-end: relay numbers
        mcu: object
            comm2checker.Serial2Mcu

    Returns
    ----------
        str
            message from checker
    """
    rx = [None for _ in range(len(recipe))]
    for i in range(len(recipe)-1):
        odr = recipe[i+1]
        ch = odr[0:2]
        rx[i] = mcu.sendMsg(ba.ryOff + ch, 0.1)
    if rx.count(ba.posRes)==len(recipe)-1:
        return ba.posRes
    else:
        return ba.negRes

def odrRYDEF(recipe: list, mcu: object) -> str:
    """
    Order Relay to default to checker

    Parameters
    ----------
        recipe: list
            0: RYDEF
            1: None
        mcu: object
            comm2checker.Serial2Mcu

    Returns
    ----------
        str
            message from checker
    """
    if mcu.sendMsg(ba.ryDef ,0.1) != ba.posRes:
        return ba.negRes
    else:
        return ba.posRes

def odrRYALLOFF(recipe: list, mcu: object) -> str:
    """
    Order All Relays Off to checker

    Parameters
    ----------
        recipe: list
            0: RYALLOFF
            1: None
        mcu: object
            comm2checker.Serial2Mcu

    Returns
    ----------
        str
            message from checker
    """
    if mcu.sendMsg(ba.ryAllOff ,0.1) != ba.posRes:
        return ba.negRes
    return mcu.sendMsg(ba.ryAllOff, 0.1)

def _cnvCanRct(receipt: str) -> str:
    """
    [private]
    Extract only responce message(s) from CAN responce messages with comma

    Parameters
    ----------
        receipt: str
            all CAN message(s)

    Returns
    ----------
        receipt / receipt_new: str
            only necessary message
    """
    receipt_new = ''
    _receipt_new = ''
    _receipt_list = []
    receipt_list = []
    receipt_list = [s.split(' ') for s in receipt.split(',')]
    # when receive only 1 msg (= negRes)
    if len(receipt_list)==1:
        return receipt
    # when receive 2 msgs (= 1 DTC or DTC clear w/o pending)
    if len(receipt_list)==2:
        if receipt_list[0][1] == '54':
            # DTC CLEAR: ok, and no pending
            receipt_new = '54'
            return receipt_new
        else:
            # DTC READ: only 1 dtc
            receipt_new = receipt_list[0][4] + receipt_list[0][5] + receipt_list[0][6] + receipt_list[0][7]
            return receipt_new
    # when receive 3 or more msgs (= 2 or more DTCs or DTC clear w/ pending)
    if receipt_list[0][0][0:1] != '1':
        # DTC CLEAR: after pending
        receipt_new = receipt_list[1][1]
        return receipt_new
    else:
        # DTC READ: 2 and more dtcs
        for i in range(len(receipt_list)):
            if i==0:
                del receipt_list[i][0:5]
                _receipt_new = _receipt_new + ''.join(receipt_list[i])
            else:
                del receipt_list[i][0]
                _receipt_new = _receipt_new + ''.join(receipt_list[i])
        _receipt_list = [_receipt_new.strip('aa')[i:i+8] for i in range(0,len(_receipt_new),8)]
        _receipt_list = [a for a in _receipt_list if a != '']
        receipt_new = ','.join(_receipt_list)
        return receipt_new

def odrCAN(recipe: list, mcu: object) -> str:
    """
    Order to checker, send CAN message to ECU

    Parameters
    ----------
        recipe: list
            0: CAN
            1: DTCREAD, DTCCLEAR
        mcu: object
            comm2checker.Serial2Mcu

    Returns
    ----------
        str
            converted CAN message(s)
    """
    odr = recipe[1]
    if odr=='DTCREAD':
        receipt = mcu.sendMsg(ba.canDtcRead, 2)
    elif odr=='DTCCLEAR':
        receipt = mcu.sendMsg(ba.canDtcClear, 2)
    return _cnvCanRct(receipt)

def odrWAIT(recipe: list, mcu: object) -> str:
    """
    Order WAIT some seconds to checker

    Parameters
    ----------
        recipe: list
            0: WAIT
            1: wait time (seconds * 10) at str (max: 9.9sec)
        mcu: object
            comm2checker.Serial2Mcu

    Returns
    ----------
        str
            message from checker
    """
    wtSec = str(recipe[1])
    elapse = mcu.sendMsg(ba.waitSec + wtSec, 0.1)
    receipt = str(round(float(elapse)/1000.0,1))
    return receipt

def odrMeasAmpere(recipe: list, mcu: object, dmm: object) -> float:
    """
    Order measurement DCI to checker and DMM

    Parameters
    ----------
        recipe: list
            0: MEASA
            1: None
        mcu: object
            comm2checker.Serial2Mcu
        dmm: object
            comm2dmm.DmmADC

    Returns
    ----------
        amp: float
            measurement result
    """
    if dmm.hDev==1:
        return 'error'
    if _setDmmMode('amp', mcu) != ba.posRes:
        return ba.negRes
    time.sleep(0.5)
    amp = dmm.measDCI()
    if _setDmmMode('default', mcu) != ba.posRes:
        return ba.negRes
    return amp

# TODO: after MCU soft update about bitassign, unset comment of _set***Mode
def odrMeasOhm(recipe: list, mcu: object, dmm: object) -> float:
    """
    Order measurement OHM to checker and DMM

    Parameters
    ----------
        recipe: list
            0: MEASR
            1: relay number
        mcu: object
            comm2checker.Serial2Mcu
        dmm: object
            order2dmm.DmmADC

    Returns
    ----------
        ohm: float
            measurement result
    """
    if dmm.hDev==1:
        return 'error'
    if _setDmmMode('res', mcu) != ba.posRes:
        return ba.negRes
    if _setResMode('OPEN', mcu) != ba.posRes:
        return ba.negRes
    if order2checker(['RYON', recipe[1]], mcu) != ba.posRes:
        return ba.negRes
    time.sleep(0.5)
    meas = dmm.measOhm()
    ohm = round(meas, 2)
    if order2checker(['RYOFF', recipe[1]], mcu) != ba.posRes:
        return ba.negRes
    if _setDmmMode('default', mcu) != ba.posRes:
        return ba.negRes
    return ohm

def odrLevelingOhm(
        recipe: list,
        mcu: object,
        res: object,
        boxRes: list
    ) -> float:
    """
    Order Leveling Ohm to checker and Resistor

    Parameters
    ----------
        recipe: list
            0: LEVEL-(timing)-(mode)
            1: relay number
            2: dtc
        mcu: object
            comm2checker.Serial2Mcu
        res: object
            comm2resistor.Res
        boxRes:
            box's each SQ ohms

    Returns
    ----------
        receipt: float
            ohm at detected dtc
    """
    if res.statusRes==False:
        return 'error'
    # take in recipe
    timing = recipe[0][6:10]
    mode = recipe[0][11:]
    rNum = recipe[1]
    dtc = recipe[2]
    # take in initial ohm
    initOhm = INIT_OHM.copy()
    if os.path.exists(INI_FILE_PATH):
        with open(INI_FILE_PATH, 'rb') as ini:
            line = ini.readline().decode('utf-8')
            if line.split('=')[0] == mode:
                initOhm[mode] = float(line.split('=')[1].strip(' '))
    else:
        return 'error'
    # set relay
    if _setResMode(mode, mcu) == ba.negRes:
        return 'set res mode error'
    _ = odrRYON(['RYON', rNum], mcu)
    # main
    count = 0
    ohm = initOhm[mode]
    digit = int(math.log10(ohm))
    receipt = 0.0
    while count<50:
        _ = odrCAN(['CAN', 'DTCCLEAR'], mcu)
        # if initial, igoff and igon
        if timing == 'INIT':
            _ = odrIGOFF(['IGOFF',], mcu)
            _ = odrWAIT(['WAIT', 30], mcu)
            _ = odrIGON(['IGON',], mcu)
            _ = odrWAIT(['WAIT', 80], mcu)
        # set resistor
        res.setRes(ohm)
        # check dtc
        _ = odrWAIT(['WAIT', 25], mcu)
        dtcread = odrCAN(['CAN', 'DTCREAD'], mcu)
        if dtc in dtcread:
            # if detect dtc, down digit
            receipt = ohm
            if digit < -2:
                break
            else:
                if mode=='OPEN':
                    ohm = (ohm - 1 * (10**digit)) + 1 * (10**(digit-1))
                    digit -= 1
                else:
                    digit -= 1
                    ohm = (ohm + 9 * (10**digit))
        else:
            # if not detect dtc, down ohm of this digit
            ohm = (ohm - 1 * (10**digit)) if not mode == 'OPEN' else (ohm + 1 * (10**digit))
        # levelize
        if ohm <= 0:
            return 'no detected.'
        count += 1
    else:
        return 'timeout (over 50 times)'
    # undo relay
    _ = odrRYOFF(['RYOFF', rNum])
    _ = _setResMode('default', mcu)
    # dtc clear
    _ = odrCAN(['CAN', 'DTCCLEAR'], mcu)
    # return
    if mode=='OPEN' or mode=='SHORT':
        int_rNum = int(rNum, 16) - 8
        receipt = receipt + boxRes[int_rNum-1]
    return str(receipt)

def _setDmmMode(mode: str, mcu: object) -> str:
    """
    [private] Set relay to each DMM mode

    Parameters
    ----------
        mode: str
            default, amp, res
        mcu: object
            comm2checker.Serial2Mcu

    Returns
    ----------
        str
            message from checker
    """
    if mode == 'default':
        receipt = mcu.sendMsg(ba.dmmDefault, 0.1)
    elif mode == 'amp':
        receipt = mcu.sendMsg(ba.dmmAmpereMode, 0.1)
    elif mode == 'res':
        receipt = mcu.sendMsg(ba.dmmResistorMode, 0.1)
    if receipt == ba.posRes:
        return receipt
    else:
        return ba.negRes

def _setResMode(mode: str, mcu: object) -> str:
    """
    [private] Set relay to each Resistor mode

    Parameters
    ----------
        mode: str
            default, +B-LEAK, GND-LEAK, OPEN, SHORT
        mcu: object
            comm2checker.Serial2Mcu

    Returns
    ----------
        str
            message from checker
    """
    if mode == 'default':
        receipt = mcu.sendMsg(ba.resDefault, 0.1)
    if mode == '+B-LEAK':
        receipt = mcu.sendMsg(ba.resBleakMode, 0.1)
    elif mode == 'GND-LEAK':
        receipt = mcu.sendMsg(ba.resGNDleakMode, 0.1)
    elif mode == 'OPEN' or mode == 'SHORT':
        receipt = mcu.sendMsg(ba.resOpenMode, 0.1)
    else:
        receipt = ba.negRes
    if receipt == ba.posRes:
        return receipt
    else:
        return ba.negRes

def order2checker(
        recipe: list,
        mcu: object = None,
        dmm: object = None,
        res: object = None,
        boxRes: list = [0.0]*16
    ):
    """
    Order each message to checker

    Parameters
    ----------
        recipe: list
            0: main
            1-end: option
        mcu: object
            comm2checker.Serial2Mcu
        dmm: object
            comm2dmm.DmmADCMT
        res: object
            comm2resistor.Res
        boxRes: list
            box's each SQ's ohms

    Returns
    ----------
        each message from checker
    """
    mcu.emptySeriBuf(mcu.port)
    majC = recipe[0]
    if majC == 'IGON':
        return odrIGON(recipe, mcu)
    elif majC == 'IGOFF':
        return odrIGOFF(recipe, mcu)
    elif majC == 'RYON':
        return odrRYON(recipe, mcu)
    elif majC == 'RYOFF':
        return odrRYOFF(recipe, mcu)
    elif majC == 'RYDEF':
        return odrRYDEF(recipe, mcu)
    elif majC == 'RYALLOFF':
        return odrRYALLOFF(recipe, mcu)
    elif majC == 'WAIT':
        return odrWAIT(recipe, mcu)
    elif majC == 'CAN':
        return odrCAN(recipe, mcu)
    elif majC == 'MEASA':
        return odrMeasAmpere(recipe, mcu, dmm=dmm)
    elif majC == 'MEASOHM':
        return odrMeasOhm(recipe, mcu, dmm=dmm)
    elif majC[0:5] == 'LEVEL':
        return odrLevelingOhm(recipe, mcu, res=res, boxRes=boxRes)
    else:
        return 0

def judge2checker(receipt=None, judge=None) -> str:
    """
    Make Judgement from checker's receipt

    Parameters
    ----------
        receipt: str
            result from checker
        judge: str
            judgement from scenario

    Returns
    ----------
        result: str
            PASS or FAIL
    """
    # if none
    if receipt is None:
        result = 'FAIL'
    # if levelize
    elif '~' in judge:
        li_jdg = sorted(list(map(lambda item: float(item), judge.split('~'))))
        if len(li_jdg) > 2:
            result = 'FAIL'
        elif li_jdg[0] <= float(receipt) <= li_jdg[1]:
            result = 'PASS'
        else:
            result = 'FAIL'
    # if dtc
    else:
        li_jdg = judge.lower().strip().split(',')
        rct_num = receipt.count(',') + 1
        result = ''
        pass_num = len([s for s in li_jdg if s in receipt])
        if pass_num == len(li_jdg) and pass_num == rct_num:
            result = 'PASS'
        else:
            result = 'FAIL'
    return result

'''
----------
main
----------
'''
if __name__ == '__main__':
    pass
