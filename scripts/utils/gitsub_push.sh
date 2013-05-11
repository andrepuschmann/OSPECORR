#!/bin/sh
git submodule foreach $MOBICOM_PATH/common/scripts/utils/git_push.sh && git push
