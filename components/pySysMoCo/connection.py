# -*- coding: utf-8 -*-
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
#   Copyright 2011-2014 Andre Puschmann <andre.puschmann@tu-ilmenau.de>
#

import sys
import paramiko
import time
from os.path import expanduser
import subprocess as sub
from subprocess import (PIPE, Popen)
#import sys

class Connection(object):
    def __init__(self, id="defaultid", \
                 sshhost="unknown", \
                 source_control=None, \
                 source_data=None, \
                 destination_control=None, \
                 destination_data=None, \
                 dataport=5101,
                 controlport=5000, \
                 startoffset=0, \
                 duration=10, \
                 rate="1M", \
                 framelength=1450, \
                 reportinterval=0.5):
        self.id = id
        self.sshhost = sshhost
        self.source_control = source_control
        self.source_data = source_data
        self.destination_control = destination_control
        self.destination_data = destination_data
        self.port_control = controlport
        self.port_data = dataport
        self.startoffset = startoffset
        self.duration = duration
        self.protocol = "-u"        
        self.rate = rate
        self.formatted_rate = float(rate[:-1])
        self.framelength = float(framelength)
        self.reportinterval = float(reportinterval)
        
        # SSH client
        self.sshclient = None        
        
        # convert starttime into string
        start = time.localtime()
        self.starttime = "%4d%02d%02d_%02d_%02d_%02d" % (start[0], start[1], start[2], start[3], start[4], start[5])
        self.starttime = "%4d%02d%02d" % (start[0], start[1], start[2]) # only data
        
        # construct commandline
        # Example for nuttcp using default client/server mode
        # $ nuttcp-7.2.1 -T2 -u -Ri500M -l1450 -fparse -i 0.5 host
        '''
        self.nuttcp_cmd = "nuttcp -T%d %s -R%s -l%d -fparse -i %.2f %s" % (self.duration, 
                                                                                  self.protocol,
                                                                                  self.rate,
                                                                                  self.framelength,
                                                                                  self.reportinterval,
                                                                                  self.destination)
        '''
        
        # Example using nuttcp's third-party mode
        # $ nuttcp -T10 -u -Ri1.5M -l2450 -fparse -i 0.5 192.168.1.100/10.0.0.1 192.168.1.104/10.0.0.4
        self.nuttcp_cmd = "nuttcp %s -T%d -R%s -l%d -fparse -i %.2f -p %s -P %s/%s %s/%s %s/%s" % (self.protocol,
                                                                                  self.duration,
                                                                                  self.rate,
                                                                                  self.framelength,
                                                                                  self.reportinterval,
                                                                                  self.port_data,
                                                                                  self.port_control,
                                                                                  self.port_control,
                                                                                  self.source_control,
                                                                                  self.source_data,
                                                                                  self.destination_control,
                                                                                  self.destination_data)
                                                                                
        print self.nuttcp_cmd

    def run(self):
        if self.sshclient:
            print "Sleeping for %ds .." % self.startoffset
            time.sleep(self.startoffset)
            print "Executing command: %s" % self.nuttcp_cmd
            stdin, stdout, stderr = self.sshclient.exec_command(self.nuttcp_cmd)
            self.cmd_stderr = stderr.readlines()
            self.cmd_stdout = stdout.readlines()
            if (self.cmd_stderr):
                print "WARNING: Something may went wrong during execution:"
                self.print_stderr()
                return False
            print self.cmd_stdout 
            return True
        return False

    def run_local(self):
        print "Sleeping for %ds .." % self.startoffset
        time.sleep(self.startoffset)
        print "Executing command: %s" % self.nuttcp_cmd
        self.cmd_stdout = Popen(self.nuttcp_cmd, stdout=PIPE,shell=True).stdout.read()
        print 'out: ', self.cmd_stdout 
        return self.cmd_stdout
        
    def set_data(self, data):
        self.data = data
        
    def set_summary(self, data):
        self.sum_data = data        

        
    def write_results_to_file(self):
        filename = "%s_%04.0fK_%04.0f_%s.log" % (self.starttime, self.formatted_rate, self.framelength, self.id)
        print "Writing results to %s" % (filename)
        
        with file(filename, 'w') as outfile:
            outfile.write('# This is the result file for a single connection. It includes the command invoked to produce these numbers and some additional information on how to interpret them.\n')
            outfile.write('#nuttcp command=%s\n' % (self.nuttcp_cmd))
            # add stderr output as comments
            if (self.cmd_stderr):
                for line in self.cmd_stderr:
                    outfile.write('#%s' % (line))
            
            outfile.write('#startoffset=%d\n' % (self.startoffset))
            outfile.write('#rate=%s\n' % (self.rate))
            outfile.write('#framelen=%s\n' % (self.framelength))
            for line in self.cmd_stdout:
                if "Warning=" in line:
                    outfile.write('#%s' % (line))
                else:
                    outfile.write(line,)
                #np.savetxt(outfile, data_slice, fmt='%-.2f')        
        
        
    
    def print_stderr(self):
        if (self.cmd_stderr):       
            for line in self.cmd_stderr:
                print line,
     
    def print_raw_results(self):
        self.print_stderr()
        for line in self.cmd_stdout:
            print line,
        return self.cmd_stdout
