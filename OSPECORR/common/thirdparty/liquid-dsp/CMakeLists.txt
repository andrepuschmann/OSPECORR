include(ExternalProject)
ExternalProject_Add(liquid-dsp
   DOWNLOAD_COMMAND
   URL http://ganymede.ece.vt.edu/downloads/liquid-dsp-1.2.0.tar.gz
   BUILD_IN_SOURCE 1
   UPDATE_COMMAND <SOURCE_DIR>/reconf
   CONFIGURE_COMMAND <SOURCE_DIR>/configure
)
