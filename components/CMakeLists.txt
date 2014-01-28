# these are the mandatory components
ADD_SUBDIRECTORY (pySysMoCo)
ADD_SUBDIRECTORY (examplePhyPublisher)
ADD_SUBDIRECTORY (examplePhySubscriber)
ADD_SUBDIRECTORY (exampleRadioReconfigurator)

# check which version of Iris
IF(NOT IRIS_TUI)
  ADD_SUBDIRECTORY (iris)
  MESSAGE(STATUS "Building public version of Iris.")
ELSE(NOT IRIS_TUI)
  IF(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/iris_tui/")
    ADD_SUBDIRECTORY (iris_tui)
    MESSAGE(STATUS "Building TUI version of Iris.")
  ENDIF(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/iris_tui/")
ENDIF(NOT IRIS_TUI)

# these are optional components of OSPECORR
IF(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/drmcontroller/")
ADD_SUBDIRECTORY (drmcontroller)
ENDIF(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/drmcontroller/")
IF(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/drmgenerator/")
ADD_SUBDIRECTORY (drmgenerator)
ENDIF(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/drmgenerator/")
