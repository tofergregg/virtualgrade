#!python2.7virt/venv/bin/python

import cgi,sys,os
import shutil
import cgitb
import subprocess
import uuid
import threading
import time,datetime

cgitb.enable()
dataDir = "../data/"
classesDir = "classes/"
logDir = "log/"
metadataDir = "metadata/"

try:
    form = cgi.FieldStorage()
    remoteUser = form['remoteUser'].value

    # studentToLock should be in the form:
    # 'semester/department/course/assignment/studentId/'
    dirToChange = form['dirToChange'].value
    bonusPoints = form['bonusPoints'].value

except:
    remoteUser = sys.argv[1]
    dirToChange = sys.argv[2]
    bonusPoints = 4
    
# simply update the bonus points for the assignment in the metadata directory
bonusPointsFile = dataDir+classesDir+dirToChange+metadataDir+"BonusPoints.txt"
with open(bonusPointsFile,"w") as f:
	f.write(bonusPoints+"\n")

sys.stdout.write("Content-Type: text/html")
sys.stdout.write("\n")
sys.stdout.write("\n")
print bonusPointsFile
quit()

# update log file
now = time.strftime("%c")
with open(dataDir+logDir+'virtualgrade.log','a') as f:
    f.write('updatedBonusPoints,'+remoteUser+','+
            now+','+
            bonusPoints+'\n')



