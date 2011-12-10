# set project's name
PROJECT( pySysMoCo )

SET( MAIN_UI ./ui/gui.ui )
  
  
  
  # by default only QtCore and QtGui modules are enabled
  # other modules must be enabled like this:
  #SET( QT_USE_QT3SUPPORT TRUE )   
  #SET( QT_USE_QTXML TRUE )
  
# this command finds Qt4 libraries and sets all required variables
# note that it's Qt4, not QT4 or qt4
FIND_PACKAGE( Qt4 REQUIRED )
  
# add some useful macros and variables
# (QT_USE_FILE is a variable defined by FIND_PACKAGE( Qt4 ) that contains a path to CMake script)
INCLUDE( ${QT_USE_FILE} )
  
  
# this will run uic on .ui files:
QT4_WRAP_UI( SAMPLE_UI_HDRS ${MAIN_UI} )
  
# and finally this will run moc:
#QT4_WRAP_CPP( SAMPLE_MOC_SRCS ${SAMPLE_MOC_HDRS} )

INSTALL(FILES pythonSubscriber.py DESTINATION ${CMAKE_CURRENT_BINARY_DIR})


