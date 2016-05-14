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
        userData = json.loads(form['userData'].value)

except:
        remoteUser = sys.argv[1]
        userData = sys.argv[2]

# read data/users.txt
with open(dataDir+"users.txt","w") as f:
        # should have locking mechanism!
        f.write(json.dumps(userData)+'\n')

sys.stdout.write("Content-Type: text/plain")
sys.stdout.write("\n")
sys.stdout.write("\n")
print('Saved data')

now = time.strftime("%c")
with open(dataDir+logDir+'virtualgrade.log','a') as f:
        f.write('saveUsers,'+remoteUser+','+
                        now+'\n')



