# OSPECORR

OSPECORR is a free and __Open Software Platform for Experimental Cognitive Radio Research__ which is being developed by members
of the Graduate School on Mobile Communication (MOBICOM) at Ilmenau University of Technology, Germany.
The main idea behind OSPECORR is to provide an easy to use platform that facilitates research and experimentation in the
field of Cognitive Radio (CR).

Cognitive Radios are often built on top of a so called __Software Defined Radio (SDR)__ that enables the flexible reconfiguration
and adaption of the radio during runtime. Moreover, a typical CR design comprises other components including a 
__Cognitive Resource Manager (CRM)__
or an __Radio Environment Database (REM)__ that allows to store certain information gathered for instance through spectrum sensing. Naturally, the components of the radio are required to exchange information among each other and this is where OSPECORR comes into play.

Rather than implementing the entire radio inside a single application, OSPECORR allows to split the functionality among
different components that communicate with each other over a middleware called SCL. SCL allows to describe the structure of the messages using Google's Protocol Buffers, all definitions can be find in the __message-defs__ path. Those messages are then sent through ZeroMQ sockets. All components and their links are defined inside a YAML configuration file stored in __config__ path.


### Project structure:

The general project structure is shown below:

* __components__
    * __examplePhySubscriber__: An example SCL subscriber application written in C++
    * __examplePhyPublisher__: An example SCL publisher application written in Python
    * __exampleRadioReconfigurator__: An example application demonstrating how to reconfigure a running Iris instance
    * __gnuradio__: GNU-Radio scripts
    * __iris__: A reconfigurable component-based software radio framework
    * __pySysMoCo__: A Python+QT GUI application for system monitoring and control
* __config__: Contains the SCL system configuration
* __message-defs__: Message definitions used for SCL messages
* __scripts__: Mainly includes cmake scripts for building OSPECORR
* __scl__: The Signaling and Communication Link as an git submodule


### Getting started:

1. Install some basic packet dependencies onto your system. E.g. using Ubuntu, invoke the following:

   ```bash
$ sudo apt-get install build-essential libboost-all-dev git libfftw3-dev autoconf cmake libprotobuf-dev python-protobuf python-qt4-gl python-yaml protobuf-compiler protobuf-c-compiler python-qt4 python-qt4-dev pyqt4-dev-tools python-matplotlib python-setuptools python-qwt5-qt4 libzmq-dev libpgm-dev python-zmq libqwt-dev liblog4cxx10-dev
```   

2. Clone the repo to your machine:

    ```bash
$ git clone https://github.com/andrepuschmann/OSPECORR.git OSPECORR
```
3. Change into the new directory and setup the build environment

    ```bash
$ cd ./OSPECORR
$ export OSPECORR_PATH=$PWD
$ export SCL_CACHE_GENERATOR=$OSPECORR_PATH/scl/tools/gen_cache.sh
$ export SCL_CONFIG=$OSPECORR_PATH/config/system.yaml
$ export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib
```

4. To store the configuration permanently, put them into your .bashrc or .zshrc or .profile (and reinstalize your environment)

    ```bash
$ echo "export OSPECORR_PATH=$PWD" >> $HOME/.bashrc
$ echo 'export SCL_CACHE_GENERATOR=$OSPECORR_PATH/scl/tools/gen_cache.sh' >> $HOME/.bashrc
$ echo 'export SCL_CONFIG=$OSPECORR_PATH/config/system.yaml' >> $HOME/.bashrc
$ echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib' >> $HOME/.bashrc
$ bash
```


4. Initialize all sub repositories

    ```bash
$ ./gitsub_update.sh
```

5. Now, create a new build directory and build the source

    ```bash
$ mkdir build
$ cd build
$ cmake ..
$ make
$ make install
```
   Note: Calling make install without sudo assumes you have right permissions to the install location (i.e /usr/local/). 
   If that's not the case, either call it with sudo, choose a different install path or set the permissions accordingly,
   i.e. call ```$ sudo chown -R $USER /usr/local/```
   
   Note: Building OSPECORR for debugging goes like this ..

    ```bash
$ cmake -DCMAKE_BUILD_TYPE=Debug ..
```

7. You're done! OSPECORR should be built and installed. Let's try it out by starting an example component which publishes (randomly generated)
RSSI measurements over SCL.

    7.1. Start the example PHY publisher (which is a Python app and therefore requires a Python interpreter)
    ```bash
$ python /usr/local/bin/OSPECORR/examplePhyPublisher.py
```

    7.2. Start the example PHY subscriber in another console (which is a standard C++ application and can be started without parameter)
    ```bash
$ /usr/local/bin/OSPECORR/examplePhySubscriber
```
    You should now be able to see the incoming measurements from the publishing application
    
    
    7.3. Let's also start pySysMoCo on a third console. pySysMoCo should also be able to visualize the measurements
    coming from the first application. Please note that we have to start pySysMoCo from the source directory as it has
    some file dependencies such as the UI file. You should be able to see regular RSSI updates in the PHY tab of pySysMoCo.
    ```bash
$ python /usr/local/bin/OSPECORR/pySysMoCo.py
```

8. As another example, let's run a simple Iris radio and let an external application reconfigure the running radio. Let's say, we would like to increase the transmit power, i.e. transmitter gain, periodically. 

    8.1. Start the AlohaMac Iris radio that periodically transmits packets. Note that any radio that wants to be reconfigurable from within an external application needs to include the __RadioConfig controller__ in its XML radio specification.


      ```bash
$ cd ../examples/alohamac
$ iris -t /usr/local/lib/iris_modules/components/gpp/stack/ -p /usr/local/lib/iris_modules/components/gpp/phy/ -c /usr/local/lib/iris_modules/controllers/ alohamac_liquidofdm_tx.xml
```

    8.2. After making sure that radio is running, call the exampleRadioReconfigurator

      ```bash
$ /usr/local/bin/OSPECORR/exampleRadioReconfigurator
```


    8.3. Looking at a spectrum analyzer should give something similar to this. One can see that the transmit power is increased peridically exhibiting a ramp characteristic.
    

    ![Waterfall plot of the exampleRadioReconfigurator](https://f.cloud.github.com/assets/525775/2027689/84ded0a6-88bc-11e3-9d01-94251baa86ad.jpg "GNU Radio screenshot")
