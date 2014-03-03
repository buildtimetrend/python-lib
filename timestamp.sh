#!/bin/bash
# usage : ./timestamp.sh timestamp_name
echo $1 : `date +%s`
#echo \"$1\",\"`date +%s`\" >> $BUILD_LOGFILE
