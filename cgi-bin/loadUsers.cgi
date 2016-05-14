#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
import subprocess
import uuid
import threading
import shutil
import time
import json

cgitb.enable()
dataDir = "../data/"
classesDir = "classes/"
userLockfilesDir = "metadata/lockfiles/"
logDir = "log/"



try:
        form = cgi.FieldStorage()
        remoteUser = form['remoteUser'].value

except:
        remoteUser = sys.argv[1]

# read data/users.txt
users=[]
with open(dataDir+"users.txt","r") as f:
        # will be in json form
        users = json.loads(f.read())

sys.stdout.write("Content-Type: application/json")
sys.stdout.write("\n")
sys.stdout.write("\n")
print(json.dumps(users))

now = time.strftime("%c")
with open(dataDir+logDir+'virtualgrade.log','a') as f:
        f.write('loadUsers,'+remoteUser+','+
                        now+'\n')



