# Python macros
# ~~~~~~~~~~~~~
# Copyright (c) 2007, Simon Edwards <simon@simonzone.com>
# modifications by Tobias Simon, Ilmenau University of Technology
#
# Redistribution and use is allowed according to the terms of the BSD license.
# For details see the accompanying COPYING-CMAKE-SCRIPTS file.
#
# This file defines the following macros:
#
# PYTHON_INSTALL (SOURCE_FILE DESINATION_DIR)
#     Install the SOURCE_FILE, which is a Python .py file, into the
#     destination directory during install. The file will be byte compiled
#     and both the .py file and .pyc file will be installed.


MACRO(PYTHON_INSTALL SOURCE_FILE DESINATION_DIR)
  # prepare:
  FIND_FILE(_python_compile_py PythonCompile.py PATHS ${CMAKE_MODULE_PATH})
  GET_FILENAME_COMPONENT(_absfilename ${SOURCE_FILE} ABSOLUTE)
  GET_FILENAME_COMPONENT(_filename ${SOURCE_FILE} NAME)
  GET_FILENAME_COMPONENT(_filenamebase ${SOURCE_FILE} NAME_WE)
  SET(_bin_py ${CMAKE_CURRENT_BINARY_DIR}/${_filename})
  SET(_bin_pyc ${CMAKE_CURRENT_BINARY_DIR}/${_filenamebase}.pyc)

  # add command for copying and byte-compiling:
  ADD_CUSTOM_COMMAND(
      OUTPUT ${_bin_py} ${_bin_pyc}
      COMMAND ${CMAKE_COMMAND} -E copy ${_absfilename} ${_bin_py}
      COMMAND ${PYTHON_EXECUTABLE} ${_python_compile_py} ${_bin_py}
      DEPENDS ${_absfilename}
    )
  
  # create a unique target name, namespace-restricted by MOBICOM_PROJECT_PATH:
  set(_target_name ${CMAKE_CURRENT_SOURCE_DIR}/${SOURCE_FILE}c)
  string(REPLACE $ENV{MOBICOM_PROJECT_PATH}/ "" _target_name ${_target_name})
  string(REGEX REPLACE "/" "_" _target_name ${_target_name})
  # add target:
  ADD_CUSTOM_TARGET(${_target_name} ALL DEPENDS ${_bin_py} ${_bin_pyc})

ENDMACRO(PYTHON_INSTALL)
