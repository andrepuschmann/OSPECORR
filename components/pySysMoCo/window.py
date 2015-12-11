# -*- coding: UTF-8 -*-
#
#   This file is part of OSPECOR².
#
#   OSPECOR² is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   OSPECOR² is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with OSPECOR².  If not, see <http://www.gnu.org/licenses/>.
#
#   Copyright 2011-2012 Andre Puschmann <andre.puschmann@tu-ilmenau.de>
#

from PyQt4.QtCore import Qt, SIGNAL
from PyQt4.QtGui import *
from PyQt4 import QtGui, uic
from PyQt4 import Qwt5 as Qwt
from PyQt4 import Qt
from PyQt4.Qwt5.anynumpy import *
from PyQt4 import QtGui, QtCore
#import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
from netifaces import interfaces, ifaddresses, AF_INET
import numpy
import time

# import own classes
from listener import ListenerTask
from activitycontroller import ActivityController
from radioconfig import RadioConfig
import scl
import application_pb2
import linklayer_pb2
import phy_pb2
import radioconfig_pb2
from controller import RadioOptimizer
from client import ClientOptimizer
import threading
import thread
import signal
import os

class mainDialog(QtGui.QDialog):
    # create listener objects
    #listenerQosReq = ListenerTask(None,'pySysMoCo', 'qosRequirements')
    #listenerLinkStats = ListenerTask(None,'pySysMoCo', 'linkStatistics')
    listenerPhyEvent = ListenerTask(None,'pySysMoCo', 'phyevent')
    listenerLinkLayerEvent = ListenerTask(None,'pySysMoCo', 'linklayerevent')
    radioConfig = radioconfig_pb2.RadioConfig()
    displaychannellist = {}

    def __init__(self):
        QtGui.QDialog.__init__(self)

        # Set up the user interface from Designer.
        self.ui = uic.loadUi("gui.ui")
        self.ui.show()

        # setup GUI slots and signals
        self.ui.plot = FftPlot()
        self.ui.plot.resize(620, 440)
        self.ui.plot.setParent(self.ui.qwtWidget)
        self.ui.dpi = 100
        self.ui.fig = Figure((6.5, 4.0), dpi=self.ui.dpi)
        self.ui.canvas = FigureCanvas(self.ui.fig)
        self.ui.canvas.setParent(self.ui.mplWidget)
        self.ui.axes = self.ui.fig.add_subplot(111)
        self.ui.mpl_toolbar = NavigationToolbar(self.ui.canvas, self.ui.mplToolbar)
        self.ui.testButton.clicked.connect(self.toggleChannelColors)
        self.ui.clearButton.clicked.connect(self.clearButtonClicked)
        self.ui.closeButton.clicked.connect(self.quitWindow)
        self.ui.pauseButton.clicked.connect(self.pauseButtonClicked)
        # Radio Configuration Tab
        self.ui.getRadioButton.clicked.connect(self.getRadio)
        self.ui.applyChangesButton.clicked.connect(self.reconfigRadio)
        self.ui.componentList.currentItemChanged.connect(self.updateParamTable)
        self.ui.parameterTable.setHorizontalHeaderLabels(["Name", "Value"])
        # Activity control tab
        self.ui.automaticButton.clicked.connect(self.automaticButtonClicked)
        self.ui.manualButton.clicked.connect(self.manualButtonClicked)
        self.ui.ch1Button.clicked.connect(self.channelButtonClicked)
        self.ui.ch2Button.clicked.connect(self.channelButtonClicked)
        self.ui.ch3Button.clicked.connect(self.channelButtonClicked)
        self.manualButtonClicked() # initialze GUI in manual mode
        # neighbortable has 4 columns (address, tx packets, rx packets, rx lost packets)
        self.ui.neighborTable.setColumnCount(4)
        self.ui.neighborTable.setHorizontalHeaderLabels(["Node Address", "TX packets", "RX packets", "Lost packets"])
        self.lastChannel = 0 # to reset last channel
        self.paused = False

        # connect and start listener
        self.listenerPhyEvent.recvSignal.connect(self.updatePhy)
        self.listenerLinkLayerEvent.recvSignal.connect(self.updateLinkLayer)
        self.listenerPhyEvent.start()
        self.listenerLinkLayerEvent.start()
        
        self.optimize = True
        #Radio optimizer code
        #Client code
        self.ui.Start_Opt_Client.clicked.connect(self.startOptClient)
        self.cliOptimizer = ClientOptimizer()
         
        # create list of available network interfaces
        addresses = []
        for ifaceName in interfaces():
            addr = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
            #addresses.append(self.tr('%s: %s' % (ifaceName, ', '.join(addr))))
            addresses.append(self.tr('%s' % (addr[0])))
        #print addresses
        # show them in gui
        """
        self.ui.clientControlIp.clear()
        self.ui.clientControlIp.addItems(addresses)
        self.ui.clientDataIp.clear()
        self.ui.clientDataIp.addItems(addresses)
        """
        self.ui.serverControlIp.clear()
        self.ui.serverControlIp.addItems(addresses)
        self.ui.serverDataIp.clear()
        self.ui.serverDataIp.addItems(addresses)

        self.ui.cli_ControlIp.clear()
        self.ui.cli_ControlIp.addItems(addresses)
        self.ui.cli_DataIp.clear()
        self.ui.cli_DataIp.addItems(addresses)

        #Controller code
        self.start_opt = True
        
        self.ui.getRadioButton_opt.clicked.connect(self.getRadio)
        self.ui.componentList_opt.currentItemChanged.connect(self.updateParamTable_opt)
        self.ui.applyChangesButton_opt.clicked.connect(self.reconfigRadio_opt)
        self.ui.parameterTable_opt.setHorizontalHeaderLabels(["Name", "Value", "Optimize", "Range"])
        self.ui.radioOptimizer_start.clicked.connect(self.optimizeRadio_start)
        self.ui.radioOptimizer_stop.clicked.connect(self.optimizeRadio_stop)
        self.ui.UpdateOptimizerPlot.clicked.connect(self.updateOptimizerPlot)
        self.radioOptimizer = RadioOptimizer(self.radioConfig)
        #Plot init for the optimizer graph
        self.ui.optimizer_plot = self.radioOptimizer.add_plot()
        self.ui.optimizer_plot.resize(620, 440)
        self.ui.optimizer_plot.setParent(self.ui.qwtWidgetOptimizer)
        signal.signal(signal.SIGALRM, self.receive_optimizer_alarm)

        file_name = 'iris_default_configuration.xml'
        tree = Config.parse(file_name)
        self.cliConfig = tree.getroot()
        self.ui.componentList_cli.currentItemChanged.connect(self.updateParamTable_cli)
        self.ui.parameterTable_cli.setHorizontalHeaderLabels(["Name", "Value", "Optimize", "Range"])
        self.ui.componentList_cli.clear()
        
    ''' This function tries to initialize the activity thread object
        it's always save to call this, the object is only created once
    '''
    def tryInitActivityObject(self):
        print "initactivityobject"
        
        try:
            if self.activityThread.isAlive():
                print "thread exists already .."
                probs = self.getProbabilities()
                self.activityThread.update_probabilites(probs)
                return True
        except:
            pass
        
        # prepare channel list
        channellist = self.displaychannellist
        #channellist = [2400000000L, 2404000000L, 2408000000L]
        print channellist
        
        if not self.displaychannellist:
            print "No channels specified so far, abort."
            return False
        
        # prepare propabilities
        probs = self.getProbabilities()
        
        # start thread
        print "Start thread .."
        avg_holdtime = float(self.ui.avgHoldTime.text())
        min_holdtime = float(self.ui.minHoldTime.text())
        engineName = self.ui.engineName.text()
        componentName = self.ui.componentName.text()
        
        try:
            self.activityThread = ActivityController(self.displaychannellist, probs, avg_holdtime, min_holdtime, engineName, componentName)
            self.activityThread.start()
            return True
        except:
            pass


    def getProbabilities(self):
        probs = []
        probs.append(float(self.ui.propCh1.text()))
        probs.append(float(self.ui.propCh2.text()))
        probs.append(float(self.ui.propCh3.text()))
        return probs

    def automaticButtonClicked(self):
        print "AutomaticButton clicked"
        self.tryInitActivityObject()
        
        # enable widgets as needed
        self.ui.ch1Button.setEnabled(False)
        self.ui.ch2Button.setEnabled(False)
        self.ui.ch3Button.setEnabled(False)
        self.ui.propBox.setEnabled(True)
        self.ui.poissonBox.setEnabled(True)
        # resume thread
        try:
            self.activityThread.resume()
        except:
            pass
        
        
    def manualButtonClicked(self):
        print "manualButtonClicked"
        # enable widgets as needed
        self.ui.propBox.setEnabled(False)
        self.ui.poissonBox.setEnabled(False)
        self.ui.ch1Button.setEnabled(True)
        self.ui.ch2Button.setEnabled(True)
        self.ui.ch3Button.setEnabled(True)
        # pause thread
        try:
            self.activityThread.pause()
        except:
            pass
          
    
    def channelButtonClicked(self):
        print "channelButtonClicked"
        if self.tryInitActivityObject() == False:
            print "init failed"
            return
        
        engineName = self.ui.engineName.text()
        componentName = self.ui.componentName.text()            
        config = RadioConfig(engineName, componentName)

        if self.ui.ch1Button.isChecked():
            print "channel 1 cliked"
            index = 0
        elif self.ui.ch2Button.isChecked():
            print "channel 2 cliked"
            index = 1
        elif self.ui.ch3Button.isChecked():
            print "channel 3 cliked"
            index = 2

        # hack to get key for specific value
        for key, value in self.displaychannellist.items():
            if value == index:
                print "freq is: %s" % key
                config.tuneRadio(key)

    def pauseButtonClicked(self):
        self.paused = not self.paused
        label = "Resume" if self.paused else "Pause"
        self.ui.pauseButton.setText(label)

    def toggleChannelColors(self):
        self.ui.statusChannel1.setStyleSheet("background-color:rgb(0,170,0);");
        #self.ui.statusChannel2.setStyleSheet("background-color:rgb(255,140,0);");
        #self.ui.statusChannel3.setStyleSheet("background-color:rgb(255,0,0);");
        #self.ui.statusChannel4.setStyleSheet("background-color:rgb(0,170,0);");
        #self.ui.statusChannel5.setStyleSheet("background-color:rgb(140,140,140);"); #grey
        print "Hello, World!"

    def clearButtonClicked(self):
        self.ui.statusChannel0.setStyleSheet("background-color:rgb(140,140,140);"); #grey
        self.ui.statusChannel1.setStyleSheet("background-color:rgb(140,140,140);"); #grey
        self.ui.statusChannel2.setStyleSheet("background-color:rgb(140,140,140);"); #grey
        self.ui.statusChannel3.setStyleSheet("background-color:rgb(140,140,140);"); #grey
        self.ui.statusChannel4.setStyleSheet("background-color:rgb(140,140,140);"); #grey
        self.ui.channelRadio0.setText('none')
        self.ui.channelRadio1.setText('none')
        self.ui.messageLog.clear()

    def updateMessageLog(self):
        # update message log
        if update.statusMessage:
            self.ui.messageLog.append(update.statusMessage)

        # label for current channel
        self.ui.channelRadio0.setText(str(update.channel + 1) + ' (' + update.description + ')')


    def updateQosReq(self):
        requirements = application_pb2.qosRequirements()
        requirements.ParseFromString(self.listenerQosReq.string)

        # set gui
        self.ui.dataRateValue.setText(str(requirements.dataRate) + ' kB/s')
        self.ui.delayValue.setText(str(requirements.delay) + ' ms')
        self.ui.losslessValue.setChecked(requirements.featureLossless)


    def updateLinkStats(self):
        stats = application_pb2.linkStatistics()
        stats.ParseFromString(self.listenerLinkStats.string)

        # set gui
        self.ui.upwardThroughputValue.setText(str(format(stats.upwardThroughput, '.2f')) + ' kB/s')
        self.ui.upwardPacketSizeValue.setText(str(stats.upwardPacketSize) + ' byte')
        self.ui.downwardThroughputValue.setText(str(format(stats.downwardThroughput, '.2f')) + ' kB/s')
        self.ui.downwardPacketSizeValue.setText(str(stats.downwardPacketSize) + ' byte')


    def stateToString(self, state):
        if state == phy_pb2.FREE:
            return "free"
        elif state == phy_pb2.BUSY_SU:
            return "busy"
        elif state == phy_pb2.BUSY_PU:
            return "PU active"
        elif state == phy_pb2.UNKNOWN:
            return "unknown"


    def setChannelState(self, message):
        # update channel state
        if (message.channel.f_center not in self.displaychannellist) and (len(self.displaychannellist) <= 5):
            print "Add new channel to display list."
            self.displaychannellist[message.channel.f_center] = len(self.displaychannellist)
        else:
            if len(self.displaychannellist) > 5:
                print "Maximum number of channels to display reached, abort."
                return

        if message.channel.f_center in self.displaychannellist:
            # update channel
            objectName = "self.ui.freqChannel" + str(self.displaychannellist[message.channel.f_center])
            #print objectName
            objectHandle = eval(objectName)
            objectHandle.setText(str(message.channel.f_center/1000000) + ' MHz') # channel map starts with zero

            # update operating channel, if applicable
            if message.is_active == True:
                objectName = "self.ui.channelRadio" + str(message.trx)
                objectHandle = eval(objectName)
                objectHandle.setText('Channel ' + str(self.displaychannellist[message.channel.f_center] + 1))
            
            # update channel activity for TRx 0 only
            if message.trx == 0:            
                objectName = "self.ui.statusChannel" + str(self.displaychannellist[message.channel.f_center])
                #print objectName
                objectHandle = eval(objectName)
                if message.state == phy_pb2.FREE:
                    objectHandle.setStyleSheet("background-color:rgb(0,170,0);");
                elif message.state == phy_pb2.BUSY_SU:
                    objectHandle.setStyleSheet("background-color:rgb(255,140,0);");
                elif message.state == phy_pb2.BUSY_PU:
                    objectHandle.setStyleSheet("background-color:rgb(255,0,0);");
                elif message.state == phy_pb2.UNKNOWN:
                    objectHandle.setStyleSheet("background-color:rgb(140,140,140);");

            return

    def updatePhy(self):
        stats = phy_pb2.PhyMessage()
        stats.ParseFromString(self.listenerPhyEvent.string)

        if stats.HasField('channel'):
            print "Stats contains channel specific information."
            self.setChannelState(stats)

        # set gui
        self.ui.rssiValue.setText(str(format(stats.rssi, '.2f')) + ' dB')
        self.ui.lastRssiValue.setText(str(format(stats.last_rx_rssi, '.2f')) + ' dB')
        self.ui.thresholdValue.setText(str(format(stats.threshold, '.2f')) + ' dB')
        self.ui.channelStateValue.setText(self.stateToString(stats.state))
        self.ui.evmValue.setText(str(format(stats.evm, '.2f')) + ' dB')
        self.ui.ferValue.setText(str(format(stats.fer, '.2f')))
        self.ui.cfoValue.setText(str(format(stats.cfo, '.2f')) + ' f/Fs')

        # update fft plot
        if stats.fft_bin:
            if not self.paused:
                fft = numpy.array(stats.fft_bin._values)
                # pyqwt display
                self.ui.plot.plotFft(fft)
                # matplotlib display
                #self.axes.set_axis_bgcolor('black')
                #self.axes.clear()
                #self.axes.grid(True)
                #self.axes.plot(range(len(fft)), fft, '-', label='what')
                #self.axes.set_ylabel('Power in dBm')
                #self.axes.axis([0, 512, -140, -70])
                #self.canvas.draw()

        # update the radio optimizer
        if self.optimize:
            self.cliOptimizer.accumulate(stats)

    def getRadio(self):

        map = scl.generate_map("pySysMoCo")
        radioconfigcontrol = map["radioconfcontrol"]

        #Create request for getting ratio
        request = radioconfig_pb2.RadioConfigControl()
        request.type = radioconfig_pb2.REQUEST
        request.command = radioconfig_pb2.GET_RADIO_CONFIG
        string = request.SerializeToString()
        radioconfigcontrol.send(string)

        #Create Reply
        reply = radioconfig_pb2.RadioConfigControl()
        string = radioconfigcontrol.recv()
        reply.ParseFromString(string)
        # set radioconfig for later reference
        self.radioConfig = reply.radioconf

        # FIXME: change to tree view and add engines too
        # update component list
        self.ui.componentList.clear()
        self.ui.componentList_opt.clear()
        for i in self.radioConfig.engines:
            for k in i.components:
                self.ui.componentList.addItem(str(k.name))
                self.ui.componentList_opt.addItem(str(k.name))

        # make first item active
        self.ui.componentList.setCurrentItem(self.ui.componentList.item(0))
        self.ui.componentList_opt.setCurrentItem(self.ui.componentList_opt.item(0))
        
        #Call radio optimizer to fill its init config
        if self.optimize:
            self.radioOptimizer.update_config(self.radioConfig)

    #Module to optimize the radio
    
    #Start the client
    def startOptClient(self):
        if self.optimize:
            # get GUI parameters
            clientControlIp = self.ui.cli_ControlIp.currentText()
            clientDataIp = self.ui.cli_DataIp.currentText()

            self.cliOptimizer.updateConfiguration(clientControlIp, clientDataIp)
            self.cliOptimizer.start()
        
    def optimizeRadio_start(self):
        if self.optimize:

            # get GUI parameters
            """
            clientControlIp = self.ui.clientControlIp.currentText()
            clientDataIp = self.ui.clientDataIp.currentText()

            serverControlIp = self.ui.serverControlIp.text()
            serverDataIp = self.ui.serverDataIp.text()
            """
            clientControlIp = self.ui.clientControlIp.text()
            clientDataIp = self.ui.clientDataIp.text()

            serverControlIp = self.ui.serverControlIp.currentText()
            serverDataIp = self.ui.serverDataIp.currentText()

            self.radioOptimizer.updateConfiguration(clientControlIp, clientDataIp, serverControlIp, serverDataIp)
            
            #Enable the the optimizer to run
            self.radioOptimizer.start_optimizer()
            #Start the thread only once
            if self.start_opt: 
                #Start the thread
                self.radioOptimizer.start()
                self.start_opt = False

    def optimizeRadio_stop(self):
        if self.optimize:
            #Disable the optimizer
            self.radioOptimizer.stop_optimizer()
                        
    #Updates the plot, when the button is clicked        
    def updateOptimizerPlot(self):
        if self.optimize:
            #print 'Optimizer Plot...'
            self.radioOptimizer.opt_plot.plotOptimizer(self.radioOptimizer.x_vals, self.radioOptimizer.y_vals, self.radioOptimizer.best_x, self.radioOptimizer.best_y)
            #self.ui.best_config.setText(self.radioOptimizer.best_ind)
            #print self.radioOptimizer.best_ind
            self.ui.best_config.clear()
            for i in self.radioOptimizer.best_ind:
                    self.ui.best_config.addItem(str(i).replace(":", ", "))
            
    def receive_optimizer_alarm(self, signum, stack):
        if self.optimize:
            print '##Receive_optimizer_alarm'
            self.radioOptimizer.opt_plot.plotOptimizer(self.radioOptimizer.x_vals, self.radioOptimizer.y_vals, self.radioOptimizer.best_x, self.radioOptimizer.best_y)
            #signal.alarm(1)
            
    
    def updateParamTable_opt(self):
        #print "updateParamTable()"
        if(self.radioConfig != 0):
            # clear table
            self.ui.parameterTable_opt.clearContents()
            self.ui.parameterTable_opt.setRowCount(0)
            # get current component
            currentItem = self.ui.componentList_opt.currentItem().text()
            for engine in self.radioConfig.engines:
                for component in engine.components:
                    if currentItem == component.name:
                        for param in component.parameters:
                            numRows = self.ui.parameterTable_opt.rowCount()
                            self.ui.parameterTable_opt.insertRow(numRows)
                            self.ui.parameterTable_opt.setItem(numRows, 0, QTableWidgetItem(param.name))
                            self.ui.parameterTable_opt.setItem(numRows, 1, QTableWidgetItem(param.value))                          
                            #Set the check boxes
                            item = QTableWidgetItem("")
                            item.setCheckState(QtCore.Qt.Unchecked);
                            self.ui.parameterTable_opt.setItem(numRows, 2, item);
                            #Fill the table with the default optimization values provided by default_list
                            for x in self.radioOptimizer.default_list:
                                if component.name == x.component and param.name == x.parameter:
                                    self.ui.parameterTable_opt.setItem(numRows, 3, QTableWidgetItem(x.values))


    def reconfigRadio_opt(self):
        print "reconfigRadio called"
        map = scl.generate_map("pySysMoCo")
        radioconfigcontrol = map["radioconfcontrol"]

        #Create request for radio reconfiguration
        request = radioconfig_pb2.RadioConfigControl()
        request.type = radioconfig_pb2.REQUEST
        request.command = radioconfig_pb2.SET_RADIO_CONFIG

        # get selected component and add to reconf request
        currentComponent = self.ui.componentList_opt.currentItem()
        print currentComponent.text()

        #Set the GA values
        self.radioOptimizer.NGEN = int(self.ui.NGEN.text())
        self.radioOptimizer.NIND = int(self.ui.NIND.text())
        self.radioOptimizer.CXPB = float(self.ui.CXPB.text())
        self.radioOptimizer.MUTPB = float(self.ui.MUTPB.text())
        
        print "GA: ", self.ui.NGEN.text(), self.ui.NIND.text(), self.ui.CXPB.text(), self.ui.MUTPB.text()
        # add engine and just use name of first
        newEngine = request.radioconf.engines.add()

        # find the engine the component lives in and set name
        for engine in self.radioConfig.engines:
            for component in engine.components:
                if component.name == currentComponent.text():
                    # create new engine in request object
                    newEngine.name = engine.name

        newComponent = newEngine.components.add()
        newComponent.name = str(currentComponent.text())

        # add all parameter that have changed
        # FIXME: compare with self.radioConfig and really just update if changes
        numRows = self.ui.parameterTable_opt.rowCount()
        for row in xrange(0, numRows):
            newParameter = newComponent.parameters.add()
            # name is column 0
            newParameter.name = str(self.ui.parameterTable_opt.item(row, 0).text())
            # value is column 1
            newParameter.value = str(self.ui.parameterTable_opt.item(row, 1).text())

            if self.optimize and self.ui.parameterTable_opt.item(row, 2).checkState() == QtCore.Qt.Checked:
                self.radioOptimizer.prepare_config(newEngine.name, newComponent.name, newParameter.name, str(self.ui.parameterTable_opt.item(row, 3).text()) )

        #send request
        string = request.SerializeToString()
        radioconfigcontrol.send(string)
        #wait for reply, fixme: check result
        string = radioconfigcontrol.recv()

    def updateParamTable(self):
        #print "updateParamTable()"
        if(self.radioConfig != 0):
            # clear table
            self.ui.parameterTable.clearContents()
            self.ui.parameterTable.setRowCount(0)
            # get current component
            currentItem = self.ui.componentList.currentItem().text()
            for engine in self.radioConfig.engines:
                for component in engine.components:
                    if currentItem == component.name:
                        for param in component.parameters:
                            numRows = self.ui.parameterTable.rowCount()
                            self.ui.parameterTable.insertRow(numRows)
                            self.ui.parameterTable.setItem(numRows, 0, QTableWidgetItem(param.name))
                            self.ui.parameterTable.setItem(numRows, 1, QTableWidgetItem(param.value))


    def reconfigRadio(self):
        print "reconfigRadio called"
        map = scl.generate_map("pySysMoCo")
        radioconfigcontrol = map["radioconfcontrol"]

        #Create request for radio reconfiguration
        request = radioconfig_pb2.RadioConfigControl()
        request.type = radioconfig_pb2.REQUEST
        request.command = radioconfig_pb2.SET_RADIO_CONFIG

        # get selected component and add to reconf request
        currentComponent = self.ui.componentList.currentItem()
        print currentComponent.text()

        # add engine and just use name of first
        newEngine = request.radioconf.engines.add()

        # find the engine the component lives in and set name
        for engine in self.radioConfig.engines:
            for component in engine.components:
                if component.name == currentComponent.text():
                    # create new engine in request object
                    newEngine.name = engine.name

        newComponent = newEngine.components.add()
        newComponent.name = str(currentComponent.text())

        # add all parameter that have changed
        # FIXME: compare with self.radioConfig and really just update if changes
        numRows = self.ui.parameterTable.rowCount()
        for row in xrange(0, numRows):
            newParameter = newComponent.parameters.add()
            # name is column 0
            newParameter.name = str(self.ui.parameterTable.item(row, 0).text())
            # value is column 1
            newParameter.value = str(self.ui.parameterTable.item(row, 1).text())

        #send request
        string = request.SerializeToString()
        radioconfigcontrol.send(string)
        #wait for reply, fixme: check result
        string = radioconfigcontrol.recv()



    def getNeighbortableRow(self, address):
        # find address in table and set row if found
        numRows = self.ui.neighborTable.rowCount()
        row = -1
        i = 0
        while i < numRows:
            if self.ui.neighborTable.item(i,0).text() == address:
                #print "Address found"
                row = i
            i += 1
        if row == -1:
            print "Neighbor address " + address + " not found, add it"
            self.ui.neighborTable.insertRow(numRows)
            self.ui.neighborTable.setItem(numRows, 0, QtGui.QTableWidgetItem(address))
            row = numRows
        return row

    def updateLinkLayer(self):
        stats = linklayer_pb2.LinkLayerMessage()
        stats.ParseFromString(self.listenerLinkLayerEvent.string)

        # set gui
        self.ui.rttValue.setText(str(format(stats.mac.avg_rtt, '.2f')) + ' ms')
        self.ui.txQueueValue.setText(str(stats.mac.tx_queue_size) + '/' + str(stats.mac.tx_queue_capacity))
        self.ui.retransValue.setText(str(stats.mac.tx_retries_per_packet))
        self.ui.cwValue.setText(str(stats.mac.min_cw) + '/' + str(stats.mac.current_cw) + '/' + str(stats.mac.max_cw))
        self.ui.txRateValue.setText(str(stats.mac.tx_rate))

        # update txstats (column 1)
        for nodeStats in stats.mac.tx_stats:
            row = self.getNeighbortableRow(nodeStats.address)
            self.ui.neighborTable.setItem(row, 1, QtGui.QTableWidgetItem(str(nodeStats.packets)))

        # update rxstats (column 2)
        for nodeStats in stats.mac.rx_stats:
            row = self.getNeighbortableRow(nodeStats.address)
            self.ui.neighborTable.setItem(row, 2, QtGui.QTableWidgetItem(str(nodeStats.packets)))

        # update rxstatslost (column 3)
        for nodeStats in stats.mac.rx_stats_lost:
            row = self.getNeighbortableRow(nodeStats.address)
            self.ui.neighborTable.setItem(row, 3, QtGui.QTableWidgetItem(str(nodeStats.packets)))

    def quitWindow(self):
        # ask listener thread to stop
        #self.listenerFastSensing.stop()
        #self.listenerFineSensing.stop()
        #self.listenerChStatusUpdate.stop()
        #self.listenerQosReq.stop()
        #self.listenerLinkStats.stop()
        try:
            self.activityThread.pause()
            self.activityThread.stop()
        except:
            pass
        self.cliOptimizer.stop()
        self.radioOptimizer.stop()
        self.listenerPhyEvent.stop()
        self.listenerLinkLayerEvent.stop()
        self.close()



class DataPlot(Qwt.QwtPlot):

    def __init__(self, *args):
        Qwt.QwtPlot.__init__(self, *args)

        self.setCanvasBackground(Qt.Qt.white)
        self.alignScales()

        # Initialize data
        self.x = arange(0.0, 100.1, 0.5)
        self.y = zeros(len(self.x), Float)
        self.z = zeros(len(self.x), Float)

        self.setTitle("A Moving QwtPlot Demonstration")
        self.insertLegend(Qwt.QwtLegend(), Qwt.QwtPlot.BottomLegend);

        self.curveR = Qwt.QwtPlotCurve("Data Moving Right")
        self.curveR.attach(self)
        self.curveL = Qwt.QwtPlotCurve("Data Moving Left")
        self.curveL.attach(self)

        self.curveL.setSymbol(Qwt.QwtSymbol(Qwt.QwtSymbol.Ellipse,
                                        Qt.QBrush(),
                                        Qt.QPen(Qt.Qt.yellow),
                                        Qt.QSize(7, 7)))

        self.curveR.setPen(Qt.QPen(Qt.Qt.red))
        self.curveL.setPen(Qt.QPen(Qt.Qt.blue))

        mY = Qwt.QwtPlotMarker()
        mY.setLabelAlignment(Qt.Qt.AlignRight | Qt.Qt.AlignTop)
        mY.setLineStyle(Qwt.QwtPlotMarker.HLine)
        mY.setYValue(0.0)
        mY.attach(self)

        self.setAxisTitle(Qwt.QwtPlot.xBottom, "Time (seconds)")
        self.setAxisTitle(Qwt.QwtPlot.yLeft, "Values")

        self.startTimer(50)
        self.phase = 0.0

    def alignScales(self):
        self.canvas().setFrameStyle(Qt.QFrame.Box | Qt.QFrame.Plain)
        self.canvas().setLineWidth(1)
        for i in range(Qwt.QwtPlot.axisCnt):
            scaleWidget = self.axisWidget(i)
            if scaleWidget:
                scaleWidget.setMargin(0)
            scaleDraw = self.axisScaleDraw(i)
            if scaleDraw:
                scaleDraw.enableComponent(
                    Qwt.QwtAbstractScaleDraw.Backbone, False)

class FftPlot(Qwt.QwtPlot):

    def __init__(self, parent=None):
        Qwt.QwtPlot.__init__(self)
        self.setAxisTitle(Qwt.QwtPlot.xBottom, 'Frequency [Hz]');
        self.setAxisTitle(Qwt.QwtPlot.yLeft, "Power in dBm")
        self.setCanvasBackground(Qt.Qt.black)
        self.spectrumCurve = Qwt.QwtPlotCurve("FFT")
        self.spectrumCurve.attach(self)
        self.spectrumCurve.setPen(Qt.QPen(Qt.Qt.blue))
        self.spectrumCurve.setYAxis(Qwt.QwtPlot.yLeft)
        self.setAxisScale( Qwt.QwtPlot.xBottom, 0.0, 512.0)
        self.setAxisScale( Qwt.QwtPlot.yLeft, -140.0, -60.0)

    def plotFft(self, values):
        self.spectrumCurve.setData(range(len(values)), values)
        self.replot()
