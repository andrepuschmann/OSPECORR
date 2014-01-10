set(GEN_SHARED 1)
set(GEN_CPP 1)
set(PROTO_MSG_PREFIX "scl_ospecorr_")
INCLUDE( GenProto )

INSTALL(TARGETS scl_ospecorr_messages
    LIBRARY DESTINATION ${LIBRARY_DIR} # .so file
    ARCHIVE DESTINATION ${LIBRARY_DIR} # .lib file
    RUNTIME DESTINATION ${RUNTIME_DIR} # .dll file
)

# If using out-of-source builds, the generated python files (e.g. phy_pb2.py) are 
# stored inside the build path while the setup.py file is inside the source path
# To fix this, try to create a symlink to setup.py and call the install script from
# within the build directory
if (CMAKE_HOST_UNIX)
install(CODE "EXECUTE_PROCESS (COMMAND ln -sf ${CMAKE_CURRENT_SOURCE_DIR}/setup.py ${CMAKE_CURRENT_BINARY_DIR}/setup.py WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} )")
endif(CMAKE_HOST_UNIX)
INSTALL(CODE "execute_process(COMMAND python setup.py install -f --prefix=${CMAKE_INSTALL_PREFIX} WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR})")
