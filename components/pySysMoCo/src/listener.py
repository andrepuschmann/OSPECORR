from PyQt4 import QtCore 
import time
import threading
import traceback
import sys
import zmq

from google.protobuf import message

class ListenerTask(threading.Thread, QtCore.QObject):
    """ Listerner Task is server thread """
    _stop = threading.Event()
    recvSignal = QtCore.pyqtSignal()
    context = zmq.Context(1)
    
    def __init__(self, parent=None, address=None): #add type as parameter too
        QtCore.QObject.__init__(self)
        self.zmqAddress = str(address)
        print self.zmqAddress
        threading.Thread.__init__ (self)
        _stop = threading.Event()

    def stop(self):
        self._stop.set()
        
    def stopped(self):
        return self._stop.isSet()
        
    def run(self):
        """ server routine """
        print "listener thread startet"
        
        # Prepare our context and Sockets
        context = zmq.Context(1)
        
        # Socket to talk to clients
        socket = self.context.socket(zmq.SUB)
        socket.connect(self.zmqAddress)
        socket.setsockopt(zmq.SUBSCRIBE,'')
        
        while not self.stopped():
            # non-blocking recv to allow pysense to shutdown
            try:
                string = socket.recv(zmq.NOBLOCK)
                self.string = string # store received string
                self.recvSignal.emit()
            except zmq.ZMQError, e:
                if e.errno == zmq.EAGAIN:
                    pass
                else:
                    raise
            time.sleep(0.1)
