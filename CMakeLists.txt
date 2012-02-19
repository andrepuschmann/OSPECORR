########################################################################
# Prevent in-tree builds
########################################################################
IF(${CMAKE_SOURCE_DIR} STREQUAL ${CMAKE_BINARY_DIR})
    MESSAGE(FATAL_ERROR "Prevented in-tree built. This is bad practice.")
ENDIF(${CMAKE_SOURCE_DIR} STREQUAL ${CMAKE_BINARY_DIR})


########################################################################
# Project setup
#######################################################################
CMAKE_MINIMUM_REQUIRED (VERSION 2.6)
PROJECT (MOBICOM)


SET(MOBICOM_PATH $ENV{MOBICOM_PATH})
IF (NOT MOBICOM_PATH)
    MESSAGE(FATAL_ERROR "MOBICOM_PATH directory not specified!")
    MESSAGE(FATAL_ERROR "Use 'export MOBICOM_PATH=/path/to/' to specify one.")
ENDIF (NOT MOBICOM_PATH)

LIST(APPEND CMAKE_MODULE_PATH ${MOBICOM_PATH}/common/scripts/cmake)
find_package(Protobuf REQUIRED)
find_package(YAML-CPP REQUIRED)
find_package(ZeroMQ REQUIRED)


SET(MOBICOM_PROJECT_NAME $ENV{MOBICOM_PROJECT_NAME})
IF (NOT MOBICOM_PROJECT_NAME)
    MESSAGE(FATAL_ERROR "MOBICOM_PROJECT_NAME directory not specified!")
    MESSAGE(FATAL_ERROR "Use 'export MOBICOM_PROJECT_NAME=/path/to/' to specify one.")
ENDIF (NOT MOBICOM_PROJECT_NAME)
SET(PROJECT_NAME $ENV{PROJECT_NAME})

INCLUDE_DIRECTORIES($ENV{MOBICOM_PROJECT_BUILD_PATH}/common/message-defs)

INCLUDE_DIRECTORIES(common/scl/src)

ADD_SUBDIRECTORY (common)
ADD_SUBDIRECTORY (${MOBICOM_PROJECT_NAME})
