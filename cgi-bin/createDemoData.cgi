#!/bin/bash
# wrapper for createDemoDataPython.cgi to include a library path
export LD_LIBRARY_PATH=/h/cgregg/local/lib:/usr/sup/lib64:/usr/sup/lib64:/usr/sup/lib:$LD_LIBRARY_PATH
./convertDemoDataPython.cgi "$!"
