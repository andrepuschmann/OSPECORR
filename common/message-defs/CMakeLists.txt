# This is a nice CMakeLists.txt file which scans through the
# current path an compiles all .proto files it finds
# At the end it generates libmessages.a which the final
# application just has to link againt.
#
# Taken from:
# http://pragma-once.blogspot.com/2011/01/google-protobufs-and-cmake.html

#protobuf input - finds all .proto files in the current dir
file(GLOB PROTO_INPUT
RELATIVE ${CMAKE_CURRENT_SOURCE_DIR}
"*.proto")

#protobuf compiler
find_program(PROTOC protoc)
set(PROTOC_C_OUT_FLAG --cpp_out)

#protobuf output
set(PROTO_GEN_DIR ${CMAKE_CURRENT_BINARY_DIR})
foreach(PROTO_FILE ${PROTO_INPUT})
#get the name of the file without extension
get_filename_component(PROTO_NAME ${PROTO_FILE} NAME_WE)
#add the generated files
set(PROTO_GEN ${PROTO_GEN}
${PROTO_GEN_DIR}/${PROTO_NAME}.pb.h
${PROTO_GEN_DIR}/${PROTO_NAME}.pb.cc)
endforeach(PROTO_FILE ${PROTO_INPUT})

# add the custom command that will generate all the files
add_custom_command(
OUTPUT ${PROTO_GEN}
COMMAND ${PROTOC} ${PROTO_INPUT} ${PROTOC_C_OUT_FLAG} ${CMAKE_CURRENT_BINARY_DIR}
DEPENDS ${PROTOC} ${PROTO_INPUT}
WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

#message(STATUS "PROTO_GEN: ${PROTO_GEN}" )

# Static library (test code can link against this)
ADD_LIBRARY(messages STATIC ${PROTO_GEN})
