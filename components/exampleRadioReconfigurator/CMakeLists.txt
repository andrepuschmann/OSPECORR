########################################################################
# Add executables
########################################################################
ADD_EXECUTABLE (exampleRadioReconfigurator exampleRadioReconfigurator.cpp)
TARGET_LINK_LIBRARIES (exampleRadioReconfigurator boost_thread boost_program_options ${OSPECORR_LIBS})

INCLUDE_DIRECTORIES(${PROJECT_SOURCE_DIR}/lib/utility)

INSTALL(TARGETS exampleRadioReconfigurator
    LIBRARY DESTINATION ${LIBRARY_DIR} # .so file
    ARCHIVE DESTINATION ${LIBRARY_DIR} # .lib file
    RUNTIME DESTINATION ${RUNTIME_DIR} # .dll file
)
