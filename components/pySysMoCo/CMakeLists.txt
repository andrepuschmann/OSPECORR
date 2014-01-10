# set project's name
PROJECT( pySysMoCo )

SET( PYSYSMOCO_FILES pySysMoCo.py listener.py window.py drmhelper.py gui.ui )

# this command finds Qt4 libraries and sets all required variables
# note that it's Qt4, not QT4 or qt4
FIND_PACKAGE( Qt4 )

# add some useful macros and variables
# (QT_USE_FILE is a variable defined by FIND_PACKAGE( Qt4 ) that contains a path to CMake script)
INCLUDE( ${QT_USE_FILE} )

# Install to local build path and to system wide binary path
INSTALL(FILES ${PYSYSMOCO_FILES} DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
INSTALL(FILES ${PYSYSMOCO_FILES} DESTINATION ${RUNTIME_DIR})
