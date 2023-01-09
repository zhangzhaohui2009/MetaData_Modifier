#!/bin/bash

if [ $# -lt 1 ]; then
 echo "usage: $0 fpath[single nc file or a subdirectory]"
 exit 1
fi
fpath="$1"

python M2OCEAN_global_metadata_main.py $fpath 

