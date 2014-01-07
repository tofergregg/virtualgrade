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

    # studentDir should be in the form:
    # 'semester/department/course/assignment/studentId/'
    studentDir = form['studentDir'].value

except:
    remoteUser = sys.argv[1]
    studentDir = sys.argv[2]

student = studentDir.split('/')[-2]
assignment = studentDir.split('/')[-3]
# update log file
now = time.strftime("%c")
with open(dataDir+logDir+'virtualgrade.log','a') as f:
    f.write('downloadedStudentExam,'+remoteUser+','+
            now+','+student+'\n')

sys.stdout.write("Content-Type: application/pdf\n")
sys.stdout.write("Content-Disposition: attachment; filename="+student+"_"+assignment+".pdf\n");
sys.stdout.write("\n")
with open(dataDir+classesDir+studentDir+student+'_Full.pdf',"rb") as pdfFile:
     while 1:
        chunk = pdfFile.read(4096)
        if not chunk: break
        sys.stdout.write (chunk)


