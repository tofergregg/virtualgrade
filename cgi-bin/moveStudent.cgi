#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
import subprocess
import uuid
import threading
import shutil
import time

cgitb.enable()
dataDir = "../data/"
classesDir = "classes/"
userLockfilesDir = "metadata/lockfiles/"
logDir = "log/"


sys.stdout.write("Content-Type: text/html")
sys.stdout.write("\n")
sys.stdout.write("\n")

try:
    form = cgi.FieldStorage()
    print form.keys()
    remoteUser = form['remoteUser'].value

    # dirToChange should be in the form:
    # 'semester/department/course/assignment/'
    dirToChange = form['dirToChange'].value
    
    # studentToChange should be in the form studentId
    studentToChange = form['studentToChange'].value

    # pageToLock should be in the form:
    # pageX.png
    oldPage = form['oldPage'].value
    newName = form['newName'].value
    newPage = form['newPage'].value
except:
    remoteUser = sys.argv[1]
    dirToChange = sys.argv[2]
    studentToChange = sys.argv[3]
    newName = sys.argv[4]
    newPage = sys.argv[5]
    oldPage = sys.argv[6]

print studentToChange
print newName
print newPage
print oldPage
print dirToChange
try:
        try:
                os.makedirs(dataDir+classesDir+dirToChange+newName)
        except OSError:
                pass # if already created, don't worry about it
        print dataDir+classesDir+dirToChange+studentToChange+'/page'+oldPage
        print dataDir+classesDir+dirToChange+newName+'/page'+newPage
        os.rename(dataDir+classesDir+dirToChange+studentToChange+'/page'+oldPage+'.png', 
                        dataDir+classesDir+dirToChange+newName+'/page'+newPage+'.png')
        nameChanged = True
except OSError:
        nameChanged = False
        

if nameChanged:
        sys.stdout.write("Successfully changed "+studentToChange+" to "+newName+"\n");
else:
        sys.stdout.write("Could not change "+studentToChange+" to "+newName);
        # update log file
        now = time.strftime("%c")
        with open(dataDir+logDir+'virtualgrade.log','a') as f:
            f.write('rename,'+remoteUser+','+
                    now+','+
                    studentToChange+','
                    +newName+'\n')

