#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
import json

cgitb.enable()
dataDir = "../data/"
classesDir = "classes/"
metaDataDir = "metadata/"

#sys.stdout.write("Content-Type: application/json")
sys.stdout.write("Content-Type: text/plain")
sys.stdout.write("\r\n")
sys.stdout.write("\r\n")

form = cgi.FieldStorage()
# courseDir should be in the form 'semester/department/class/'
assignmentDir = form['courseDir'].value
userToken = form['userToken'].value

with open(dataDir+classesDir+assignmentDir+metaDataDir+'graders.txt',"r") as f:
    token,remoteUser,userType = f.readline()[:-1].split(',')

print token,remoteUser,userType