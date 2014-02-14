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
userLockfilesDir = "metadata/lockfiles/"
logDir = "log/"
metadataDir = "metadata/"

try:
    form = cgi.FieldStorage()
    remoteUser = form['remoteUser'].value

    # studentToLock should be in the form:
    # 'semester/department/course/assignment/studentId/'
    dirToChange = form['dirToChange'].value
    pageNum = form['pageNum'].value
    score = form['score'].value

except:
    remoteUser = sys.argv[1]
    dirToChange = sys.argv[2]
    pageNum = sys.argv[3]
    score = 0
    
# for each student in dataDir+classesDir+dirToChange
dirListing = os.listdir(dataDir+classesDir+dirToChange)
dirListing.remove('metadata')
for student in dirListing:
        shutil.copyfile(dataDir+classesDir+dirToChange+'/'+student+'/page'+pageNum+'.png',
                        dataDir+classesDir+dirToChange+'/'+student+'/page'+pageNum+'_graded.png')
                                
        # change score in metadata folder
        authTime=time.time()
        humanReadableAuthTime=str(datetime.datetime.fromtimestamp(authTime))

        pageName = 'page'+pageNum+'.grd'
        with open(dataDir+classesDir+dirToChange+'/'+student+'/'+metadataDir+pageName, "wb") as f:
            f.write('0,'+remoteUser+','+humanReadableAuthTime+','+repr(authTime)+',0\n')
    
        # update log file
        now = time.strftime("%c")
        with open(dataDir+logDir+'virtualgrade.log','a') as f:
            f.write('grade,'+remoteUser+','+
                    now+','+
                    student+'/'+metadataDir+pageName+','+
                    '0'+','+
                    '0'+','+
                    '\n')

sys.stdout.write("Content-Type: text/html")
sys.stdout.write("\n")
sys.stdout.write("\n")

# update log file
now = time.strftime("%c")
with open(dataDir+logDir+'virtualgrade.log','a') as f:
    f.write('changedScoresToZero,'+remoteUser+','+
            now+','+
            pageNum+'\n')



