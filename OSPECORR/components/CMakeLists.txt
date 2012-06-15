# these are optional components of OSPECORR
IF(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/iris2/")
ADD_SUBDIRECTORY (iris2)
ENDIF(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/iris2/")
IF(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/drmcontroller/")
ADD_SUBDIRECTORY (drmcontroller)
ENDIF(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/drmcontroller/")
IF(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/drmgenerator/")
ADD_SUBDIRECTORY (drmgenerator)
ENDIF(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/drmgenerator/")
# these are the mandatory components
ADD_SUBDIRECTORY (pySysMoCo)
ADD_SUBDIRECTORY (examplePhyPublisher)
ADD_SUBDIRECTORY (examplePhySubscriber)
