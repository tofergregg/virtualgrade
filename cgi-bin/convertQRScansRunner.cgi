#!/bin/bash
export LD_LIBRARY_PATH=/h/cgregg/local/lib:$LD_LIBRARY_PATH
./convertQRScans.cgi "$@"

