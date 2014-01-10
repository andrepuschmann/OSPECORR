import numpy as np
import time
import random
import threading
from radioconfig import RadioConfig

class ActivityController(threading.Thread):
    _stop = threading.Event()
    _pause = threading.Event()
    radioconfig = RadioConfig()
    
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
         _pause = threading.Event()

    def pause(self):
        print "pause thread"
        self._pause.set()
    
    def resume(self):
        print "resume thread"
        self._pause.clear()
    
    def paused(self):
        return self._pause.isSet()

    def stop(self):
        print "stop called"
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
        
    def update_probabilites(self, probs):
        # check if they add up to 1.0
        propsum = 0
        for i in probs:
            propsum+=i
        if propsum != 1.0:
            print "Cumulative probability is not 1.0, aborting."
            return -1
        self.props = probs
        print "Channel probabilities have been updated to" 
        print self.props
        return 0

    # From PythonCookBook, to draw from list with fix probability
    def random_pick(self, some_list, probabilities):
        x = random.uniform(0, 1)
        cumulative_probability = 0.0
        for item, item_probability in zip(some_list, probabilities):
            cumulative_probability += item_probability
            if x < cumulative_probability: break
        return item

    def run(self):

        # start in pause mode
        self.pause()
        
        if self.update_probabilites(self.props) == -1:
            return

        # start work
        print "Start : %s" % time.ctime()
        while not self.stopped():
            # pause loop
            while not self.paused():
                # get freq of next channel
                freq = self.random_pick(self.channels, self.props)
                print "Tune to frequency %s" % freq
                self.radioconfig.tuneRadio(freq)
                
                # draw sample to see for how long we have to turn on transmitter
                duty = np.random.poisson(self.dutycycle)
                print "Duty %ss" % duty
                time.sleep(duty)
                
                # wait until transmitter tunes to next channel
                wait = np.random.poisson(self.interarrivaltime)
                print "Wait %ss" % wait
                # FIXME: should pause radio here
                time.sleep(wait)
            print "thread paused .."
            time.sleep(1)
        print "End : %s" % time.ctime()
