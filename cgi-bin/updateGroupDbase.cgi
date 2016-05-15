#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
import subprocess
import uuid
import threading
import shutil
import time
import json
from subprocess import call

cgitb.enable()
dataDir = "../data/"
classesDir = "classes/"
userLockfilesDir = "metadata/lockfiles/"
logDir = "log/"



try:
        form = cgi.FieldStorage()
        remoteUser = form['remoteUser'].value
        toAdd = json.loads(form['toAdd'].value)
        toDelete = json.loads(form['toDelete'].value)

except:
        remoteUser = sys.argv[1]
        quit()
        toAdd = json.loads(sys.argv[2])
        toDelete = json.loads(sys.argv[3])

# add users
# called like this: ./updateGradersDatabase cgregg add abc01
for user in toAdd:
        call(['./updateGradersDatabase',remoteUser,'add',user])

# delete users
# called like this: ./updateGradersDatabase cgregg add abc01
for user in toDelete:
        call(['./updateGradersDatabase',remoteUser,'remove',user])

sys.stdout.write("Content-Type: text/plain")
sys.stdout.write("\n")
sys.stdout.write("\n")
print('Added and deleted users')

now = time.strftime("%c")
with open(dataDir+logDir+'virtualgrade.log','a') as f:
        f.write('add_delete_users,'+remoteUser+','+
                        now+'\n')



