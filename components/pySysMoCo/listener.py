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

from PyQt4 import QtCore 
import time
import threading
import traceback
import sys
import scl
import zmq

from google.protobuf import message

class ListenerTask(threading.Thread, QtCore.QObject):
    """ Listerner Task is server thread """
    _stop = threading.Event()
    recvSignal = QtCore.pyqtSignal()
    
    def __init__(self, parent=None, component=None, gate=None):
        QtCore.QObject.__init__(self)
        self.component = str(component)
        self.gate = str(gate)
        threading.Thread.__init__ (self)
        _stop = threading.Event()

    def stop(self):
        self._stop.set()
        
    def stopped(self):
        return self._stop.isSet()
        
    def run(self):
        """ server routine """
        print self.component + ": " + self.gate + ": listener thread startet"
        
        # Prepare our context and Sockets
        map = scl.generate_map(self.component)
        socket = map[self.gate]
        
        while not self.stopped():
            # non-blocking recv to allow app to shutdown
            try:
                string = socket.recv(zmq.NOBLOCK)
                self.string = string # store received string
                self.recvSignal.emit()
            except zmq.ZMQError, e:
                if e.errno == zmq.EAGAIN:
                    pass
                else:
                    raise
            #time.sleep(0.1)
