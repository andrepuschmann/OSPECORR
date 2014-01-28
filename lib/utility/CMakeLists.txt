########################################################################
# Custom target to ensure headers get picked up by IDEs
########################################################################
SET(headers
    OspecorrHelper.h
)
ADD_CUSTOM_TARGET(libutilityheaders SOURCES ${headers})
