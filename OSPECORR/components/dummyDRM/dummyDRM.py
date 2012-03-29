#!/usr/bin/env python
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
#   Copyright 2012 Andre Puschmann <andre.puschmann@tu-ilmenau.de>
#

import scl
import scldrm_pb2
import random
import time
from google.protobuf import message


map = scl.generate_map("DRM")
control = map["drmcontrol"]

print "Waiting for DRM request messages .."
while True:
    string = control.recv()
    request = scldrm_pb2.controlRequest()
    request.ParseFromString(string)
    print "received " + request.command
    #switch(request.command)
    
    reply = scldrm_pb2.controlReply()
    reply.command = request.command # same as request
    reply.freq = 3 # test
    string = reply.SerializeToString()
    control.send(string)
    time.sleep(0.1)
