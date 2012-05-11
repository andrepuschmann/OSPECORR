MESSAGE(STATUS "Checking for OSPECORR")

SET(OSPECORR_FOUND 0)

# trivial check
IF(${MOBICOM_PROJECT_NAME} MATCHES "OSPECORR")
  SET(OSPECORR_FOUND 1)
  MESSAGE(STATUS "Found OSPECORR")
  SET(OSPECORR_LIBS "scl_messages" "scl_shared" "zmq" "yaml-cpp" "protobuf" )
  INCLUDE_DIRECTORIES(${CMAKE_SOURCE_DIR}/common/thirdparty/yaml-cpp-0.2.7/include)
  INCLUDE_DIRECTORIES($ENV{MOBICOM_PROJECT_BUILD_PATH}/common/message-defs)
ELSE(${MOBICOM_PROJECT_NAME} MATCHES "OSPECORR")
  MESSAGE(STATUS "OSPECORR not found")
ENDIF(${MOBICOM_PROJECT_NAME} MATCHES "OSPECORR")