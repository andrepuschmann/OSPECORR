from PyQt4.QtCore import Qt, SIGNAL
from PyQt4.QtGui import *
from gui_auto import Ui_Form
from listener import ListenerTask
#from spectrum import DataHolder
#from spectrum import testClass
from PyQt4 import Qwt5 as Qwt
from PyQt4 import Qt

from PyQt4.Qwt5.anynumpy import *

# protocol buffers
import nodecontroller_pb2
import application_pb2

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
import numpy

import time


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


class Window(QWidget, Ui_Form):
              
    listener = ListenerTask(None,'ipc:///tmp/simplesense_data.pipe')
    listenerApplication = ListenerTask(None,'ipc:///tmp/scl_application_qos.pipe')
    
    #listener 
    
    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self.listener.start()
        self.listenerApplication.start()
        
        self.plot = FftPlot()       
        self.plot.resize(620, 440)
        self.plot.setParent(self.qwtWidget)
        self.dpi = 100
        self.fig = Figure((6.5, 4.0), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.mplWidget)
        self.axes = self.fig.add_subplot(111)
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.mplToolbar)
        self.testButton.clicked.connect(self.toggleChannelColors)
        self.clearButton.clicked.connect(self.clearButtonClicked)
        self.closeButton.clicked.connect(self.quitWindow)
        self.pauseButton.clicked.connect(self.pauseButtonClicked)
        self.listener.recvSignal.connect(self.updateGui)
        self.listenerApplication.recvSignal.connect(self.updateGuiApplication)
        self.lastChannel = 0 # to reset last channel
        self.paused = False
        #QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('cleanlooks'))
    
    def toggleChannelColors(self):
        self.statusChannel1.setStyleSheet("background-color:rgb(0,170,0);");
        self.statusChannel2.setStyleSheet("background-color:rgb(255,140,0);");
        self.statusChannel3.setStyleSheet("background-color:rgb(255,0,0);");
        self.statusChannel4.setStyleSheet("background-color:rgb(0,170,0);");
        self.statusChannel5.setStyleSheet("background-color:rgb(140,140,140);"); #grey
        print "Hello, World!"
        
    def pauseButtonClicked(self):
        self.paused = not self.paused
        label = "Resume" if self.paused else "Pause"
        self.pauseButton.setText(label)

    def clearButtonClicked(self):
        self.statusChannel1.setStyleSheet("background-color:rgb(140,140,140);"); #grey
        self.statusChannel2.setStyleSheet("background-color:rgb(140,140,140);"); #grey
        self.statusChannel3.setStyleSheet("background-color:rgb(140,140,140);"); #grey
        self.statusChannel4.setStyleSheet("background-color:rgb(140,140,140);"); #grey
        self.statusChannel5.setStyleSheet("background-color:rgb(140,140,140);"); #grey
        self.currentChannel.setText('none')
        self.messageLog.clear()
    
    def updateGui(self):
        statusUpdate = nodecontroller_pb2.statusUpdate()
        statusUpdate.ParseFromString(self.listener.string) # fill protobuf, string is stored in listener object
        
        # update channel activity
        objectName = "self.statusChannel" + str(statusUpdate.channel + 1) # channel map starts with zero
        # print objectName
        objectHandle = eval(objectName)
        if statusUpdate.currentStatus == statusUpdate.FREE:
            objectHandle.setStyleSheet("background-color:rgb(0,170,0);");
        elif statusUpdate.currentStatus == statusUpdate.SU_BUSY:
            objectHandle.setStyleSheet("background-color:rgb(255,140,0);");
        elif statusUpdate.currentStatus == statusUpdate.PU_BUSY:
            objectHandle.setStyleSheet("background-color:rgb(255,0,0);");
        
        # this is a bad hack to grey out the former channel
        if (self.lastChannel != statusUpdate.channel):
             objectName = "self.statusChannel" + str(self.lastChannel + 1) # channel map starts with zero
             objectHandle = eval(objectName)
             objectHandle.setStyleSheet("background-color:rgb(140,140,140);");
        self.lastChannel = statusUpdate.channel
        
        # update message log
        if statusUpdate.statusMessage:
            self.messageLog.append(statusUpdate.statusMessage)
        
        # label for current channel
        self.currentChannel.setText(str(statusUpdate.channel + 1) + ' (' + statusUpdate.description + ')')
        
        # fft plot
        if statusUpdate.fft_bin:
            if not self.paused:
                fft = numpy.array(statusUpdate.fft_bin._values)
                # pyqwt display
                self.plot.plotFft(fft)
                
                # matplotlib display
                #self.axes.set_axis_bgcolor('black')
                #self.axes.clear()        
                #self.axes.grid(True)
                #self.axes.plot(range(len(fft)), fft, '-', label='what')
                #self.axes.set_ylabel('Power in dBm')
                #self.axes.axis([0, 512, -140, -70])
                #self.canvas.draw()

    def updateGuiApplication(self):
        requirements = application_pb2.qosRequirements()
        requirements.ParseFromString(self.listenerApplication.string) # fill protobuf, string is stored in listener object
        
        # set gui
        self.dataRateValue.setText(str(requirements.dataRate) + ' kB/s')
        self.delayValue.setText(str(requirements.delay) + ' ms')
        self.losslessValue.setChecked(requirements.featureLossless)
    
    def quitWindow(self):
        self.listener.stop() # ask listener thread to stop
        self.close()
