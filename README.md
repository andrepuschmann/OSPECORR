# OSPECOR²

This is OSPECOR². OSPENCOR² stands for Open Software Platform for Exeperimental Cognitive Radio Research.

This repository contains the public bits of the platform.

### Getting started:

1. Clone the repo to your machine, make sure to call it MOBICOM (the actual project name will be a directory inside the repo)

    ```bash
$ git clone git@github.com:andrepuschmann/OSPECORR.git MOBICOM
```
2. Change into the new directory and initialize the submodules (i.e. the common part of MOBICOM)
   
    ```bash
$ cd ./MOBICOM
$ ./gitsub_init.sh
```
    
3. Copy the content of ```example.bashrc``` into your local bashrc and edit it if required, reinstalize your environment

    ```bash
$ cat example.bashrc >> ~/.bashrc
$ nano ~/.bashrc
$ bash
```

4. Now, create a new build directory and build the source

    ```bash
$ mkdir build
$ cd build
$ cmake ..
$ make
```

5. You're done! Try it out by starting pySysMoCo in one console and examplePublisher in another console.

    ```bash
$ cd ../OSPECORR/components/pySysMoCo
$ ./pySysMoCo.py
```