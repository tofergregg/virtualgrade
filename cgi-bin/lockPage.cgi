#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
import subprocess
import uuid
import threading
import time,datetime

cgitb.enable()
dataDir = "../data/"
classesDir = "classes/"
userLockfilesDir = "metadata/lockfiles/"
logDir = "log/"

try:
    form = cgi.FieldStorage()

    remoteUser = form['remoteUser'].value

    # studentToLock should be in the form:
    # 'semester/department/course/assignment/studentId/'
    studentToLock = form['studentToLock'].value

    # pageToLock should be in the form:
    # pageX.png
    pageToLock = form['pageToLock'].value
except:
    remoteUser = sys.argv[1]
    studentToLock = sys.argv[2]
    pageToLock = sys.argv[3]

# lock code modified from:
# http://stackoverflow.com/a/3322242/561677

user_lockfile = dataDir+classesDir+studentToLock+userLockfilesDir+pageToLock+'_'+remoteUser+'.lock'
page_lockfile = dataDir+classesDir+studentToLock+pageToLock+'.lock'

# create the user_lockfile and populate it with info
now = time.strftime("%c")
with open(user_lockfile, 'w') as f:
    f.write(remoteUser+'\n')
    f.write(now+'\n')

lockAcquired = False
#while not lockAcquired:
try:
    os.link(user_lockfile, page_lockfile)
except:
    lockAcquired = (os.stat(user_lockfile).st_nlink == 2)
else:
    lockAcquired = True

# update log file
if lockAcquired:
    lockAcquired="locked"
else:
    lockAcquired="failed"
with open(dataDir+logDir+'virtualgrade.log','a') as f:
    f.write('lock,'+remoteUser+','+
            now+','+
            studentToLock+pageToLock+','+
            lockAcquired+'\n')

sys.stdout.write("Content-Type: text/plain")
sys.stdout.write("\n")
sys.stdout.write("\n")
sys.stdout.write("status:"+str(lockAcquired)+"\n")

#To unlock:
#unlink(global_lockfile)
#lockAcquired = False
