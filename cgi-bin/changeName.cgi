#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
import subprocess
import uuid
import threading
import time

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
    dirToChange = form['dirToChange'].value
    studentToChange = form['studentToChange'].value

    # pageToLock should be in the form:
    # pageX.png
    newName = form['newName'].value
except:
    remoteUser = sys.argv[1]
    studentToChange = sys.argv[2]
    newName = sys.argv[3]


try:
        os.rename(dataDir+classesDir+dirToChange+studentToChange, dataDir+classesDir+dirToChange+newName)
        nameChanged = True
except:
        nameChanged = False

sys.stdout.write("Content-Type: text/html")
sys.stdout.write("\n")
sys.stdout.write("\n")
if nameChanged:
        sys.stdout.write("Successfully changed "+studentToChange+" to "+newName);
else:
        sys.stdout.write("Could not change "+studentToChange+" to "+newName);

# update log file
now = time.strftime("%c")
with open(dataDir+logDir+'virtualgrade.log','a') as f:
    f.write('rename,'+remoteUser+','+
            now+','+
            studentToChange+','
            +newName+'\n')



