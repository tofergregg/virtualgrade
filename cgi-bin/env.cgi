#!/bin/bash

printf "Content-Type: text/plain\n\n"
echo "LD_LIBRARY_PATH:"
echo $LD_LIBRARY_PATH
echo
echo "Full env:"
env
