include(ExternalProject)
ExternalProject_Add(aodv-click
   #DOWNLOAD_COMMAND
   GIT_REPOSITORY git://github.com/andrepuschmann/aodv-click.git
   UPDATE_COMMAND ""
   BUILD_IN_SOURCE 1
   CONFIGURE_COMMAND <SOURCE_DIR>/configure
)
