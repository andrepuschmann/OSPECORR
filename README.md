# OSPECOR²

This is OSPECOR². OSPECOR² stands for Open Software Platform for Experimental Cognitive Radio Research.

### Overview

This repository contains the public bits of the platform. Some of the core components such as the SDR framework (i.e. Iris) are not yet included for license reasons but will be added in the future.

The repository consists of the core of OSPECORR and one subrepository called common which houses commonly used components such as the Signaling and Communication Link (SCL) which is used by multiple projects within the Graduate School on Mobile Communication (MOBICOM) at Ilmenau University of Technology, Ilmenau, Germany.

The general folder structure is shown below:

* __MOBICOM__ (MOBICOM_PATH defines top-level path)
    * __common__ MOBICOM common, aka __"level 1 common"__
        * __scl__: signaling and communication link
        * __svctrl__: service control utility
        * __scripts__: bashrc (sourced from user bashrc)
    * __OSPECORR__ (MOBICOM_PROJECT_NAME = __OSPECORR__):
        * __common__ __OSPECORR__ common, aka __"level 2 common"__
            * __config__: common configuration files for all subprojects
            * __scripts__: bashrc (sourced from upper-level bashrc)
        * __components__: programs connected through __common__ above

The key motivation behind this structure is to support code-reuse while keeping conceptually different parts of the software system in different repositories (plug-in concept).
Thus, our system has the following benefits:

* a standard structure, comparable with the Linux filesystem having fixed file locations at 3 hierarchy levels (1-3) in the filesystem. Repeating directories are for example: config, messages, scripts.
* code reuse between distinct projects like ARCADE and OSPECOR (__"level 1"__ common) keeps systems maintainable through submodules
* support for automatic export of environment variables through multiple bashrc files
* defining different software architectures (__"level 2"__ common) for multiple deployment targets (UAV, PC, ...)
* sharing code and message formats between multiple processes (components) on a single machine (__"level 3"__ common)


### Getting started:

1. Install some basic packet dependencies onto your system. E.g. using Ubuntu, invoke the following:

   ```bash
$ sudo apt-get install build-essential libboost-all-dev git libfftw3-dev autoconf cmake libprotobuf-dev python-protobuf python-yaml protobuf-compiler protobuf-c-compiler python-qt4 python-qt4-dev pyqt4-dev-tools python-matplotlib python-setuptools python-qwt5-qt4 libzmq-dev libpgm-dev python-zmq libqwt-dev
```   

2. Clone the repo to your machine, make sure to call it MOBICOM (the actual project name will be a directory inside the repo)

    ```bash
$ git clone git://github.com/andrepuschmann/OSPECORR.git MOBICOM
```
3. Change into the new directory and initialize the submodules (i.e. the common part of MOBICOM)
   
    ```bash
$ cd ./MOBICOM
$ ./gitsub_update.sh
```
    
4. Copy the content of ```example.bashrc``` into your local bashrc and edit it if required, reinstalize your environment

    ```bash
$ cat example.bashrc >> ~/.bashrc
$ nano ~/.bashrc
$ bash
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
   
   Note: When running on ARM-based systems such as the E100, you might use the following cmake command instead:

    ```bash
$ cmake -DCMAKE_TOOLCHAIN_FILE=../common/scripts/cmake/Toolchains/arm_cortex_a8_native.cmake ..
```    

6. You're done! OSPECORR should be built and installed. Let's try it out by starting an example component which publishes
RSSI measurements over SCL.

    6.1. Start the example PHY publisher (which is a Python app and therefore requires a Python interpreter)
    ```bash
$ python OSPECORR/components/examplePhyPublisher/examplePhyPublisher.py
```

    6.2. Start the example PHY subscriber in another console (which is a standard C++ application and be started without parameter)
    ```bash
$ OSPECORR/components/examplePhySubscriber/examplePhySubscriber
```
    You should now be able to see the incoming measurements from the publishing application
    
    
    6.3. Let's also start pySysMoCo on a third console. pySysMoCo should also be able to visualize the measurements
    coming from the first application. Please note that we have to start pySysMoCo from the source directory as it has
    some file dependencies such as the UI file. You should be able to see regular RSSI updates in the PHY tab of pySysMoCo.
    ```bash
$ cd ../OSPECORR/components/pySysMoCo
$ python pySysMoCo.py
```