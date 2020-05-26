# coding: utf-8
"""
Serial messages of bit assign to checker.
Require to less than 4digits.
"""

# controller -> checker

# system
mcuReset = '1000'
softVersion = '1100'
igOpe = '12'
igOn = '1200'
igOff = '1299'
readVol = '13'
readVCC = '1301'
readVPWR = '1302'
# relay
ryOn = '20'
ryOff = '21'
ryDef = '2200'
ryAllOff = '2300'
# wait
waitSec = '30'
# can
canDtcRead = '4000'
canDtcClear = '4100'
# dmm
dmmDefault = '5000'
dmmAmpereMode = '5100'
dmmResistorMode = '5200'
# resistor
resDefault = '6000'
resOpenMode = '6100'
resBleakMode = '6200'
resGNDleakMode = '6300'
# initial command
chkComm = '8000'
reqCanSndId = '8100'
reqCanResId = '8200'
reqCanMsgDtcRead = '8300'
reqCanMsgDtcClear = '8400'
reqCanMsgAddReq = '8500'
reqRelayDefault = '8900'

# checker -> controller

posRes = '9011'
negRes = '9022'
penRes = '9033'
