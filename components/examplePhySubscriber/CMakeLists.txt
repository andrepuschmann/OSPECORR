########################################################################
# Add executables
########################################################################
ADD_EXECUTABLE (examplePhySubscriber examplePhySubscriber.cpp)
TARGET_LINK_LIBRARIES (examplePhySubscriber ${OSPECORR_LIBS})

INSTALL(TARGETS examplePhySubscriber
    LIBRARY DESTINATION ${LIBRARY_DIR} # .so file
    ARCHIVE DESTINATION ${LIBRARY_DIR} # .lib file
    RUNTIME DESTINATION ${RUNTIME_DIR} # .dll file
)
