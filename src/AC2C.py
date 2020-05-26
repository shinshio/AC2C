# coding: utf-8

# ====================================
# import
# ====================================
# import from std
import os
import sys
sys.path.append('./')
import time
import traceback
# import from pypi
import datetime
from plyer import notification
import PyQt5.QtWidgets as qw
import PyQt5.QtGui as qg
import PyQt5.QtCore as qc
# import from selfmade
import src.analyzeScenario as asn
import src.comm2checker
import src.comm2dmm
import src.comm2resistor
import src.generateExcel
import src.ipmessenger as ipm
import src.order2checker as o2c
import src.serBitAssign as ba
# ====================================
# global variables
# ====================================
flgGoing = False
# ====================================
# const variables
# ====================================
ACCver = 'b0.1'
ROOTPATH = os.getenv('HOMEDRIVE') + os.getenv('HOMEPATH') + '/Desktop'
initialOhmPath = './settings/initial_ohm_setting.ini'
imgStart = './images/start.png'
imgPause = './images/pause.png'
imgStop = './images/stop.png'
imgInitRes = './images/initial.png'
imgGo = './images/go.png'
imgReady = './images/ready.png'
imgSet = './images/set.png'
imgIco = './images/car_dekotora.ico'
imgToast = './images/car_dekotora.ico'
imgSplash = './images/splash_loading.png'
# ====================================
# Scenario Tab
# ====================================
class ScenarioTab(qw.QWidget):
    # *************
    # init
    # *************
    def __init__(self,parent=None):
        super(ScenarioTab, self).__init__()
        self.initUI()
        self.logSavePath = ''
        self.scenarioFullPath = ''
        self.lstScenarioCover = []
        self.lstScenarioItems = []
        self.lstScenarioCanInfo = []
        self.lstScenarioRyDefInfo = []
        self.systemLog = []
        self.lstResData = []
        self.lstDmmInfo = []
        self.lstResInfo = []
        self.flgPause = False
        self.flgStop = False
    # *************
    # function
    # *************
    # --------------
    # update system log
    # --------------
    def updateStatusIcon(self, img):
        # update
        try:
            if img=='go':
                self.lblState.setPixmap(qg.QPixmap(imgGo).scaled(48,48))
            elif img=='ready':
                self.lblState.setPixmap(qg.QPixmap(imgReady).scaled(48,48))
            elif img=='set':
                self.lblState.setPixmap(qg.QPixmap(imgSet).scaled(48,48))
        except:
            if traceback.format_exc(2) != 'SystemExit: 0':
                with open(ROOTPATH + '/ErrLog.txt', 'a') as file:
                    file.write(traceback.format_exc())
                    file.close()
        qg.QGuiApplication.processEvents()
    # --------------
    # update system log
    # --------------
    def updateSystemLog(self, log):
        # append
        self.systemLog.append(log)
        self.boxLogData.append(log)
        qg.QGuiApplication.processEvents()
    # --------------
    # push save path dir button
    # --------------
    def funcSelectFolder(self):
        # dialog
        rootpath = ROOTPATH
        path = qw.QFileDialog.getExistingDirectory(
            None,
            'select log save folder',
            rootpath
            )
        # output
        self.boxSavePath.setText(path)
        self.logSavePath = path
    # --------------
    # push scenario file button
    # --------------
    def funcSelectExcelFile(self):
        # dialog
        rootpath = ROOTPATH
        filename = qw.QFileDialog.getOpenFileName(
            self,
            'select scenario file',
            rootpath,
            'Excel Files (*.xls *.xlsx *.xlsm)'
            )
        # GUI update
        try:
            if filename[0] != '':
                self.scenarioFullPath = filename[0]
                # ---init
                self.boxScenarioPath.clear()
                self.boxScenarioTitle.clear()
                self.boxScenarioAuthor.clear()
                self.boxScenarioECUtype.clear()
                self.boxScenarioECUcode.clear()
                self.boxScenarioSumm.clear()
                self.boxScenarioItems.clear()
                self.boxScenarioJudgement.clear()
                # ---cover
                self.lstScenarioCover = asn.takeInCover(filename[0])
                self.boxScenarioPath.setText(filename[0])
                self.boxScenarioTitle.setText(self.lstScenarioCover[0])
                self.boxScenarioAuthor.setText(self.lstScenarioCover[1])
                self.boxScenarioECUtype.setText(self.lstScenarioCover[2])
                self.boxScenarioECUcode.setText(self.lstScenarioCover[3])
                self.boxScenarioSumm.append(self.lstScenarioCover[4])
                self.boxScenarioSumm.append(self.lstScenarioCover[5])
                self.boxScenarioSumm.append(self.lstScenarioCover[6])
                self.boxScenarioSumm.append(self.lstScenarioCover[7])
                # --- contents
                self.lstScenarioItems = asn.takeInScenario(filename[0])
                for i in range(len(self.lstScenarioItems)):
                    no = asn.sn2numZ3(self.lstScenarioItems[i])
                    odr = asn.sn2order(self.lstScenarioItems[i])
                    jdg = asn.sn2judge(self.lstScenarioItems[i])
                    self.boxScenarioItems.append(no+': '+odr)
                    self.boxScenarioJudgement.append(no+': '+jdg)
                # --- can info
                self.lstScenarioCanInfo = asn.takeInCanInfo(filename[0])
                # --- relay default info
                self.lstScenarioRyDefInfo = asn.takeInRyDefInfo(filename[0])
        except:
            pass
            # with open(ROOTPATH + '/ErrLog.txt', 'a') as file:
            #     file.write(traceback.format_exc())
            #     file.close()
    # --------------
    # push res data file button
    # --------------
    def funcSelectResFile(self):
        # dialog
        rootpath = ROOTPATH
        filename = qw.QFileDialog.getOpenFileName(
            self,
            'select res file',
            rootpath,
            'M_Res_in_Checker Files (*.res)'
            )
        # GUI update
        try:
            if filename[0] != '':
                # --- contents
                rawData = []
                filedata = open(filename[0], 'r')
                rawData = filedata.readlines()
                self.lstResData = [float(item.split(' ')[-1].strip()) for item in rawData]
                self.boxInitResPath.setText(filename[0])
        except:
            pass
            # with open(ROOTPATH + '/ErrLog.txt', 'a') as file:
            #     file.write(traceback.format_exc())
            #     file.close()
    # --------------
    # push start button
    # --------------
    def funcStart(self):
        global flgGoing
        # +++++++++++++
        # error check
        # +++++++++++++
        # ---event
        if self.boxSampleEvent.text() == '':
            qw.QMessageBox.warning(self, 'ACC', 'Sample event is blank.')
            return 0
        # ---name
        if self.boxSampleName.text() == '':
            qw.QMessageBox.warning(self, 'ACC', 'Sample name is blank.')
            return 0
        # ---logfolder
        if self.boxSavePath.text() == '':
            qw.QMessageBox.warning(self, 'ACC', 'Log save folder is blank.')
            return 0
        # ---scenario
        if self.boxScenarioPath.text() == '':
            qw.QMessageBox.warning(self, 'ACC', 'Scenario file is not selected.')
            return 0
        # ---progress
        if flgGoing == True:
            qw.QMessageBox.warning(self, 'ACC', 'Already Started.')
            return 0
        # +++++++++++++
        # process start
        # +++++++++++++
        # ---dialog
        msg = qw.QMessageBox.question(
            self,
            'ACC',
            'Sure?',
            qw.QMessageBox.Yes | qw.QMessageBox.No
        )
        if msg == qw.QMessageBox.No:
            return 0
        # ---init variables
        flgGoing = True
        self.flgPause = False
        self.flgStop = False
        self.systemLog = []
        self.boxLogData.clear()
        self.boxScenarioJudgement.clear()
        # ---display update
        self.updateStatusIcon('go')
        # ---start
        self.updateSystemLog('----------------------------------')
        self.updateSystemLog('    Launch Auto Checker System    ')
        self.updateSystemLog('----------------------------------')
        self.updateSystemLog('Initialize Checker.')
        self.updateSystemLog('... Connect Checker to ACC.')
        # ---check serial comm open (and usb cable is set)
        mcu = src.comm2checker.Serial2Mcu()
        # ---close system when serial comm is not available
        if mcu.port is None:
            self.updateSystemLog('>>>>>> Connection is failed.')
            self.updateSystemLog('>>>>>> System exit.')
            self.updateStatusIcon('set')
            flgGoing = False
            return 0
        self.updateSystemLog('>>>>>> Connection is successful.')
        # ---reset mcu
        self.updateSystemLog('... Reset Checker\'s MCU.')
        _ = mcu.sendMsg(ba.mcuReset,0.1)
        self.updateSystemLog('>>>>>> Restart after 3 seconds.')
        time.sleep(1)
        self.updateSystemLog('>>>>>> Restart after 2 seconds.')
        time.sleep(1)
        self.updateSystemLog('>>>>>> Restart after 1 seconds.')
        time.sleep(1)
        self.updateSystemLog('>>>>>> Done.')
        # ---get sample info
        lstSampleInfo = [self.boxSampleEvent.text(), self.boxSampleName.text()]
        # ---get checker info
        lstCheckerInfo = [
            ACCver,
            mcu.sendMsg(ba.softVersion,0.1),
            self.boxScenarioTitle.text()
        ]
        # ---get scenario info(init)
        lstScenarioInfo = []
        # ---send can info to checker
        self.updateSystemLog('... Send CAN Data to Checker.')
        self.updateSystemLog('>>>>>> Sending Data 1.')
        _ = mcu.sendAddInfo(ba.reqCanSndId, self.lstScenarioCanInfo[0][1], 0.1)
        self.updateSystemLog('>>>>>> Sending Data 2.')
        _ = mcu.sendAddInfo(ba.reqCanResId, self.lstScenarioCanInfo[1][1], 0.1)
        self.updateSystemLog('>>>>>> Sending Data 3.')
        _ = mcu.sendAddInfo(ba.reqCanMsgDtcRead, self.lstScenarioCanInfo[2][1], 0.1)
        self.updateSystemLog('>>>>>> Sending Data 4.')
        _ = mcu.sendAddInfo(ba.reqCanMsgDtcClear, self.lstScenarioCanInfo[3][1], 0.1)
        self.updateSystemLog('>>>>>> Sending Data 5.')
        _ = mcu.sendAddInfo(ba.reqCanMsgAddReq, self.lstScenarioCanInfo[4][1], 0.1)
        self.updateSystemLog('>>>>>> Done.')
        # ---send relay default info to checker
        self.updateSystemLog('... Send Relay Default Status to Checker.')
        lstRyDef = [
            str(self.lstScenarioRyDefInfo[i][0]).zfill(2)
            for i in range(len(self.lstScenarioRyDefInfo))
            if self.lstScenarioRyDefInfo[i][1].lower()=='on'
        ]
        strRyDef = ''.join(lstRyDef) if lstRyDef!=[] else 'ff'
        _ = mcu.sendAddInfo(ba.reqRelayDefault, strRyDef, 0.1)
        _ = mcu.sendMsg(ba.ryDef,0.1)
        self.updateSystemLog('>>>>>> Done.')
        # ---connect to dmm
        self.updateSystemLog('Try to connect with DMM.')
        dmm = src.comm2dmm.DmmADCMT(1)
        if dmm.hDev==1:
            self.updateSystemLog('>>>>>> Connection with DMM is failed.')
            self.updateSystemLog('>>>>>> Item about DMM is skipped.')
            self.lstDmmInfo = ['No Connection', 'No Connection', 'No Connection']
        else:
            self.lstDmmInfo = dmm.readId()
            self.updateSystemLog('>>>>>> Done.')
        # ---connect to resistor
        self.updateSystemLog('Try to connect with Resistor.')
        res = src.comm2resistor.Resistor('resistorname')
        if res.statusRes==False:
            self.updateSystemLog('>>>>>> Connection with Resistor is failed.')
            self.updateSystemLog('>>>>>> Item about Resistor is skipped.')
            self.lstResInfo = ['No Connection', 'No Connection', 'No Connection']
        else:
            self.lstResInfo = res.readId()
            self.updateSystemLog('>>>>>> Done.')
        # ---system log update
        self.updateSystemLog('----------------------------------')
        self.updateSystemLog('Start Auto Checker Program')
        self.updateSystemLog('Auto Checker Controller Version  : {}'.format(lstCheckerInfo[0]))
        self.updateSystemLog('Auto Checker MCU Software Version: {}'.format(lstCheckerInfo[1]))
        self.updateSystemLog('----------------------------------')
        self.updateSystemLog('DMM Model  Name  : {}, {}'.format(self.lstDmmInfo[0], self.lstDmmInfo[1]))
        self.updateSystemLog('DMM Serial Number: {}'.format(self.lstDmmInfo[2]))
        self.updateSystemLog('----------------------------------')
        self.updateSystemLog('Resistor Model   Name  : {}, {}'.format(self.lstResInfo[0], self.lstResInfo[1]))
        self.updateSystemLog('Resistor Serial  Number: {}'.format(self.lstResInfo[2]))
        self.updateSystemLog('Resistor Initial File  : {}'.format(self.boxScenarioPath.text()))
        self.updateSystemLog('----------------------------------')
        self.updateSystemLog('start time: {}'.format(datetime.datetime.now()))
        self.updateSystemLog('----------------------------------')
        self.updateSystemLog('sample event  : {}'.format(lstSampleInfo[0]))
        self.updateSystemLog('sample name   : {}'.format(lstSampleInfo[1]))
        self.updateSystemLog('scenario file : {}'.format(self.boxScenarioPath.text()))
        self.updateSystemLog('----------------------------------')
        # ---order and judge about each recipe
        for i, item in enumerate(self.lstScenarioItems):
            # take in scenario data
            no = asn.sn2numZ3(item)
            odr = asn.sn2order(item)
            jdg = asn.sn2judge(item)
            self.updateSystemLog('{}: [order]   {}'.format(no,odr))
            # extract recipe
            rcp = asn.sn2recipe(item)
            self.updateSystemLog('{}: [recipe]  {}'.format(no,rcp))
            # order recipe and receive receipt from checker
            rct = o2c.order2checker(rcp, mcu, dmm, res, self.lstResData)
            # --- move items box
            if i==0:
                self.boxScenarioItems.moveCursor(qg.QTextCursor.Start)
            else:
                self.boxScenarioItems.moveCursor(qg.QTextCursor.Down)
            # --- if receipt is penRes (checker 5V is low)
            if rct == ba.penRes:
                self.updateSystemLog('Checker error!')
                self.updateSystemLog('Checker internal power is something wrong.')
                self.updateSystemLog('System exit.')
                self.updateStatusIcon('set')
                qw.QMessageBox.information(self, 'ACC', 'Terminated.')
                break
            result = o2c.judge2checker(rct, jdg)
            if result == 'PASS':
                # when all receipt is pass, judge text color sets black
                self.boxScenarioJudgement.setTextColor(qg.QColor(0,0,0))
            else:
                # when any receipt is fail, judge text color sets red
                self.boxScenarioJudgement.setTextColor(qg.QColor(255,0,0))
            self.boxScenarioJudgement.append('['+result+']'+no+': '+rct)
            self.updateSystemLog('{}: [receipt] {} ... {} (judge: {})'.format(no,rct,result,jdg))
            # when pause is clicked
            if self.flgPause:
                self.updateSystemLog('Pause Button is pressed!')
                self.updateStatusIcon('ready')
                qw.QMessageBox.information(self, 'ACC', 'Pause is clicked.\nContinue?')
                self.flgPause = False
                self.updateStatusIcon('go')
                self.updateSystemLog('Restart!')
            # when stop is clicked
            if self.flgStop:
                self.updateSystemLog('Stop Button is pressed!')
                self.updateStatusIcon('ready')
                msg = qw.QMessageBox.question(
                    self,
                    'ACC',
                    'Stop is clicked.\nSure?',
                    qw.QMessageBox.Yes | qw.QMessageBox.No
                )
                if msg ==qw.QMessageBox.No:
                    self.flgStop = False
                    self.updateStatusIcon('go')
                    self.updateSystemLog('Restart!')
                else:
                    self.updateStatusIcon('set')
                    qw.QMessageBox.information(self, 'ACC', 'Terminated.')
                    break
            # display update
            self.updateStatusIcon('go')
            qg.QGuiApplication.processEvents()
            # ---get scenario info(append)
            lstScenarioInfo.append([no, odr, jdg, rct, result])
        # end process
        # --- set all relay off
        _ = o2c.order2checker(['RYALLOFF',], mcu)
        # --- display update
        self.updateStatusIcon('set')
        flgGoing = False
        self.updateSystemLog('----------------------------------')
        self.updateSystemLog('end time: {}'.format(datetime.datetime.now()))
        self.updateSystemLog('')
        self.updateSystemLog('Finished!')
        # --- toast
        notification.notify(
            title='Message From ACC',
            message='Finished All Scenario Orders!',
            app_name='ACC(Python)',
            app_icon=imgToast
        )
        # --- output log file
        timeNow = datetime.datetime.now().isoformat().replace(':','-').rsplit('.')[0]
        fnamelog = (
            self.logSavePath+'/'
            +str(self.boxSampleEvent.text())+'_'
            +str(self.boxSampleName.text())+'_'
            +timeNow
            +'.log'
        )
        with open(fnamelog, 'w') as file:
            file.write('\n'.join(self.systemLog))
            file.close()
        self.updateSystemLog('System log is output at [{}]'.format(self.logSavePath))
        # --- output report file
        fnameExcel = (
            self.logSavePath+'/'
            +str(self.boxSampleEvent.text())+'_'
            +str(self.boxSampleName.text())+'_'
            +timeNow
            +'.xlsx'
        )
        report = src.generateExcel.Report(fnameExcel)
        report.setSampleInfo(lstSampleInfo)
        report.setCheckerInfo(lstCheckerInfo)
        report.setDmmInfo(self.lstDmmInfo)
        report.setResistorInfo(self.lstResInfo)
        report.setScenarioInfo(lstScenarioInfo)
        report.setSampleInfo(lstSampleInfo)
        report.outputExcelReport()
        report.outputLevelCsv()
        self.updateSystemLog('Report file is output at [{}]'.format(self.logSavePath))
        # --- ip messenger
        if self.boxNotify.isChecked():
            self.callIPMsng('finish')
        # --- delete objects
        del mcu
        del dmm
        del res
    # --------------
    # push init res button
    # --------------
    def funcInitRes(self):
        global flgGoing
        # +++++++++++++
        # error check
        # +++++++++++++
        # ---logfolder
        if self.boxSavePath.text() == '':
            qw.QMessageBox.warning(self, 'ACC', 'Log save folder is blank.')
            return 0
        # ---progress
        if flgGoing == True:
            qw.QMessageBox.warning(self, 'ACC', 'Already Started.')
            return 0
        # +++++++++++++
        # process start
        # +++++++++++++
        # ---dialog
        msg = qw.QMessageBox.question(self, 'ACC', 'Sure?', qw.QMessageBox.Yes | qw.QMessageBox.No)
        if msg == qw.QMessageBox.No:
            return 0
        # ---init variables
        flgGoing = True
        self.flgPause = False
        self.flgStop = False
        self.systemLog = []
        self.boxLogData.clear()
        self.boxScenarioJudgement.clear()
        # ---display update
        self.updateStatusIcon('go')
        # ---start
        self.updateSystemLog('----------------------------------')
        self.updateSystemLog('    Launch Auto Checker System    ')
        self.updateSystemLog('----------------------------------')
        self.updateSystemLog('Initialize Checker.')
        self.updateSystemLog('... Connect Checker to ACC.')
        # ---check serial comm open (and usb cable is set)
        mcu = src.comm2checker.Serial2Mcu()
        # ---close system when serial comm is not available
        if mcu.port is None:
            self.updateSystemLog('>>>>>> Connection is failed.')
            self.updateSystemLog('>>>>>> System exit.')
            self.updateStatusIcon('set')
            flgGoing = False
            return 0
        self.updateSystemLog('>>>>>> Connection is successful.')
        # ---reset mcu
        self.updateSystemLog('... Reset Checker\'s MCU.')
        _ = mcu.sendMsg(ba.mcuReset,0.1)
        self.updateSystemLog('>>>>>> Restart after 3 seconds.')
        time.sleep(1)
        self.updateSystemLog('>>>>>> Restart after 2 seconds.')
        time.sleep(1)
        self.updateSystemLog('>>>>>> Restart after 1 seconds.')
        time.sleep(1)
        self.updateSystemLog('>>>>>> Done.')
        # ---get checker info
        lstCheckerInfo = [ACCver, mcu.sendMsg(ba.softVersion,0.1), self.boxScenarioTitle.text()]
        # --- set all relay off
        _ = o2c.order2checker(['RYALLOFF',], mcu)
        # ---system log update
        self.updateSystemLog('----------------------------------')
        self.updateSystemLog('Start Auto Checker Program')
        self.updateSystemLog('Auto Checker Controller Version: {}'.format(lstCheckerInfo[0]))
        self.updateSystemLog('Auto Checker MCU Software Version: {}'.format(lstCheckerInfo[1]))
        self.updateSystemLog('----------------------------------')
        self.updateSystemLog('start time: {}'.format(datetime.datetime.now()))
        self.updateSystemLog('----------------------------------')
        # ---start measurement
        lstMeasOhm = []
        lstRelaySQ = [
            '09', '0a', '0b', '0c', '0d', '0e', '0f', '10',
            '19', '1a', '1b', '1c', '1d', '1e', '1f', '20'
            ]
        # open comm to dmm
        dmm = src.comm2dmm.DmmADCMT(1)
        if dmm.hDev==1:
            self.updateSystemLog('>>>>>> Connection with DMM is failed.')
            self.updateSystemLog('>>>>>> System exit.')
            self.updateStatusIcon('set')
            flgGoing = False
            return 0
        # measure
        for item in lstRelaySQ:
            # --- measure
            time.sleep(1)
            rct = o2c.order2checker(['MEASOHM', item], mcu, dmm=dmm)
            # --- if receipt is penRes (checker 5V is low)
            if rct == ba.penRes:
                self.updateSystemLog('Checker error!')
                self.updateSystemLog('Checker internal power is something wrong.')
                self.updateSystemLog('System exit.')
                self.updateStatusIcon('set')
                flgGoing = False
                break
            # --- if receipt is negRes
            if rct == ba.negRes:
                self.updateSystemLog('Checker error!')
                self.updateSystemLog('System exit.')
                self.updateStatusIcon('set')
                flgGoing = False
                break
            lstMeasOhm.append('SQ'+str(len(lstMeasOhm)+1).zfill(2)+': '+str(rct))
            self.boxScenarioJudgement.append(lstMeasOhm[-1])
            self.updateSystemLog('SQ{} ... {}'.format(str(len(lstMeasOhm)).zfill(2),str(rct)))
        # end process
        # --- set all relay off
        _ = o2c.order2checker(['RYALLOFF',], mcu)
        # --- display update
        self.updateStatusIcon('set')
        flgGoing = False
        self.updateSystemLog('----------------------------------')
        self.updateSystemLog('end time: {}'.format(datetime.datetime.now()))
        self.updateSystemLog('')
        self.updateSystemLog('Finished!')
        # --- output res file
        timeNow = datetime.datetime.now().isoformat().replace(':','-').rsplit('.')[0]
        fnameres = self.logSavePath+'/'+'M_Res_in_Checker'+'_'+timeNow+'.res'
        with open(fnameres, 'w') as file:
            file.write('\n'.join(lstMeasOhm))
            file.close()
        self.updateSystemLog('Measurement data is output at [{}]'.format(self.logSavePath))
        # --- delete dmm object
        del dmm
    # --------------
    # push pause button
    # --------------
    def funcPause(self):
        # flag
        self.flgPause = True
    # --------------
    # push stop button
    # --------------
    def funcStop(self):
        # flag
        self.flgStop = True
    # --------------
    # send message with ip messenger
    # --------------
    def callIPMsng(self, state):
        ipAddr = self.boxIPAddr.text()
        result = ipm.ipMessenger(ipAddr, state)
        if result == 1:
            qw.QMessageBox.information(self, 'ACC', 'Successfully Send Message.')
        elif result == 2:
            qw.QMessageBox.warning(self, 'ACC', 'Confirm IP Address.')
        elif result == 3:
            qw.QMessageBox.warning(self, 'ACC', 'IP Messenger is not launched.')
        else:
            qw.QMessageBox.warning(self, 'ACC', 'Unexpected Error.')
    # *************
    # GUI
    # *************
    def initUI(self):
        # --------------
        # common styles
        # --------------
        style = '''
            *{
                font-family: Meiryo
                }
            QGroupBox{
                color: #2A3FFF;
                font-size: 12pt
                }
            QLineEdit{
                font-family: Courier
            }
            QTextEdit{
                font-family: Courier
            }
            '''
        self.setStyleSheet(style)
        # --------------
        # Group <Buttons>
        # --------------
        # create parts
        self.btnStart = qw.QPushButton()
        self.btnPause = qw.QPushButton()
        self.btnStop = qw.QPushButton()
        self.btnInitRes = qw.QPushButton()
        # style
        self.btnStart.setStyleSheet('QPushButton{width: 50px; height: 50px;}')
        self.btnStart.setIcon(qg.QIcon(imgStart))
        self.btnStart.setIconSize(qc.QSize(48,48))
        self.btnPause.setStyleSheet('QPushButton{width: 50px; height: 50px;}')
        self.btnPause.setIcon(qg.QIcon(imgPause))
        self.btnPause.setIconSize(qc.QSize(48,48))
        self.btnStop.setStyleSheet('QPushButton{width: 50px; height: 50px;}')
        self.btnStop.setIcon(qg.QIcon(imgStop))
        self.btnStop.setIconSize(qc.QSize(48,48))
        self.btnInitRes.setStyleSheet('QPushButton{width: 50px; height: 50px;}')
        self.btnInitRes.setIcon(qg.QIcon(imgInitRes))
        self.btnInitRes.setIconSize(qc.QSize(48,48))
        # call function
        self.btnStart.clicked.connect(self.funcStart)
        self.btnPause.clicked.connect(self.funcPause)
        self.btnStop.clicked.connect(self.funcStop)
        self.btnInitRes.clicked.connect(self.funcInitRes)
        # place parts on layout
        self.loButtons = qw.QGridLayout()
        self.loButtons.addWidget(self.btnStart,0,0,2,2)
        self.loButtons.addWidget(self.btnPause,0,2,2,2)
        self.loButtons.addWidget(self.btnStop,0,4,2,2)
        self.loButtons.addWidget(self.btnInitRes,0,8,2,2)
        # place layout on groupbox
        self.gbButtons = qw.QGroupBox()
        self.gbButtons.setFlat(True)
        self.gbButtons.setLayout(self.loButtons)
        # --------------
        # Group <State>
        # --------------
        # create parts
        self.lblState = qw.QLabel(self)
        # style
        self.lblState.setStyleSheet('QLabel{width: 50px; height: 50px;}')
        self.updateStatusIcon('set')
        # call function
        pass
        # place parts on layout
        self.loState = qw.QGridLayout()
        self.loState.addWidget(self.lblState,0,0,2,2)
        # place layout on groupbox
        self.gbState = qw.QGroupBox()
        self.gbState.setFlat(True)
        self.gbState.setLayout(self.loState)
        # --------------
        # Group <Sample info>
        # --------------
        # create parts
        self.lblSampleEvent = qw.QLabel('Event')
        self.boxSampleEvent = qw.QLineEdit()
        self.lblSampleName = qw.QLabel('ECU ID')
        self.boxSampleName = qw.QLineEdit()
        self.btnSavePath = qw.QPushButton('Save Fol.')
        self.boxSavePath = qw.QLineEdit()
        # style
        self.boxSampleEvent.setStyleSheet('QLineEdit{background-color: yellow}')
        self.boxSampleEvent.textChanged.connect(
            lambda text: self.boxSampleEvent.setStyleSheet(
                'QLineEdit{background-color: %s}' % ('white' if text else 'yellow')
            )
        )
        self.boxSampleName.setStyleSheet('QLineEdit{background-color: yellow}')
        self.boxSampleName.textChanged.connect(
            lambda text: self.boxSampleName.setStyleSheet(
                'QLineEdit{background-color: %s}' % ('white' if text else 'yellow')
            )
        )
        self.boxSavePath.setStyleSheet('QLineEdit{background-color: yellow}')
        self.boxSavePath.textChanged.connect(
            lambda text: self.boxSavePath.setStyleSheet(
                'QLineEdit{background-color: %s}' % ('white' if text else 'yellow')
            )
        )
        self.boxSavePath.setReadOnly(True)
        # call function
        self.btnSavePath.clicked.connect(self.funcSelectFolder)
        # place parts on layout
        self.loSamInfo = qw.QGridLayout()
        self.loSamInfo.addWidget(self.lblSampleEvent,0,0,1,1)
        self.loSamInfo.addWidget(self.boxSampleEvent,0,1,1,4)
        self.loSamInfo.addWidget(self.lblSampleName,0,5,1,1)
        self.loSamInfo.addWidget(self.boxSampleName,0,6,1,4)
        self.loSamInfo.addWidget(self.btnSavePath,1,0,1,1)
        self.loSamInfo.addWidget(self.boxSavePath,1,1,1,9)
        # place layout on groupbox
        self.gbSamInfo = qw.QGroupBox('Sample Information')
        self.gbSamInfo.setLayout(self.loSamInfo)
        # --------------
        # Group <IP Messenger>
        # --------------
        # create parts
        self.boxNotify = qw.QCheckBox('Enable')
        self.btnSendTest = qw.QPushButton('TEST')
        self.lblIPAddr = qw.QLabel('IP Address')
        self.boxIPAddr = qw.QLineEdit()
        # style
        pass
        # call function
        self.btnSendTest.clicked.connect(lambda: self.callIPMsng('test'))
        # place parts on layout
        self.loIPMsng = qw.QGridLayout()
        self.loIPMsng.addWidget(self.boxNotify,0,0,1,1)
        self.loIPMsng.addWidget(self.btnSendTest,0,1,1,1)
        self.loIPMsng.addWidget(self.lblIPAddr,1,0,1,1)
        self.loIPMsng.addWidget(self.boxIPAddr,1,1,1,5)
        # place layout on groupbox
        self.gbIPMsng = qw.QGroupBox('IP Messenger')
        self.gbIPMsng.setLayout(self.loIPMsng)
        # --------------
        # Group <scenario info>
        # --------------
        # create parts
        self.btnScenarioPath = qw.QPushButton('Scenario')
        self.boxScenarioPath = qw.QLineEdit()
        self.btnInitResPath = qw.QPushButton('RES File')
        self.boxInitResPath = qw.QLineEdit()
        self.lblScenarioTitle = qw.QLabel('Title')
        self.boxScenarioTitle = qw.QLineEdit()
        self.lblScenarioAuthor = qw.QLabel('Author')
        self.boxScenarioAuthor = qw.QLineEdit()
        self.lblScenarioECUtype = qw.QLabel('ECU Type')
        self.boxScenarioECUtype = qw.QLineEdit()
        self.lblScenarioECUcode = qw.QLabel('ECU Code')
        self.boxScenarioECUcode = qw.QLineEdit()
        self.lblScenarioSumm = qw.QLabel('Summary')
        self.boxScenarioSumm = qw.QTextEdit()
        self.lblScenarioItems = qw.QLabel('Items')
        self.boxScenarioItems = qw.QTextEdit()
        self.lblScenarioJudgement = qw.QLabel('Judgement')
        self.boxScenarioJudgement = qw.QTextEdit()
        # style
        self.boxScenarioPath.setStyleSheet('QLineEdit{background-color: yellow}')
        self.boxScenarioPath.textChanged.connect(
            lambda text: self.boxScenarioPath.setStyleSheet(
                'QLineEdit{background-color: %s}' % ('white' if text else 'yellow')
            )
        )
        self.boxScenarioPath.setReadOnly(True)
        self.boxInitResPath.setReadOnly(True)
        self.boxScenarioTitle.setReadOnly(True)
        self.boxScenarioAuthor.setReadOnly(True)
        self.boxScenarioECUtype.setReadOnly(True)
        self.boxScenarioECUcode.setReadOnly(True)
        self.boxScenarioSumm.setReadOnly(True)
        self.boxScenarioItems.setReadOnly(True)
        self.boxScenarioJudgement.setReadOnly(True)
        # call function
        self.btnScenarioPath.clicked.connect(self.funcSelectExcelFile)
        self.btnInitResPath.clicked.connect(self.funcSelectResFile)
        # place parts on layout
        self.loSnroInfo = qw.QGridLayout()
        self.loSnroInfo.addWidget(self.btnScenarioPath,0,0,1,1)
        self.loSnroInfo.addWidget(self.boxScenarioPath,0,1,1,14)
        self.loSnroInfo.addWidget(self.btnInitResPath,1,0,1,1)
        self.loSnroInfo.addWidget(self.boxInitResPath,1,1,1,14)
        self.loSnroInfo.addWidget(self.lblScenarioTitle,3,0,1,1)
        self.loSnroInfo.addWidget(self.boxScenarioTitle,3,1,1,2)
        self.loSnroInfo.addWidget(self.lblScenarioAuthor,4,0,1,1)
        self.loSnroInfo.addWidget(self.boxScenarioAuthor,4,1,1,2)
        self.loSnroInfo.addWidget(self.lblScenarioECUtype,5,0,1,1)
        self.loSnroInfo.addWidget(self.boxScenarioECUtype,5,1,1,2)
        self.loSnroInfo.addWidget(self.lblScenarioECUcode,6,0,1,1)
        self.loSnroInfo.addWidget(self.boxScenarioECUcode,6,1,1,2)
        self.loSnroInfo.addWidget(self.lblScenarioSumm,7,0,1,1)
        self.loSnroInfo.addWidget(self.boxScenarioSumm,7,1,4,2)
        self.loSnroInfo.addWidget(self.lblScenarioItems,2,3,1,1)
        self.loSnroInfo.addWidget(self.boxScenarioItems,3,3,8,6)
        self.loSnroInfo.addWidget(self.lblScenarioJudgement,2,9,1,1)
        self.loSnroInfo.addWidget(self.boxScenarioJudgement,3,9,8,6)
        # place layout on groupbox
        self.gbSnroInfo = qw.QGroupBox('Scenario Information')
        self.gbSnroInfo.setLayout(self.loSnroInfo)
        # --------------
        # Gronp <Log>
        # --------------
        # create parts
        self.boxLogData = qw.QTextEdit()
        # style
        self.boxLogData.setReadOnly(True)
        # call function
        # place parts on layout
        self.loLogData = qw.QGridLayout()
        self.loLogData.addWidget(self.boxLogData,0,0,3,15)
        # place layout on groupbox
        self.gbLogData = qw.QGroupBox('System Log')
        self.gbLogData.setLayout(self.loLogData)
        # --------------
        # window set
        # --------------
        # V:15 H:15
        # place parts
        self.gridWhole = qw.QGridLayout()
        self.gridWhole.addWidget(self.gbButtons,0,0,2,4)
        self.gridWhole.addWidget(self.gbState,0,13,2,2)
        self.gridWhole.addWidget(self.gbSamInfo,2,0,2,10)
        self.gridWhole.addWidget(self.gbIPMsng,2,10,2,5)
        self.gridWhole.addWidget(self.gbSnroInfo,4,0,11,15)
        self.gridWhole.addWidget(self.gbLogData,15,0,3,15)
        # display
        self.setLayout(self.gridWhole)
# ====================================
# Manual Tab
# ====================================
class ManualSetTab(qw.QWidget):
    # *************
    # init
    # *************
    def __init__(self,parent=None):
        super(ManualSetTab, self).__init__()
        self.initUI()
        self.lstScenarioCover = []
        self.lstScenarioItems = []
        self.lstScenarioCanInfo = []
        self.lstScenarioRyDefInfo = []
        self.systemLog = []
        self.mcu = src.comm2checker.Serial2Mcu_Manual()
    # *************
    # function
    # *************
    # --------------
    # update system log
    # --------------
    def updateSystemLog(self, log):
        # append
        self.systemLog.append(log)
        self.boxLogData.append(log)
        qg.QGuiApplication.processEvents()
    # --------------
    # push scenario file button
    # --------------
    def funcSelectExcelFile(self):
        # dialog
        rootpath = ROOTPATH
        filename = qw.QFileDialog.getOpenFileName(
            self,
            'select scenario file',
            rootpath,
            'Excel Files (*.xls *.xlsx *.xlsm)'
            )
        # GUI update
        try:
            if filename[0] != '':
                self.scenarioFullPath = filename[0]
                # ---init
                self.boxScenarioPath.clear()
                self.boxScenarioTitle.clear()
                self.boxScenarioAuthor.clear()
                self.boxScenarioECUtype.clear()
                self.boxScenarioECUcode.clear()
                self.boxScenarioSumm.clear()
                self.boxScenarioItems.clear()
                self.boxScenarioJudgement.clear()
                # ---cover
                self.lstScenarioCover = asn.takeInCover(filename[0])
                self.boxScenarioPath.setText(filename[0])
                self.boxScenarioTitle.setText(self.lstScenarioCover[0])
                self.boxScenarioAuthor.setText(self.lstScenarioCover[1])
                self.boxScenarioECUtype.setText(self.lstScenarioCover[2])
                self.boxScenarioECUcode.setText(self.lstScenarioCover[3])
                self.boxScenarioSumm.append(self.lstScenarioCover[4])
                self.boxScenarioSumm.append(self.lstScenarioCover[5])
                self.boxScenarioSumm.append(self.lstScenarioCover[6])
                self.boxScenarioSumm.append(self.lstScenarioCover[7])
                # --- contents
                self.lstScenarioItems = asn.takeInScenario(filename[0])
                for i in range(len(self.lstScenarioItems)):
                    no = asn.sn2numZ3(self.lstScenarioItems[i])
                    odr = asn.sn2order(self.lstScenarioItems[i])
                    jdg = asn.sn2judge(self.lstScenarioItems[i])
                    self.boxScenarioItems.append(no+': '+odr)
                    self.boxScenarioJudgement.append(no+': '+jdg)
                # --- can info
                self.lstScenarioCanInfo = asn.takeInCanInfo(filename[0])
                # --- relay default info
                self.lstScenarioRyDefInfo = asn.takeInRyDefInfo(filename[0])
        except:
            with open(ROOTPATH + '/ErrLog.txt', 'a') as file:
                file.write(traceback.format_exc())
                file.close()
    # --------------
    # push connect to checker button
    # --------------
    def funcManuC2C(self):
        global flgGoing
        # +++++++++++++
        # error check
        # +++++++++++++
        # ---Scenario
        if self.boxScenarioPath.text() == '':
            qw.QMessageBox.warning(self, 'ACC', 'scenario file is not selected.')
            return 0
        # +++++++++++++
        # process start
        # +++++++++++++
        flgGoing = True
        # ---init variables
        self.systemLog = []
        self.boxLogData.clear()
        # ---start
        self.updateSystemLog('----------------------------------')
        self.updateSystemLog('    Launch Auto Checker System    ')
        self.updateSystemLog('----------------------------------')
        self.updateSystemLog('Initialize Checker.')
        self.updateSystemLog('... Connect Checker to ACC.')
        # ---check serial comm open (and usb cable is set)
        self.mcu.port = self.mcu.openSeriPort()
        # ---close system when serial comm is not available
        if self.mcu.port is None:
            self.updateSystemLog('>>>>>> Connection is failed.')
            self.updateSystemLog('>>>>>> System exit.')
            flgGoing = False
            return 0
        self.updateSystemLog('>>>>>> Connection is successful.')
        # ---reset mcu
        self.updateSystemLog('... Reset Checker\'s MCU.')
        _ = self.mcu.sendMsg(ba.mcuReset,0.1)
        self.updateSystemLog('>>>>>> Restart after 3 seconds.')
        time.sleep(1)
        self.updateSystemLog('>>>>>> Restart after 2 seconds.')
        time.sleep(1)
        self.updateSystemLog('>>>>>> Restart after 1 seconds.')
        time.sleep(1)
        self.updateSystemLog('>>>>>> Done.')
        # ---get checker info
        lstCheckerInfo = [
            ACCver,
            self.mcu.sendMsg(ba.softVersion,0.1),
            self.boxScenarioTitle.text()
        ]
        # ---send can info to checker
        self.updateSystemLog('... Send CAN Data to Checker.')
        self.updateSystemLog('>>>>>> Sending Data 1.')
        _ = self.mcu.sendAddInfo(ba.reqCanSndId, self.lstScenarioCanInfo[0][1], 0.1)
        self.updateSystemLog('>>>>>> Sending Data 2.')
        _ = self.mcu.sendAddInfo(ba.reqCanResId, self.lstScenarioCanInfo[1][1], 0.1)
        self.updateSystemLog('>>>>>> Sending Data 3.')
        _ = self.mcu.sendAddInfo(ba.reqCanMsgDtcRead, self.lstScenarioCanInfo[2][1], 0.1)
        self.updateSystemLog('>>>>>> Sending Data 4.')
        _ = self.mcu.sendAddInfo(ba.reqCanMsgDtcClear, self.lstScenarioCanInfo[3][1], 0.1)
        self.updateSystemLog('>>>>>> Sending Data 5.')
        _ = self.mcu.sendAddInfo(ba.reqCanMsgAddReq, self.lstScenarioCanInfo[4][1], 0.1)
        self.updateSystemLog('>>>>>> Done.')
        # ---send relay default info to checker
        self.updateSystemLog('... Send Relay Default Status to Checker.')
        lstRyDef = [
            str(self.lstScenarioRyDefInfo[i][0]).zfill(2)
            for i in range(len(self.lstScenarioRyDefInfo))
            if self.lstScenarioRyDefInfo[i][1].lower()=='on'
        ]
        strRyDef = ''.join(lstRyDef) if lstRyDef!=[] else 'ff'
        _ = self.mcu.sendAddInfo(ba.reqRelayDefault, strRyDef, 0.1)
        _ = self.mcu.sendMsg(ba.ryDef,0.1)
        self.updateSystemLog('>>>>>> Done.')
        # ---system log update
        self.updateSystemLog('----------------------------------')
        self.updateSystemLog('Initialization have finished.')
        self.updateSystemLog('Auto Checker Controller Version: {}'.format(lstCheckerInfo[0]))
        self.updateSystemLog('Auto Checker MCU Software Version: {}'.format(lstCheckerInfo[1]))
        self.updateSystemLog('----------------------------------')
        flgGoing = False
    # --------------
    # push disconnection button
    # --------------
    def funcManuDisconnect(self):
        global flgGoing
        # +++++++++++++
        # error check
        # +++++++++++++
        # --- close system when serial comm is not available
        if self.mcu.port is None:
            qw.QMessageBox.warning(self, 'ACC', 'Communication Error.\n')
            return 0
        # +++++++++++++
        # process start
        # +++++++++++++
        flgGoing = True
        self.updateSystemLog('Disconnect to Checker.')
        _ = self.mcu.closeSeriPort()
        self.updateSystemLog('>>>>>> Done.')
        self.updateSystemLog('----------------------------------')
        flgGoing = False
    # --------------
    # push set default button
    # --------------
    def funcManuDef(self):
        global flgGoing
        # +++++++++++++
        # error check
        # +++++++++++++
        # --- scenario
        if self.boxScenarioPath.text() == '':
            qw.QMessageBox.warning(self, 'ACC', 'Scenario file is not selected.')
            return 0
        # --- close system when serial comm is not available
        if self.mcu.port is None:
            qw.QMessageBox.warning(self, 'ACC', 'Communication Error.\n')
            return 0
        # +++++++++++++
        # process start
        # +++++++++++++
        flgGoing = True
        self.updateSystemLog('Set Checker to Default Status.')
        self.updateSystemLog('... Now order to checker.')
        _ = o2c.order2checker(['RYDEF',], self.mcu)
        self.updateSystemLog('>>>>>> Done.')
        self.updateSystemLog('----------------------------------')
        flgGoing = False
    # --------------
    # push start button
    # --------------
    def funcManuStart(self):
        global flgGoing
        # +++++++++++++
        # error check
        # +++++++++++++
        # ---scenario
        if self.boxScenarioPath.text() == '':
            qw.QMessageBox.warning(self, 'ACC', 'Scenario file is not selected.')
            return 0
        # ---close system when serial comm is not available
        if self.mcu.port is None:
            qw.QMessageBox.warning(self, 'ACC', 'Communication Error.\n')
            return 0
        # +++++++++++++
        # process start
        # +++++++++++++
        flgGoing = True
        # make scenario manually
        lstManuScenarioItems = []
        # --- SQ
        sqNo = int(self.boxSQno.currentText()[2:4])
        ryNo = 0
        ryStr = ''
        if self.btnSQopen.isChecked():
            if sqNo<9:
                ryNo = sqNo
                ryStr = hex(ryNo)[2:]
            elif sqNo<13:
                ryNo = sqNo + 8
                ryStr = hex(ryNo)[2:]
            else:
                ryNo = sqNo + 88
                ryStr = hex(ryNo)[2:]
            lstManuScenarioItems.append([
                '',
                'SQ{}->OPEN<RYON_{}>'.format(str(sqNo).zfill(2), ryStr.zfill(2)),
                ''
            ])
        if self.btnSQshort.isChecked():
            if sqNo<9:
                ryNo = sqNo + 8
                ryStr = hex(ryNo)[2:]
            else:
                ryNo = sqNo + 16
                ryStr = hex(ryNo)[2:]
            lstManuScenarioItems.append([
                '',
                'SQ{}->SHORT<RYON_{}_5a>'.format(str(sqNo).zfill(2), ryStr.zfill(2)),
                ''
            ])
        if self.btnSQBleak.isChecked():
            if sqNo<9:
                ryNo = sqNo + 8
                ryStr = hex(ryNo)[2:]
            else:
                ryNo = sqNo + 16
                ryStr = hex(ryNo)[2:]
            lstManuScenarioItems.append([
                '',
                'SQ{}->+Bleak<RYON_{}_4a>'.format(str(sqNo).zfill(2), ryStr.zfill(2)),
                ''
            ])
        if self.btnSQGNDleak.isChecked():
            if sqNo<9:
                ryNo = sqNo + 8
                ryStr = hex(ryNo)[2:]
            else:
                ryNo = sqNo + 16
                ryStr = hex(ryNo)[2:]
            lstManuScenarioItems.append([
                '',
                'SQ{}->SHORT<RYON_{}_52>'.format(str(sqNo).zfill(2), ryStr.zfill(2)),
                ''
            ])
        if self.btnSQsetcom.isChecked():
            if sqNo<9:
                ryNo = sqNo + 8
                ryStr = hex(ryNo)[2:]
            else:
                ryNo = sqNo + 16
                ryStr = hex(ryNo)[2:]
            lstManuScenarioItems.append([''
            ,'SQ{}->setCom<RYON_{}>'.format(str(sqNo).zfill(2) ,ryStr.zfill(2)),
            ''
        ])
        # --- SAT
        satNo = int(self.boxSATno.currentText()[3:4])
        ryNo = 0
        ryStr = ''
        if self.btnSATopen.isChecked():
            ryNo = satNo + 40
            ryStr = hex(ryNo)[2:]
            lstManuScenarioItems.append([
                '',
                'SAT{}->OPEN<RYON_{}>'.format(str(satNo).zfill(2), ryStr.zfill(2)),
                ''
            ])
        # --- load
        loadNo = self.boxLoadno.currentIndex()
        ryNo = 0
        ryStr = ''
        if self.btnLoadopen.isChecked():
            if loadNo<4:
                ryNo = loadNo + 49
                ryStr = hex(ryNo)[2:]
            elif loadNo==4:
                ryNo = 53
                ryStr = hex(ryNo)[2:]
            elif loadNo<7:
                ryNo = loadNo + 94
                ryStr = hex(ryNo)[2:]
            elif loadNo==7:
                ryNo = 108
                ryStr = hex(ryNo)[2:]
            else:
                ryNo = 54
                ryStr = hex(ryNo)[2:]
            lstManuScenarioItems.append([
                '',
                'LOAD{}->OPEN<RYON_{}>'.format(str(loadNo).zfill(2), ryStr.zfill(2)),
                ''
            ])
        # ---order and judge about each recipe
        for i in range(len(lstManuScenarioItems)):
            if range(len(lstManuScenarioItems))==0:
                self.updateSystemLog('No order.')
            # make scenario data
            odr = asn.sn2order(lstManuScenarioItems[i])
            self.updateSystemLog('[order]   {}'.format(odr))
            # extract recipe
            rcp = asn.sn2recipe(lstManuScenarioItems[i])
            self.updateSystemLog('[recipe]  {}'.format(rcp))
            # order recipe and receive receipt from checker
            rct = o2c.order2checker(rcp, self.mcu)
            # --- if receipt is penRes (checker 5V is low)
            if rct == ba.penRes:
                self.updateSystemLog('Checker error!')
                self.updateSystemLog('Checker internal power is something wrong.')
                self.updateSystemLog('System exit.')
                self.updateStatusIcon('set')
                qw.QMessageBox.information(self, 'ACC', 'Terminated.')
                break
            # --- if receipt is nothing
            if rct is None:
                rct = 'error'
            # judge receipt from checker
            self.updateSystemLog('[receipt] {}'.format(rct))
        # end process
        # --- display update
        self.updateSystemLog('All orders is finished.')
        self.updateSystemLog('----------------------------------')
        flgGoing = False
    # --------------
    # push IGONOFF button
    # --------------
    def funcTestIGONOFF(self, pressed):
        global flgGoing
        # +++++++++++++
        # error check
        # +++++++++++++
        # --- close system when serial comm is not available
        if self.mcu.port is None:
            qw.QMessageBox.warning(self, 'ACC', 'Communication Error.\n')
            # --- update GUI
            self.btnIGONOFF.setChecked(False)
            return 0
        # +++++++++++++
        # process start
        # +++++++++++++
        # --- if pressed, order
        if pressed:
            self.btnIGONOFF.setStyleSheet('QPushButton{background-color: red}')
            rct = o2c.order2checker(['IGON',], self.mcu)
            self.updateSystemLog('... Now order to checker.')
        else:
            self.btnIGONOFF.setStyleSheet('QPushButton{background-color: gray}')
            rct = o2c.order2checker(['IGOFF',], self.mcu)
            self.updateSystemLog('... Now order to checker.')
        # --- judge
        if rct ==ba.posRes:
            self.updateSystemLog('>>>>>> Done.')
            self.updateSystemLog('----------------------------------')
        else:
            self.updateSystemLog('>>>>>> Failed.')
            self.updateSystemLog('----------------------------------')
        # --- return [nothing]
        return 0
    # --------------
    # push initialization button
    # --------------
    def funcManuInit(self):
        global flgGoing
        # +++++++++++++
        # error check
        # +++++++++++++
        # --- close system when serial comm is not available
        if self.mcu.port is None:
            qw.QMessageBox.warning(self, 'ACC', 'Communication Error.\n')
            return 0
        # +++++++++++++
        # process start
        # +++++++++++++
        # --- make scenario manually
        flgGoing = True
        self.updateSystemLog('Set Checker to Initial Status.')
        self.updateSystemLog('... Now order to checker.')
        _ = o2c.order2checker(['RYALLOFF',], self.mcu)
        self.updateSystemLog('>>>>>> Done.')
        self.updateSystemLog('Disconnect to Checker.')
        _ = self.mcu.closeSeriPort()
        self.updateSystemLog('>>>>>> Done.')
        self.updateSystemLog('----------------------------------')
        # --- update GUI
        self.btnIGONOFF.setChecked(False)
        self.btnIGONOFF.setStyleSheet('QPushButton{background-color: #E1E1E1}')
        flgGoing = False
    # *************
    # GUI
    # *************
    def initUI(self):
        # --------------
        # common styles
        # --------------
        style = '''
            *{
                font-family: Meiryo
                }
            QGroupBox{
                color: #2A3FFF;
                font-size: 12pt
                }
            QLineEdit{
                font-family: Courier
            }
            QTextEdit{
                font-family: Courier
            }
            '''
        self.setStyleSheet(style)
        # --------------
        # Group <scenario info>
        # --------------
        # create parts
        self.btnScenarioPath = qw.QPushButton('Scenario')
        self.boxScenarioPath = qw.QLineEdit()
        self.lblScenarioTitle = qw.QLabel('Title')
        self.boxScenarioTitle = qw.QLineEdit()
        self.lblScenarioAuthor = qw.QLabel('Author')
        self.boxScenarioAuthor = qw.QLineEdit()
        self.lblScenarioECUtype = qw.QLabel('ECU-Type')
        self.boxScenarioECUtype = qw.QLineEdit()
        self.lblScenarioECUcode = qw.QLabel('ECU-Code')
        self.boxScenarioECUcode = qw.QLineEdit()
        self.lblScenarioSumm = qw.QLabel('Summary')
        self.boxScenarioSumm = qw.QTextEdit()
        self.lblScenarioItems = qw.QLabel('Items')
        self.boxScenarioItems = qw.QTextEdit()
        self.lblScenarioJudgement = qw.QLabel('Judgement')
        self.boxScenarioJudgement = qw.QTextEdit()
        # style
        self.boxScenarioPath.setStyleSheet('QLineEdit{background-color: yellow}')
        self.boxScenarioPath.textChanged.connect(
            lambda text: self.boxScenarioPath.setStyleSheet(
                'QLineEdit{background-color: %s}' % ('white' if text else 'yellow')
            )
        )
        self.boxScenarioTitle.setReadOnly(True)
        self.boxScenarioAuthor.setReadOnly(True)
        self.boxScenarioECUtype.setReadOnly(True)
        self.boxScenarioECUcode.setReadOnly(True)
        self.boxScenarioSumm.setReadOnly(True)
        self.boxScenarioItems.setReadOnly(True)
        self.boxScenarioJudgement.setReadOnly(True)
        # call function
        self.btnScenarioPath.clicked.connect(self.funcSelectExcelFile)
        # place parts on layout
        self.loSnroInfo = qw.QGridLayout()
        self.loSnroInfo.addWidget(self.btnScenarioPath,0,0,1,1)
        self.loSnroInfo.addWidget(self.boxScenarioPath,0,1,1,14)
        self.loSnroInfo.addWidget(self.lblScenarioTitle,2,0,1,1)
        self.loSnroInfo.addWidget(self.boxScenarioTitle,2,1,1,2)
        self.loSnroInfo.addWidget(self.lblScenarioAuthor,3,0,1,1)
        self.loSnroInfo.addWidget(self.boxScenarioAuthor,3,1,1,2)
        self.loSnroInfo.addWidget(self.lblScenarioECUtype,4,0,1,1)
        self.loSnroInfo.addWidget(self.boxScenarioECUtype,4,1,1,2)
        self.loSnroInfo.addWidget(self.lblScenarioECUcode,5,0,1,1)
        self.loSnroInfo.addWidget(self.boxScenarioECUcode,5,1,1,2)
        self.loSnroInfo.addWidget(self.lblScenarioSumm,6,0,1,1)
        self.loSnroInfo.addWidget(self.boxScenarioSumm,6,1,4,2)
        self.loSnroInfo.addWidget(self.lblScenarioItems,1,3,1,1)
        self.loSnroInfo.addWidget(self.boxScenarioItems,2,3,8,6)
        self.loSnroInfo.addWidget(self.lblScenarioJudgement,1,9,1,1)
        self.loSnroInfo.addWidget(self.boxScenarioJudgement,2,9,8,6)
        # place layout on groupbox
        self.gbSnroInfo = qw.QGroupBox('Scenario Info')
        self.gbSnroInfo.setLayout(self.loSnroInfo)
        # --------------
        # Group <SQ Buttons>
        # --------------
        self.lstSq = [
            'SQ01','SQ02','SQ03','SQ04','SQ05','SQ06','SQ07','SQ08',
            'SQ09','SQ10','SQ11','SQ12','SQ13','SQ14','SQ15','SQ16',
            ]
        # create parts
        self.lblSQno = qw.QLabel('SQ No.')
        self.boxSQno = qw.QComboBox(self)
        self.btnSQopen = qw.QRadioButton('OPEN')
        self.btnSQshort = qw.QRadioButton('SHORT')
        self.btnSQBleak = qw.QRadioButton('+B leak')
        self.btnSQGNDleak = qw.QRadioButton('GND leak')
        self.btnSQsetcom = qw.QRadioButton('Connect to COM')
        self.btnSQna = qw.QRadioButton('N/A')
        # style
        self.boxSQno.addItems(self.lstSq)
        # call function
        # place parts on layout
        self.loSQButtons = qw.QVBoxLayout()
        self.loSQButtons.addWidget(self.lblSQno)
        self.loSQButtons.addWidget(self.boxSQno)
        self.loSQButtons.addWidget(self.btnSQopen)
        self.loSQButtons.addWidget(self.btnSQshort)
        self.loSQButtons.addWidget(self.btnSQBleak)
        self.loSQButtons.addWidget(self.btnSQGNDleak)
        self.loSQButtons.addWidget(self.btnSQsetcom)
        self.loSQButtons.addWidget(self.btnSQna)
        self.loSQButtons.addStretch()
        # place layout on groupbox
        self.gbSQButtons = qw.QGroupBox('Squib')
        self.gbSQButtons.setLayout(self.loSQButtons)
        # --------------
        # Group <SAT Buttons>
        # --------------
        self.lstSat = [
            'SAT1','SAT2','SAT3','SAT4','SAT5','SAT6','SAT7','SAT8',
            ]
        # create parts
        self.lblSATno = qw.QLabel('SAT No.')
        self.boxSATno = qw.QComboBox(self)
        self.btnSATopen = qw.QRadioButton('OPEN')
        self.btnSATna = qw.QRadioButton('N/A')
        # style
        self.boxSATno.addItems(self.lstSat)
        # call function
        # place parts on layout
        self.loSATButtons = qw.QVBoxLayout()
        self.loSATButtons.addWidget(self.lblSATno)
        self.loSATButtons.addWidget(self.boxSATno)
        self.loSATButtons.addWidget(self.btnSATopen)
        self.loSATButtons.addWidget(self.btnSATna)
        self.loSATButtons.addStretch()
        # place layout on groupbox
        self.gbSATButtons = qw.QGroupBox('Satellite Sensor')
        self.gbSATButtons.setLayout(self.loSATButtons)
        # --------------
        # Group <LOAD Buttons>
        # --------------
        self.lstLoad = [
            'LOAD1','LOAD2','LOAD3','LOAD4','CN','LOAD6','LOAD7','LOAD8','LOAD_gp',
            ]
        # create parts
        self.lblLoadno = qw.QLabel('Select load')
        self.boxLoadno = qw.QComboBox(self)
        self.btnLoadopen = qw.QRadioButton('OPEN')
        self.btnLoadna = qw.QRadioButton('N/A')
        # style
        self.boxLoadno.addItems(self.lstLoad)
        # call function
        # place parts on layout
        self.loLoadButtons = qw.QVBoxLayout()
        self.loLoadButtons.addWidget(self.lblLoadno)
        self.loLoadButtons.addWidget(self.boxLoadno)
        self.loLoadButtons.addWidget(self.btnLoadopen)
        self.loLoadButtons.addWidget(self.btnLoadna)
        self.loLoadButtons.addStretch()
        # place layout on groupbox
        self.gbLoadButtons = qw.QGroupBox('Load Circuit')
        self.gbLoadButtons.setLayout(self.loLoadButtons)
        # --------------
        # Group <Setting Buttons>
        # --------------
        # create parts
        self.btnSetComm = qw.QPushButton('Connect to Checker')
        self.btnUnsetComm = qw.QPushButton('Disconnect')
        self.btnIGONOFF = qw.QPushButton('IG ON/OFF')
        self.btnSetStart = qw.QPushButton('Start')
        self.btnSetDefault = qw.QPushButton('Set Default')
        self.btnSetInit = qw.QPushButton('Initialization')
        # style
        self.btnIGONOFF.setCheckable(True)
        # call function
        self.btnSetComm.clicked.connect(self.funcManuC2C)
        self.btnUnsetComm.clicked.connect(self.funcManuDisconnect)
        self.btnIGONOFF.clicked[bool].connect(self.funcTestIGONOFF)
        self.btnSetStart.clicked.connect(self.funcManuStart)
        self.btnSetDefault.clicked.connect(self.funcManuDef)
        self.btnSetInit.clicked.connect(self.funcManuInit)
        # place parts on layout
        self.loSetButtons = qw.QGridLayout()
        self.loSetButtons.addWidget(self.btnSetComm,0,0,1,1)
        self.loSetButtons.addWidget(self.btnUnsetComm,1,0,1,1)
        self.loSetButtons.addWidget(self.btnSetInit,2,0,1,1)
        self.loSetButtons.addWidget(self.btnIGONOFF,0,1,1,1)
        self.loSetButtons.addWidget(self.btnSetStart,1,1,1,1)
        self.loSetButtons.addWidget(self.btnSetDefault,2,1,1,1)
        # place layout on groupbox
        self.gbSetButtons = qw.QGroupBox('Control')
        self.gbSetButtons.setLayout(self.loSetButtons)
        # --------------
        # Gronp <Log>
        # --------------
        # create parts
        self.boxLogData = qw.QTextEdit()
        # style
        self.boxLogData.setReadOnly(True)
        # call function
        # place parts on layout
        self.loLogData = qw.QGridLayout()
        self.loLogData.addWidget(self.boxLogData,0,0,5,15)
        # place layout on groupbox
        self.gbLogData = qw.QGroupBox('System Log')
        self.gbLogData.setLayout(self.loLogData)
        # --------------
        # window set
        # --------------
        # place parts
        # V:15 H:15
        self.gridWhole = qw.QGridLayout()
        self.gridWhole.addWidget(self.gbSnroInfo,0,0,10,15)
        self.gridWhole.addWidget(self.gbSQButtons,10,0,3,3)
        self.gridWhole.addWidget(self.gbSATButtons,10,3,3,3)
        self.gridWhole.addWidget(self.gbLoadButtons,10,6,3,3)
        self.gridWhole.addWidget(self.gbSetButtons,11,9,2,6)
        self.gridWhole.addWidget(self.gbLogData,13,0,5,15)
        # display
        self.setLayout(self.gridWhole)
# ====================================
# Main Window
# ====================================
class MainWindow(qw.QWidget):
    # *************
    # init
    # *************
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()
    # *************
    # function
    # *************
    # --------------
    # push close button (x)
    # --------------
    def closeEvent(self, event):
        # on going
        if flgGoing:
            qw.QMessageBox.warning(self, 'ACC', 'Program is on going.\nCan\'t close.')
            event.ignore()
        else:
            close = qw.QMessageBox.question(
                self,
                'ACC',
                'Sure?',
                qw.QMessageBox.Yes | qw.QMessageBox.No
            )
            if close == qw.QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
    # --------------
    # tab change
    # --------------
    def funcTabChanged(self):
        nowTab = self.qtab.currentIndex()
        moveTab = 0 if nowTab==1 else 1
        if flgGoing:
            self.qtab.setTabEnabled(moveTab, False)
            qw.QMessageBox.warning(
                self,
                'ACC',
                'Program is on going.\nCan\'t move from this tab.'
            )
        else:
            # pass
            self.qtab.setTabEnabled(moveTab, True)
    # *************
    # GUI
    # *************
    def initUI(self):
        # --------------
        # common styles
        # --------------
        style = '''
            *{
                font-family: Meiryo
                }
            QGroupBox{
                color: #2A3FFF;
                font-size: 12pt
                }
            QLineEdit{
                font-family: Courier
            }
            QTextEdit{
                font-family: Courier
            }
            QTabWidget::pane{
                border: 1px solid black;
                background: #F0F0F0;
            }
            QTabBar::tab:bottom:selected {
                border-top-color: #F0F0F0;
            }
            '''
        self.setStyleSheet(style)
        # --------------
        # tab
        # --------------
        # place parts on layout
        self.qtab = qw.QTabWidget()
        self.qtab.addTab(ScenarioTab(parent=self), 'Scenario')
        self.qtab.addTab(ManualSetTab(parent=self), 'Manual')
        # call function
        self.qtab.tabBarClicked.connect(self.funcTabChanged)
        # --------------
        # window set
        # --------------
        self.hbox = qw.QHBoxLayout()
        self.hbox.addWidget(self.qtab)
        self.setLayout(self.hbox)
        # display
        self.setGeometry(0, 0, 800, 720)
        self.setSizePolicy(qw.QSizePolicy.Ignored,qw.QSizePolicy.Ignored)
        self.setWindowIcon(qg.QIcon(imgIco))
        self.setWindowTitle('Auto Checker Controller')
# ====================================
# run
# ====================================
# *************
# main function
# *************
def main():
    app = qw.QApplication(sys.argv)
    # *************
    # splash screen
    # *************
    splash_pix = qg.QPixmap(imgSplash)
    splash = qw.QSplashScreen(splash_pix, qc.Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()
    # *************
    # main window
    # *************
    # main_window = ScenarioTab()
    main_window = MainWindow()
    main_window.show()
    splash.finish(main_window)
    sys.exit(app.exec_())
# *************
# call main
# *************
if __name__ == '__main__':
    try:
        main()
    except Exception:
        if traceback.format_exc(2) != 'SystemExit: 0':
            with open(ROOTPATH + '/ErrLog.txt', 'a') as file:
                file.write(traceback.format_exc())
                file.close()
    sys.exit(0)
