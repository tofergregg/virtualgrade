#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
import subprocess
import uuid
import threading

cgitb.enable()
dataDir = "../data/"
logDir = "log/"

sys.stdout.write("Content-Type: text/plain")
sys.stdout.write("\n")
sys.stdout.write("\n")
sys.stdout.flush()

form = cgi.FieldStorage()

convertId = form['convertId'].value
linesRead = int(form['linesRead'].value)

#print 'linesRead'+str(linesRead)
#print "convertId: " + convertId
with open(dataDir+logDir+convertId+'.log',"r") as f:
    fullFile = f.readlines()
    for line in fullFile[linesRead:]:
        sys.stdout.write(line)
