# coding: utf-8
'''
Send some message with IP Messenger.
https://ipmsg.org/

TODO:
    No item.
'''
# import from std
import os
import sys
sys.path.append('./')
import subprocess
# import from pypi
import re

INI_FILE_PATH = './settings/ipmessenger.ini'
IPMSNG_NAME = 'IPMsg.exe'
IPCMD_NAME = 'ipcmd.exe'
FINISH_MSG = 'AutoCheck has Finished!'
TEST_MSG = 'This is a test message from AutoChecker.'


def setExePath() -> str:
    """
    Set IP Messenger's full path

    Parameters
    ----------
        Nothing

    Returns
    ----------
        path: str
    """
    if os.path.exists(INI_FILE_PATH):
        with open(INI_FILE_PATH, 'rb') as ini:
            path = ini.readline().decode('utf-8').split('=')[1].strip(' ')
        return path
    else:
        return ''


def checkIPAddr(ipAddr: str) -> bool:
    """
    Check IP Address

    Parameters
    ----------
        ipAddr: str
            IP Address from UI
    Returns
    ----------
        boolean
    """
    pattern = r'\d{1,3}'
    lst_ipAddr = ipAddr.split('.')
    if len(lst_ipAddr) != 4:
        print('number is false')
        return False
    for item in lst_ipAddr:
        if re.fullmatch(pattern, item) is None:
            print('pattern mismatch')
            return False
    return True


def checkIPMsngState() -> int:
    """
    Check IP Messenger to be launched

    Parameters
    ----------
        Nothing

    Returns
    ----------
        res: int
            0 (success) or the other (missing)
    """
    ipcmdCall = [setExePath() + IPCMD_NAME, 'state']
    proc = ''
    try:
        proc = subprocess.Popen(ipcmdCall, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        res = proc.stdout.read().decode('utf-8').rstrip().split('stat=')[1]
        return int(res)
    except:
        print('Failed IPMessenger', file=sys.stderr)
        return 3


def ipMessenger(ipAddr: str, state: str) -> int:
    """
    Send some message with IP Messenger

    Parameters
    ----------
        ipAddr: str
            IP Address from UI
        state: str
            test, or finish
    Returns
    ----------
        int
            1 (success), 2 (missing address), 3 (not launched)
    """
    if checkIPMsngState() != 0:
        return 3
    if checkIPAddr(ipAddr) is False:
        return 2
    msg = FINISH_MSG if state=='finish' else TEST_MSG
    ipmsngCall = [setExePath() + IPMSNG_NAME, '/MSG', ipAddr, msg]
    try:
        proc = subprocess.Popen(ipmsngCall, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except:
        print('Failed IPMessenger', file=sys.stderr)
    return 1


"""
----------
main
----------
"""
if __name__ == '__main__':
    pass
