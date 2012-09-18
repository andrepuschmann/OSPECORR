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
#import threading
#import traceback
#import sys
import scl
import zmq
import drm_pb2

from google.protobuf import message

class DrmHelper(QtCore.QObject):
    """ Listerner Task is server thread """
    #_stop = threading.Event()
    #recvSignal = QtCore.pyqtSignal()
    
    def __init__(self, parent=None, component=None, gate=None):
        map = scl.generate_map("drmclient")
        self.sock = map["control"]
        time.sleep(1)
        #QtCore.QObject.__init__(self)
        #_stop = threading.Event()
        
    def getChannelList(self):
        # note, we need to put this into an own thread
        request = drm_pb2.control()
        request.type = drm_pb2.REQUEST
        request.command = drm_pb2.GET_CHANNEL_LIST
        string = request.SerializeToString()
        self.sock.send(string)
        print "Waiting for reply .."
        string = self.sock.recv()
        reply = drm_pb2.control()
        reply.ParseFromString(string)
        #print reply.channelMap[0]
        return reply.channelMap
