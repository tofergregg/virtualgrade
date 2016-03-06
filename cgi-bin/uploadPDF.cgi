#!/bin/bash
# wrapper for uploadPDFPython.cgi to include a library path
export LD_LIBRARY_PATH=/h/cgregg/local/lib:/usr/sup/lib64:/usr/sup/lib64:/usr/sup/lib:$LD_LIBRARY_PATH
./uploadPDFPython.cgi "$!"
