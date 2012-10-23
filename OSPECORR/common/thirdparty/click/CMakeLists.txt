include(ExternalProject)
ExternalProject_Add(click
   #DOWNLOAD_COMMAND
   GIT_REPOSITORY git://read.cs.ucla.edu/git/click
   UPDATE_COMMAND ""
   CONFIGURE_COMMAND <SOURCE_DIR>/configure --disable-linuxmodule
)
