########################################################################
# look for requried libraries
########################################################################
FIND_PACKAGE( OSPECORR QUIET )

########################################################################
# Add executables
########################################################################
ADD_EXECUTABLE (examplePhySubscriber examplePhySubscriber.cpp)
TARGET_LINK_LIBRARIES (examplePhySubscriber ${OSPECORR_LIBS})
