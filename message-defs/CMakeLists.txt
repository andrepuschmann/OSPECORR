set(GEN_SHARED 1)
set(GEN_CPP 1)
set(PROTO_MSG_PREFIX "scl_ospecorr_")
INCLUDE( GenProto )

INSTALL(TARGETS scl_ospecorr_messages
    LIBRARY DESTINATION ${LIBRARY_DIR} # .so file
    ARCHIVE DESTINATION ${LIBRARY_DIR} # .lib file
    RUNTIME DESTINATION ${RUNTIME_DIR} # .dll file
)
