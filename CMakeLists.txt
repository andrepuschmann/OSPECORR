########################################################################
# Prevent in-tree builds
########################################################################
IF(${CMAKE_SOURCE_DIR} STREQUAL ${CMAKE_BINARY_DIR})
    MESSAGE(FATAL_ERROR "Prevented in-tree built. This is bad practice.")
ENDIF(${CMAKE_SOURCE_DIR} STREQUAL ${CMAKE_BINARY_DIR})

########################################################################
# Project setup
#######################################################################
CMAKE_MINIMUM_REQUIRED(VERSION 2.6)
PROJECT(OSPECORR)

LIST(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/scripts/cmake)
find_package(Protobuf REQUIRED)
find_package(YAML-CPP REQUIRED)
find_package(ZeroMQ REQUIRED)

########################################################################
# Set common library variable and add include directories
########################################################################
SET(OSPECORR_LIBS "scl_ospecorr_messages" "scl_shared" "zmq" "yaml-cpp" "protobuf" )
INCLUDE_DIRECTORIES(${PROJECT_BINARY_DIR}/message-defs)
INCLUDE_DIRECTORIES(${PROJECT_SOURCE_DIR}/scl/src)

########################################################################
# Install Dirs
########################################################################
SET(RUNTIME_DIR bin)
SET(LIBRARY_DIR lib)
SET(INCLUDE_DIR include)
SET(DATA_DIR share/${CPACK_PACKAGE_NAME})
SET(DOC_DIR "share/doc/${CPACK_PACKAGE_NAME}")

########################################################################
# Create uninstall targets
########################################################################
CONFIGURE_FILE(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake_uninstall.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake"
    IMMEDIATE @ONLY)

ADD_CUSTOM_TARGET(uninstall_ospecorr
    COMMAND ${CMAKE_COMMAND} -P ${CMAKE_CURRENT_BINARY_DIR}/cmake_uninstall.cmake)

########################################################################
# Add the subdirectories
########################################################################
ADD_SUBDIRECTORY(message-defs)
ADD_SUBDIRECTORY(scl)
ADD_SUBDIRECTORY(components)

########################################################################
# Print summary
########################################################################
MESSAGE(STATUS "Using install prefix: ${CMAKE_INSTALL_PREFIX}")
