########################################################################
# Prevent in-tree builds
########################################################################
IF(${CMAKE_SOURCE_DIR} STREQUAL ${CMAKE_BINARY_DIR})
    MESSAGE(FATAL_ERROR "Prevented in-tree built. This is bad practice.")
ENDIF(${CMAKE_SOURCE_DIR} STREQUAL ${CMAKE_BINARY_DIR})

########################################################################
# Project setup
########################################################################

CMAKE_MINIMUM_REQUIRED (VERSION 2.6)
PROJECT (IRIS)

ADD_SUBDIRECTORY (core)
ADD_SUBDIRECTORY (modules)
