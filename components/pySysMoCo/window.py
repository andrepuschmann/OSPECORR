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
#import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
import numpy
import time

# import own classes
from listener import ListenerTask
import scl
import application_pb2
import linklayer_pb2
import phy_pb2
import radioconfig_pb2


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

        # neighbortable has 4 columns (address, tx packets, rx packets, rx lost packets)
        self.ui.neighborTable.setColumnCount(4)
        self.ui.neighborTable.setHorizontalHeaderLabels(["Node Address", "TX packets", "RX packets", "Lost packets"])
        self.lastChannel = 0 # to reset last channel
        self.paused = False

        # connect listener
        #self.listenerQosReq.recvSignal.connect(self.updateQosReq)
        #self.listenerLinkStats.recvSignal.connect(self.updateLinkStats)
        self.listenerPhyEvent.recvSignal.connect(self.updatePhy)
        self.listenerLinkLayerEvent.recvSignal.connect(self.updateLinkLayer)

        # start listener threads
        self.listenerPhyEvent.start()
        self.listenerLinkLayerEvent.start()

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
        self.ui.statusChannel1.setStyleSheet("background-color:rgb(140,140,140);"); #grey
        self.ui.statusChannel2.setStyleSheet("background-color:rgb(140,140,140);"); #grey
        self.ui.statusChannel3.setStyleSheet("background-color:rgb(140,140,140);"); #grey
        self.ui.statusChannel4.setStyleSheet("background-color:rgb(140,140,140);"); #grey
        self.ui.statusChannel5.setStyleSheet("background-color:rgb(140,140,140);"); #grey
        self.ui.currentChannel.setText('none')
        self.ui.messageLog.clear()

    def updateMessageLog(self):
        # update message log
        if update.statusMessage:
            self.ui.messageLog.append(update.statusMessage)

        # label for current channel
        self.ui.currentChannel.setText(str(update.channel + 1) + ' (' + update.description + ')')


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
        elif state == phy_pb2.BUSY_CU:
            return "busy classical user"
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

            # update channel activity
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

            # update operating channel, if applicable
            if message.is_active == True:
                self.ui.currentChannel.setText('Ch ' + str(self.displaychannellist[message.channel.f_center] + 1))

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
        for i in self.radioConfig.engines:
            for k in i.components:
                self.ui.componentList.addItem(str(k.name))

        # make first item active
        self.ui.componentList.setCurrentItem(self.ui.componentList.item(0))


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
