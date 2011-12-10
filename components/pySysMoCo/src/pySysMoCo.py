#!/usr/bin/env python
import sys
from PyQt4.Qt import QApplication
from PyQt4 import QtGui
from window import Window

#import time
#from PyQt4 import QtCore, QtGui
#from PyQt4.QtCore import QDateTime
#from qt import *
#from gui_auto import Ui_Form

if __name__ == "__main__":
    app = QApplication(sys.argv)

    ## Look and feel changed to CleanLooks
    QtGui.QApplication.setStyle(QtGui.QStyleFactory.create("Cleanlooks"))
    #QtGui.QApplication.setPalette(QtGui.QApplication.style().standardPalette())
	
    window = Window()
    window.show()
    sys.exit(app.exec_())
