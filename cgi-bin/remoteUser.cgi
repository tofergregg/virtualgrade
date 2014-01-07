#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
import uuid
import time
import json

cgitb.enable()
dataDir = "../data/"
classesDir = "classes/"
metadataDir = "metadata/"
userDatabase = "users.txt"
logDir = "log/"

sys.stdout.write("Content-Type: application/json")
sys.stdout.write("\n")
sys.stdout.write("\n")

remoteUser = os.environ['REMOTE_USER']

with open(dataDir+userDatabase,"r") as f:
    for line in f:
        rights = 'unauthorized'
        if not ',' in line: break
        databaseUserId,rights=line[:-1].split(',')
        if databaseUserId==remoteUser: break

print json.dumps({'remoteUser':remoteUser,'rights':rights})
