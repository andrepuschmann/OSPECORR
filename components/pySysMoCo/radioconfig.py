import scl
import radioconfig_pb2

class RadioConfig():
    def __init__(self, engineName="phyengine1", componentName="usrptx1", parameterName="frequency"):
        self.engineName = engineName
        self.componentName = componentName
        self.parameterName = parameterName

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
        txfreq.name = str(self.parameterName)
        txfreq.value = str(freq)
        
        #send request
        string = request.SerializeToString()
        radioconfigcontrol.send(string)
        print "Reconfig request sent, waiting for reply .."
        #wait for reply, fixme: check result
        string = radioconfigcontrol.recv()
        print "Got reply from radio"
