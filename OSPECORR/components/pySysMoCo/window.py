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
#   Copyright 2011 Andre Puschmann <andre.puschmann@tu-ilmenau.de>
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
import application_pb2
import linklayer_pb2
import phy_pb2


class mainDialog(QtGui.QDialog):
    # create listener objects
    listenerFastSensing = ListenerTask(None,'pySysMoCo', 'fastSensingResult')
    listenerFineSensing = ListenerTask(None,'pySysMoCo', 'fineSensingResult')
    listenerChStatusUpdate = ListenerTask(None,'pySysMoCo', 'chStatusUpdate')
    listenerQosReq = ListenerTask(None,'pySysMoCo', 'qosRequirements')
    listenerLinkStats = ListenerTask(None,'pySysMoCo', 'linkStatistics')
    listenerDemodStats = ListenerTask(None,'pySysMoCo', 'demodStatistics')
    listenerMacStats = ListenerTask(None,'pySysMoCo', 'macStatistics')
    
    
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
        # neighbortable has 3 columns (address, tx packets, rx packets)
        self.ui.neighborTable.setColumnCount(3)
        self.ui.neighborTable.setHorizontalHeaderLabels(["Node Address", "TX packets", "RX packets"]) 
        self.lastChannel = 0 # to reset last channel
        self.paused = False
        
        # connect listener
        self.listenerFastSensing.recvSignal.connect(self.updateFastSensing)
        self.listenerFineSensing.recvSignal.connect(self.updateFineSensing)
        self.listenerChStatusUpdate.recvSignal.connect(self.updateChannelStatus)
        self.listenerQosReq.recvSignal.connect(self.updateQosReq)
        self.listenerLinkStats.recvSignal.connect(self.updateLinkStats)
        self.listenerDemodStats.recvSignal.connect(self.updateDemodStats)
        self.listenerMacStats.recvSignal.connect(self.updateMacStats)
        
        # start listener threads
        self.listenerFastSensing.start()
        self.listenerFineSensing.start()
        self.listenerChStatusUpdate.start()
        self.listenerQosReq.start()
        self.listenerLinkStats.start()
        self.listenerDemodStats.start()
        self.listenerMacStats.start()
        

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
        
    def updateFastSensing(self):
        result = phy_pb2.fastSensingResult()
        result.ParseFromString(self.listenerFastSensing.string) # fill protobuf, string is stored in listener object
        
        # update gui
        self.ui.rssiValue.setText(str(result.rssi) + ' dBm')
        
    def updateFineSensing(self):
        result = phy_pb2.fineSensingResult()
        result.ParseFromString(self.listenerFineSensing.string) # fill protobuf, string is stored in listener object
        
        # update fft plot
        if result.fft_bin:
            if not self.paused:
                fft = numpy.array(result.fft_bin._values)
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
    
    def updateChannelStatus(self):
        update = phy_pb2.chStatusUpdate()
        update.ParseFromString(self.listenerChStatusUpdate.string) # fill protobuf, string is stored in listener object
        
        # update channel activity
        objectName = "self.ui.statusChannel" + str(update.channel + 1) # channel map starts with zero
        # print objectName
        objectHandle = eval(objectName)
        if update.currentStatus == update.FREE:
            objectHandle.setStyleSheet("background-color:rgb(0,170,0);");
        elif update.currentStatus == update.SU_BUSY:
            objectHandle.setStyleSheet("background-color:rgb(255,140,0);");
        elif update.currentStatus == update.PU_BUSY:
            objectHandle.setStyleSheet("background-color:rgb(255,0,0);");
        
        # this is a bad hack to grey out the former channel
        if (self.lastChannel != update.channel):
             objectName = "self.ui.statusChannel" + str(self.lastChannel + 1) # channel map starts with zero
             objectHandle = eval(objectName)
             objectHandle.setStyleSheet("background-color:rgb(140,140,140);");
        self.lastChannel = update.channel
        
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
        
    def updateDemodStats(self):
        stats = phy_pb2.demodStatistics()
        stats.ParseFromString(self.listenerDemodStats.string)
        
        # set gui
        self.ui.rssiValue.setText(str(format(stats.rssi, '.2f')) + ' dB')
        self.ui.evmValue.setText(str(format(stats.evm, '.2f')) + ' dB')
        self.ui.ferValue.setText(str(format(stats.fer, '.2f')))
        self.ui.cfoValue.setText(str(format(stats.cfo, '.2f')) + ' f/Fs')

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
    
    def updateMacStats(self):
        stats = linklayer_pb2.macStatistics()
        stats.ParseFromString(self.listenerMacStats.string)
        
        # set gui
        self.ui.rttValue.setText(str(format(stats.rtt, '.2f')) + ' ms')
        self.ui.txQueueValue.setText(str(stats.txQueueSize) + '/' + str(stats.txQueueCapacity))
        self.ui.retransValue.setText(str(stats.txPerPacket))
        self.ui.cwValue.setText(str(stats.minCw) + '/' + str(stats.curCw) + '/' + str(stats.maxCw))
        self.ui.txRateValue.setText(str(stats.txRate))
        
        # update txstats (column 1)
        for nodeStats in stats.txStats:
            row = self.getNeighbortableRow(nodeStats.address)
            self.ui.neighborTable.setItem(row, 1, QtGui.QTableWidgetItem(str(nodeStats.packets)))
        
        # update rxstats (column 2)
        for nodeStats in stats.rxStats:
            row = self.getNeighbortableRow(nodeStats.address)
            self.ui.neighborTable.setItem(row, 2, QtGui.QTableWidgetItem(str(nodeStats.packets)))
            
    def quitWindow(self):
        # ask listener thread to stop
        self.listenerFastSensing.stop()
        self.listenerFineSensing.stop()
        self.listenerChStatusUpdate.stop()
        self.listenerQosReq.stop()
        self.listenerLinkStats.stop()
        self.listenerDemodStats.stop()
        self.listenerMacStats.stop()
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
