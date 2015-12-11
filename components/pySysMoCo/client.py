import socket
import sys
from radioconfig import RadioConfig
import time
import scl
import radioconfig_pb2
import threading
import subprocess as sub
from subprocess import (PIPE, Popen)
from accumulators import Accumulators


class ClientOptimizer (threading.Thread):
    _stop = threading.Event()
    def __init__(self):
        super(ClientOptimizer, self).__init__()
        print 'Optimizer client INIT'

        # set default configuration
        #self.updateConfiguration('192.168.1.105', '10.0.0.5', '192.168.1.104', '10.0.0.4')

        self.connected = False
        _stop = threading.Event()
        
        self.evm = Accumulators()

    def stop(self):
        print "stop called"
        self._stop.set()

    def updateConfiguration(self, client_control_ip, client_data_ip):
        print "updateConfiguration(2)"       
        self.client_control_ip = client_control_ip
        self.client_data_ip = client_data_ip

    def updateIps(self, client_control_ip, client_data_ip, server_control_ip, server_data_ip):
        print "updateIps()"       
        self.client_control_ip = client_control_ip
        self.client_data_ip = client_data_ip
        self.server_control_ip = server_control_ip
        self.server_data_ip = server_data_ip

    def accumulate(self, stats):
        self.evm.add(abs(stats.evm))

    def reset_accumulator(self):
        self.evm = Accumulators()
        
    #Send traffic to the Controller to let it compute the link quality
    def feed_traffic(self, conn):
        #Reset the accumulator to calculate fresh values
        self.reset_accumulator()
        
        results = self.conn_conf.run_local()

        #Replace the unnecessary new lines to make it easier to split
        results = results.replace('\n\n', ' ')
        results = results.replace('\n', ' ')
        results = results.split(' ')
        thru = 0.0
        fer = 0.0
        for x in results:
            if x.split('=')[0] == 'rate_Mbps':   
                thru += float(x.split('=')[1])
            if x.split('=')[0] == 'data_loss':   
                fer += float(x.split('=')[1])

        evm = self.evm.compute('mean')
        #Handle the case when no packets are received which returns evm as zero
        if (evm == 0):
            evm = -100
        print 'throughput, fer: ', thru, fer, evm
        frame = 'FLEX_FRAME_RESULTS ' + str(thru) + ' ' + str(fer) + ' ' + str(evm) + ' END' 
        conn.sendall(frame)
        #print 'DONE FOR ONCE'
        return
        
        
    def run(self):
        print 'Optimizer client Run'

        # Create a TCP/IP socket
        self.local_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the port
        local_address = (self.client_control_ip, 10000)
        print >>sys.stderr, 'starting client on local ip %s port %s' % local_address
        self.local_sock.bind(local_address)
        
        # Listen for incoming connections
        self.local_sock.listen(1)
        
        # Wait for a local connection
        print >>sys.stderr, 'waiting for a local connection from controller'
        connection_local, controller_local_address = self.local_sock.accept()

        try:
            # Wait for a radio connection
            print >>sys.stderr, 'connection from', controller_local_address
            self.connected = True
            while True:
                if self._stop.isSet():
                    print 'return from client optimizer'
                    return
                self.start_client(connection_local)

        finally:
            print 'In Finally'
        

    def start_client(self, connection_local):

        # Receive the data
        data = connection_local.recv(1024)
        #Retrieve the frame and configure
        if data:
            print >>sys.stderr, 'received "%s"' % data
            #Send Acknowledgement to the transmitter
            print >>sys.stderr, 'sending ACK'
            connection_local.sendall('ACK')
            frame = data.split(' ')
            print frame
            if frame[0] == 'FLEX_FRAME_TRY':
                #Load the new Configuration'
                if (frame[1].split(':'))[0] == 'engine':
                    engineName = (frame[1].split(':'))[1]
                if (frame[2].split(':'))[0] == 'component':
                    componentName = (frame[2].split(':'))[1]
                if (frame[3].split(':'))[0] == 'parameter':
                    parameterName = (frame[3].split(':'))[1]
                if (frame[4].split(':'))[0] == 'value':
                    value = (frame[4].split(':'))[1]
                print >>sys.stderr, 'Writing new config[', engineName, componentName, parameterName, value, ']'

                #Configure the device
                config = RadioConfig(engineName, componentName, parameterName)
                config.tuneRadio(value)
                #print 'New config written' 
                #Send traffic to the controller
                #feed_traffic(connection_radio)

            elif frame[0] == 'FLEX_FRAME_CLI_CONFIG':
                print 'in Flex cli config'
                #Load the new Configuration'
                if (frame[1].split(':'))[0] == 'client_control_ip':
                    clientControlIp = (frame[1].split(':'))[1]
                if (frame[2].split(':'))[0] == 'client_data_ip':
                    clientDataIp = (frame[2].split(':'))[1]
                if (frame[3].split(':'))[0] == 'server_control_ip':
                    serverControlIp = (frame[3].split(':'))[1]
                if (frame[4].split(':'))[0] == 'server_data_ip':
                    serverDataIp = (frame[4].split(':'))[1]
                print >>sys.stderr, 'Client config received', clientControlIp, clientDataIp, serverControlIp, serverDataIp
                self.updateIps(clientControlIp, clientDataIp, serverControlIp, serverDataIp)

                #For nuttcp
                self.conn_conf = self.Connection(self.client_control_ip, self.client_data_ip, self.server_control_ip, self.server_data_ip, duration=1, rate="5M", reportinterval=2)

            elif frame[0] == 'FLEX_FRAME_START_TRAFFIC':
                #Send the ACK
                #connection_local.sendall('ACK')
                #Start the traffic to the controller
                print 'Start the traffic'
                #feed_traffic(connection_radio)
                self.feed_traffic(connection_local)

            elif frame[0] == 'FLEX_FRAME_FINAL':
                #Load the final selected configuration'
                if (frame[1].split(':'))[0] == 'engine':
                    engineName = (frame[1].split(':'))[1]
                if (frame[2].split(':'))[0] == 'component':
                    componentName = (frame[2].split(':'))[1]
                if (frame[3].split(':'))[0] == 'parameter':
                    parameterName = (frame[3].split(':'))[1]
                if (frame[4].split(':'))[0] == 'value':
                    value = (frame[4].split(':'))[1]
                print >>sys.stderr, 'Writing final config[', engineName, componentName, parameterName, value, ']'

                #Configure the device
                config = RadioConfig(engineName, componentName, parameterName)
                config.tuneRadio(value)

            elif frame[0] == 'FLEX_FRAME_END':
                #Load the final selected configuration'
                print 'Config End'
                return

            else:
                print 'Frame not recognized'

    class Connection(object):
        def __init__(self, \
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
        
        def run_local(self):
            print "Sleeping for %ds .." % self.startoffset
            time.sleep(self.startoffset)
            print "Executing command: %s" % self.nuttcp_cmd
            self.cmd_stdout = Popen(self.nuttcp_cmd, stdout=PIPE,shell=True).stdout.read()
            #stdin, stdout, stderr = self.sshclient.exec_command(self.nuttcp_cmd)
            print 'out: ', self.cmd_stdout 
            return self.cmd_stdout
        
