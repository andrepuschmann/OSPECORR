from PyQt4 import QtCore
import numpy as np
import time
import random
import threading
import scl
import radioconfig_pb2

class ActivityController(threading.Thread):
    _stop = threading.Event()
    recvSignal = QtCore.pyqtSignal()    
    
    def __init__(self, channels, propabilities, dutycycle, interarrivaltime, engineName=None, componentName=None):
         threading.Thread.__init__(self)
         self.channels = channels
         self.props = propabilities
         self.dutycycle = dutycycle
         self.interarrivaltime = interarrivaltime
         if engineName is None:
            self.engineName = "phyengine1"
         else:
            self.engineName = engineName
            
         if componentName is None:
            self.componentName = "usrptx1"
         else:
            self.componentName = componentName
         print "Enginename %s" % self.engineName
         
         _stop = threading.Event()

    def stop(self):
        print "stop called"
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    # From PythonCookBook, to draw from list with fix probability
    def random_pick(self, some_list, probabilities):
        x = random.uniform(0, 1)
        cumulative_probability = 0.0
        for item, item_probability in zip(some_list, probabilities):
            cumulative_probability += item_probability
            if x < cumulative_probability: break
        return item


    def tuneRadio(self, freq):
        print "Tune Radio"
        map = scl.generate_map("pySysMoCo")
        radioconfigcontrol = map["radioconfcontrol"]

        #Create request for radio reconfiguration
        request = radioconfig_pb2.RadioConfigControl()
        request.type = radioconfig_pb2.REQUEST
        request.command = radioconfig_pb2.SET_RADIO_CONFIG

        # add engine and component to message
        engine = request.radioconf.engines.add()
        engine.name = str(self.engineName)
        component = engine.components.add()
        component.name = str(self.componentName)
        
        # add paramters
        txfreq = component.parameters.add()
        txfreq.name = "frequency"
        txfreq.value = str(freq)
        
        #send request
        string = request.SerializeToString()
        radioconfigcontrol.send(string)
        #wait for reply, fixme: check result
        string = radioconfigcontrol.recv()
        print "Got reply from radio"


    def run(self):
        # check if they add up to 1.0
        propsum = 0
        for i in self.props:
            propsum+=i
        if propsum != 1.0:
            print "Cumulative probability is not one."
            return

        # start work
        print "Start : %s" % time.ctime()
        while not self.stopped():
            # get freq of next channel
            freq = self.random_pick(self.channels, self.props)
            self.tuneRadio(freq)
            
            # draw sample to see for how long we have to turn on transmitter
            duty = np.random.poisson(self.dutycycle)
            print "Duty %ss" % duty
            time.sleep(duty)
            
            # wait until transmitter tunes to next channel
            wait = np.random.poisson(self.interarrivaltime)
            print "Wait %ss" % wait
            # FIXME: should pause radio here
            time.sleep(wait)

        print "End : %s" % time.ctime()
            

            


