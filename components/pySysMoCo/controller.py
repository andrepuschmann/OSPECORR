import socket
import sys
import xml.etree.ElementTree as Config
import time

import array
import random
import json
import numpy as np
from deap import algorithms
from deap import base
from deap import benchmarks
from deap import creator
from deap import tools
from radioconfig import RadioConfig
import radioconfig_pb2
from PyQt4 import Qwt5 as Qwt
from PyQt4 import Qt
import csv
import threading
import signal
import os

#list to store the parameter name, no. of values and the values
class config_list():
    "Stores name and value pairs"
    def __init__(self, name, nov, values):
        self.name = name
        self.nov = nov        
        self.values = values
        

class RadioOptimizer(threading.Thread):

    radioConfig = radioconfig_pb2.RadioConfig()
    
    #The IP address of the client that needs to be configued
    CLIENT_LOCAL_IP = '192.168.1.105'
    
    #Frame type defines
    flex_frame_try = 'FLEX_FRAME_TRY '
    flex_frame_final = 'FLEX_FRAME_FINAL '
    flex_frame_end = 'FLEX_FRAME_END '
    flex_frame_start_traffic = 'FLEX_FRAME_START_TRAFFIC '
    flex_frame_results = 'FLEX_FRAME_RESULTS '
    flex_frame_cli_config = 'FLEX_FRAME_CLI_CONFIG '
    
    def __init__(self, radioConfig):
        super(RadioOptimizer, self).__init__()
        #print 'Optimizer INIT'
        self._stop = threading.Event()
        self.init_time=time.time()
        
        #self.opt_plot = Optimizer_Plot()
        self.radioConfig = radioConfig
                
        #print radioConfig
        if not radioConfig:
            print 'Nothing in radio config. Return'
            return
        
        #GA parameters
        self.NGEN = 30
        self.NIND = 30
        self.CXPB = 0.9
        self.MUTPB = 0.05
        
        #Stores the current generation
        self.igen = 0
        #Stores the best individual
        self.best_ind = []
        
        #Plot init
        self.opt_plot = self.Optimizer_Plot()
        self.x_vals = []
        self.y_vals = []
        self.best_x = [0]
        self.best_y = [0]
    
        #list to store the parameters to their corresponding respective values    
        self.param_list = []
        self.conf_list = []
        
        #Open Local and Radio sockets
        self.local_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Variables to indicate the connected and run states
        self.connected = False
        self.start_opt = False
        
        # Parse the xml file using ElementTree
        #file_name = sys.argv[1]
        file_name = 'iris_default_configuration.xml'
        tree = Config.parse(file_name)
        self.root = tree.getroot()
        #Initialize the default list
        self.default_list = []
        self.fill_default_list()

        #Create the Fitness function. The weights of the objective functions need to be given here.
        #The positive value represents the function to be maximised and the negative is for minimising
        weight_0 = 200.0
        weight_1 = -1.0
        creator.create("FitnessMulti", base.Fitness, weights=(weight_0, weight_1))
        #Give the objective index which has a higher priority.
        if abs(weight_0) > abs(weight_1):
            self.obj_indx = 0
        else:
            self.obj_indx = 1
        
        creator.create("Individual", array.array, typecode='d', fitness=creator.FitnessMulti)
        
    def stop(self):
        self._stop.set()
        
    def run(self):
        self.init_time=time.time()
        #Always loop the controller functionality
        while True:
            if self._stop.isSet():
                print 'Return from Radio Optimizer'
                return
            if self.start_opt:
                if not self.connected:
                    # Connect to the controller
                    cli_local_address = (self.client_control_ip, 10000)
                    print >>sys.stderr, 'Connecting to client on local ip %s port %s' % cli_local_address
                    self.local_sock.connect(cli_local_address)
                    self.connected = True

                    try:
                        self.send_client_config() 
                        #Start the optimization
                        self.run_optimizer()
                        self.start_opt = False
                    finally:
                        #print >>sys.stderr, 'Closing local socket'
                        #self.local_sock.close()
                        end_time=time.time()
                        print 'RunTime: ', str(end_time - self.init_time)
                else:
                    self.run_optimizer()        
        return
        
    def run_optimizer(self):
        print 'Start Optimizer'
        #File point of csv to store the results
        with open('test.csv', 'wb') as fp:
            with open('best.csv', 'wb') as fp1:   
              self.csv_fp = csv.writer(fp)
              self.best_fp = csv.writer(fp1)
              #Starts the GA
              self.start_ga()

              #Transmit the end
              frame = self.flex_frame_end
              print >>sys.stderr, 'sending %s' % frame
              self.local_sock.sendall(frame)
              return
        
    #Modules to start and stop the algorithm    
    def start_optimizer(self):
        print 'Start Optimizer'
        self.start_opt = True
        
    def stop_optimizer(self):
        print 'Stop Optimizer'
        self.start_opt = False
        
    #Method to add the plot of GUI from window.py
    def add_plot(self):
        #self.opt_plot = opt_plot
        return self.opt_plot

    def updateConfiguration(self, client_control_ip, client_data_ip, server_control_ip, server_data_ip):
        print "updateConfiguration()"
        self.client_control_ip = client_control_ip
        self.client_data_ip = client_data_ip
        self.server_control_ip = server_control_ip
        self.server_data_ip = server_data_ip

    def send_client_config(self):
        frame = self.flex_frame_cli_config + 'client_control_ip:' + str(self.client_control_ip) + ' client_data_ip:' + str(self.client_data_ip) + ' server_control_ip:' + str(self.server_control_ip) + ' server_data_ip:' + str(self.server_data_ip)
        print 'sending %s' % frame
        self.local_sock.sendall(frame)

        data = self.local_sock.recv(3)
        if data == 'ACK':
            print >>sys.stderr, 'received "%s"' % data

    #Method to update the radio config from window.py    
    def update_config(self, radioConfig):
        #self.opt_plot = opt_plot
        self.radioConfig = radioConfig
                        
    #Fill the default config, which the user can select from the gui later
    #Config is picked from an example xml provided
    def fill_default_list(self):
        idx = 0
        for subelement in self.root:
            for sub in subelement:
                for sub2 in sub:
                    if sub2.attrib.get('value') != None:
                        value = sub2.attrib.get('value')
                        values = value.split()
                        #Only take those values which are more than 1, to try in the optimization
                        if len(values) > 1 or value.startswith("range("):
                            engine =  subelement.attrib.get('name')
                            component = sub.attrib.get('name')
                            parameter = sub2.attrib.get('name')
                            self.default_list.append(self.def_list(engine, component, parameter, value))                            
                            #Increment the indx
                            idx += 1
                            
        #for x in self.default_list:
        #    print 'def: ', x.engine, x.component, x.parameter, x.values
        
        return


    #Module to return the engine name, when the component and parameter are given as inputs
    def get_engine_name(self, component, parameter):
        # Parse through the radio config
        for i in self.radioConfig.engines:
            for k in i.components:
                for j in k.parameters:
                    if(k.name == component and j.name == parameter):
                            return i.name

        return None


    #Computes the quality of the configuration, by receiving the traffic from the client
    #Also decides if the configuration of the rx too needs to be change, and does so accordingly
    def send_config( self, engine, component, parameter, value ):
          print engine, component, parameter, value
     
          #Transmit the Config to the Client
          frame = self.flex_frame_try + 'engine:' + engine + ' component:' + component + ' parameter:' + parameter + ' value:' + str(value)
          #print 'sending Frame %s' % frame
          #local_sock.sendall(frame)

          #Some parameters need to be configured on both the transmitter and receiver. So handle such cases. Generally are of modulation related
          if (parameter == 'subcarriers' or parameter == 'prefixlength' or  parameter == 'frequency' or parameter == 'rate'):
              #Certain parameters, if configued on the tx, needs to be configured on the rx of other side, and vice versa. Generally are of usrptx and usrprx parameters
              #For such cases, we need to fetch the corresponding engine name too, as it can be different for the tx and rx scripts
              if (component == 'usrptx1' and parameter == 'rate') :
                  component = 'usrprx1'
                  engine = self.get_engine_name(component, parameter)

              elif (component == 'usrprx1' and parameter == 'rate'):
                  component = 'usrptx1'
                  engine = self.get_engine_name(component, parameter)

              if not engine:
                  print >>sys.stderr, 'Could not find anything with the given engine name'
                  return

              print 'sending %s' % frame
              self.local_sock.sendall(frame)

              print 'Configuring the Rx side too, for engine :', engine, ', component:', component , ' parameter:', parameter,'value:', value
              config = RadioConfig(engine, component, parameter)
              config.tuneRadio(value)

          else:
              print 'sending %s' % frame
              self.local_sock.sendall(frame)

          #Receive ACK
          data = self.local_sock.recv(3)
          if data == 'ACK':
              print >>sys.stderr, 'received "%s"' % data
          
          return


    #Function to compute the throughput
    def compute_throughput(self):
        #Start the timer
        start_time=time.time()
        duration = 2
        thru = 0
        fer = 0

        loop = True
        while loop:
            data = self.local_sock.recv(256)
            
            if data:     
                print >>sys.stderr, 'received "%s"' % data
                frame = data.split(' ')
                print frame
                if frame[0] == 'FLEX_FRAME_RESULTS':
                    thru = float(frame[1])
                    fer = float(frame[2])
                    evm = float(frame[3])
                    print 'Throughput, FER & EVM: ', thru, fer, evm, '\n'
                    loop = False
                    break

        return thru, fer, evm
    
    def configure_individual(self, individual):
        print individual
        #print 'Conf-list: ', self.conf_list
        
        for i in range(0, len(individual)):
            #extract the individual's values of each index 
            val = int(individual[i])

            #extract the name of the parameters, corresponding to the index.
            var = self.conf_list[i].name.split(':')
            #print i, val, self.conf_list[i].values
            #pick the value of the variable from the conf list.
            val = self.conf_list[i].values[val]

            #Send the config to the client and compute the individual
            self.send_config(var[0], var[1], var[2], val)
        return


    def get_individual(self, individual):
        
        ind_list = []
        for i in range(0, len(individual)):
            #extract the individual's values of each index 
            val = int(individual[i])
            #extract the name of the parameters, corresponding to the index.
            var = self.conf_list[i].name.split(':')
            #pick the value of the variable from the conf list.
            val = self.conf_list[i].values[val]
            
            name = var[0] + ':' + var[1] + ':' + var[2] + ':' + str(val)
            ind_list.insert(len(self.param_list), name)
        return ind_list

    #Evalues the fitness required for the GA
    def evalFitness(self, individual):
        throughput = 0
        fer = 0

        self.configure_individual(individual)
        #Transmit the start traffic frame to the Client
        frame = self.flex_frame_start_traffic
        print 'sending start traffic frame %s' % frame
        self.local_sock.sendall(frame)

        #Receive ACK
        data = self.local_sock.recv(3)
        if data == 'ACK':
            print >>sys.stderr, 'received "%s"' % data

        #Compute the throughput
        throughput, fer, evm = self.compute_throughput()
        
        #Add the value into the plot
        data = [[self.igen, time.time() - self.init_time, throughput, fer,  evm, self.get_individual(individual)]]
        self.csv_fp.writerows(data)
        self.x_vals.insert(len(self.x_vals), time.time() - self.init_time)
        self.y_vals.insert(len(self.y_vals), throughput) 
        #self.y_vals.insert(len(self.y_vals), evm) 
        
        #time.sleep(1)
        #Return the two values that need to be considered for Fitness.
        #The first value is to be maximised and the second is to be minimised
        return throughput, evm


    #Prepares the conf_list and the  range config. 
    #Generally, it is called from the window.py module, to update the parameters from gui
    def prepare_config(self, engine, component, param, val):
        print 'In prepare config: ', engine, component, param, val
        if val.startswith("range("):
            print 'range: ', val
            val = val.replace('range(', '')
            val = val.replace(')', '')
            values = val.split(',')
            print 'vals', values, len(values)
            print 'Values in range', values[0], values[1], values[2]
            try:
              float(values[0])
              values = np.arange(float(values[0]),float(values[1]),float(values[2]))
            except ValueError:
              print 'Didnt float :D'
            print 'Final Values: ', values
        else:
            val = val.replace(', ', ' ')
            values = val.split()
            print 'Final Values: ', values
        
        #Form the parameter in the order of engine:component:param
        par = engine + ':' + component + ':' + param
        
        #Replace the new values of the parameter if it already exists in the list
        #No need to register a toolbox coz its already registered
        add = True
        for conf in self.conf_list:
            if conf.name == par:
                conf.nov = len(values)
                conf.values = values
                add = False
        
        if add:
            #A new parameter is to be added to the conf_list
            self.conf_list.append(config_list(par, len(values), values))
        
        for conf in self.conf_list:
            print 'Config List: ', len(self.conf_list), conf.name, conf.nov, conf.values

        return

    #Extracts the config and starts the GA
    def start_ga(self):

        toolbox = base.Toolbox()
        #Need this func seq to store the name of the parameters as attributes for input to toolbox
        func_seq = []

        #init the variables
        CXPB = self.CXPB
        MUTPB = self.MUTPB
        NGEN = self.NGEN
        MU = self.NIND

        idx = 0
        for conf in self.conf_list:
            #Register the parameter in the toolbox. We need this to make the individuals
            toolbox.register( conf.name, random.randint, 0, len(conf.values)-1) 
            #func makes a reference to the function toolbox.par
            func = getattr(toolbox, conf.name)
            #func_seq is the list of all the parameters of an individual, which are of attribute form
            func_seq.insert(idx, func)
            idx += 1
        print 'Func seq: ', func_seq

        #Register all the necessarz parameters for the GA
        toolbox.register("individual", tools.initCycle, creator.Individual, func_seq, n=1)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual, MU)
        toolbox.register("evaluate", self.evalFitness)
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", tools.mutFlipBit, indpb=MUTPB)
        toolbox.register("select", tools.selNSGA2)

        #form the population of individuals
        pop = toolbox.population()
        print 'Population: %s' % pop
        print 'Starting the GA \n'

        #Logbook
        logbook = tools.Logbook()
        stats = tools.Statistics(lambda ind: ind.fitness.values)

        #Plot the best
        self.best_x.insert(len(self.best_x), time.time() - self.init_time)
        self.best_y.insert(len(self.best_y), 0.0)
        
        #Compute the fitness of the initial generation
        fits = toolbox.map(toolbox.evaluate, pop)
        for fit, ind in zip(fits, pop):
            ind.fitness.values = fit
            print ind, fit 

        #Initialize the individual fitness to pick the best each time, and plot
        best_ind = tools.selBest(pop, 1)[0]
        self.best_x.insert(len(self.best_x), time.time() - self.init_time)
        self.best_y.insert(len(self.best_y), best_ind.fitness.values[0])
        
        # Begin the evolution
        for g in range(NGEN):
            self.igen = g
            #If a stop has been issued
            if self._stop.isSet():
                return
            #This is when the optimizer's stop button is pressed
            if not self.start_opt:
                print 'Need to Stop'
                #Configure the best individual yet
                self.configure_individual(best_ind)
                self.unregister_toolbox(toolbox)
                return
                
            print "-- Generation %i --" % g

            # Select the next generation individuals
            offsprings = toolbox.select(pop, len(pop))
            #offsprings = tools.selTournamentDCD(pop, len(pop))
            
            # Clone the selected individuals
            offsprings = map(toolbox.clone, offsprings)

            # Apply crossover and mutation on the offsprings
            for child1, child2 in zip(offsprings[::2], offsprings[1::2]):
                if random.random() < CXPB:
                    toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offsprings:
                if random.random() < MUTPB:
                    toolbox.mutate(mutant)
                    del mutant.fitness.values

            # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offsprings if not ind.fitness.valid]
            fitnesses = map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            print "  Evaluated %i individuals" % len(invalid_ind)
            print '\n'
            
            # The population is entirely replaced by the offsprings
            #pop[:] = offsprings
            
            # Select the next generation population
            pop = toolbox.select(pop + offsprings, MU)
            record = stats.compile(pop)
            logbook.record(gen=g, evals=len(invalid_ind), **record)
            print(logbook.stream)
        
            fits = [ind.fitness.values[0] for ind in pop]
            
            print 'A GEN finished'
            #Signal the parent to plot
            os.kill(os.getpid(), signal.SIGALRM)
            
            #Pick the best individual
            try_ind = tools.selBest(pop, 1)[0]
            print 'New best: ', try_ind.fitness.values[0], 'All time best: ', best_ind.fitness.values[0]
            #pick it based on the objective function which has higher priority
            if try_ind.fitness.values[self.obj_indx] > best_ind.fitness.values[self.obj_indx]:
                print 'New best Selected'
                best_ind = try_ind
            self.note_best_values(best_ind)
            print 'Best individual Configuration: ', self.get_individual(best_ind)
            self.best_ind = self.get_individual(best_ind)
            
        print '-- End of (successful) evolution of Generation %i --'  % g
        #print("Final population hypervolume is %f" % hypervolume(pop, [11.0, 11.0]))
        #best_ind = tools.selBest(pop, 1)[0]
        self.note_best_values(best_ind)
        
        print 'The final Population:', pop
        
        print 'Best Ind: ' %best_ind
        self.configure_individual(best_ind)
        self.configure_individual(best_ind)
        print self.get_individual(best_ind)
        print best_ind.fitness.values

        #Unregister the classes of GA
        self.unregister_toolbox(toolbox)
        
        return

    def unregister_toolbox(self, toolbox):
        toolbox.unregister("individual")
        toolbox.unregister("population")
        toolbox.unregister("evaluate")
        toolbox.unregister("mate")
        toolbox.unregister("mutate")
        toolbox.unregister("select")
        
    def note_best_values(self, best_ind):
        self.best_x.insert(len(self.best_x), time.time() - self.init_time)
        self.best_y.insert(len(self.best_y), best_ind.fitness.values[0])
        data = [[self.igen, time.time() - self.init_time, best_ind.fitness.values[0], best_ind.fitness.values[1], self.get_individual(best_ind)]]
        self.best_fp.writerows(data)

    #Class to plot the graph of radio-optimizer results
    class Optimizer_Plot(Qwt.QwtPlot):

        def __init__(self, parent=None):
            #print 'Plot init: ', self
            Qwt.QwtPlot.__init__(self)
            self.setAxisTitle(Qwt.QwtPlot.xBottom, 'Time(seconds)');
            self.setAxisTitle(Qwt.QwtPlot.yLeft, "Fitness(in Mbps)")
            self.setCanvasBackground(Qt.Qt.black)
            self.Curve1 = Qwt.QwtPlotCurve("Fitness-Plot")
            self.Curve1.attach(self)
            self.Curve1.setPen(Qt.QPen(Qt.Qt.blue))
            self.Curve1.setYAxis(Qwt.QwtPlot.yLeft)
            
            self.Curve2 = Qwt.QwtPlotCurve("Best-Config")
            self.Curve2.attach(self)
            self.Curve2.setPen(Qt.QPen(Qt.Qt.red))
            self.Curve2.setYAxis(Qwt.QwtPlot.yLeft)
            
            self.setAxisScale( Qwt.QwtPlot.xBottom, 0.0, 500.0)
            self.setAxisScale( Qwt.QwtPlot.yLeft, 0.0, 10.0)
            
            
        def plotOptimizer(self, x_values, y_values, best_x, best_y):
            #print 'the plot - X: ', best_x, 'Y: ', best_y
            if x_values and y_values:
                self.setAxisScale( Qwt.QwtPlot.xBottom, 0.0, max(x_values) + 10)
                self.setAxisScale( Qwt.QwtPlot.yLeft, 0.0, max(y_values) + 2)
                self.Curve1.setData(x_values, y_values)
                self.Curve2.setData(best_x, best_y)
                self.replot()


    #Stores name and value pairs
    class def_list():    
        def __init__(self, engine, component, parameter, values):
            self.engine = engine
            self.component = component
            self.parameter = parameter
            self.values = values
