#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
import time,datetime

dataDir = "../data/"
classesDir = "classes/"
metadataDir = "metadata/"
logDir = "log/"

cgitb.enable()

sys.stdout.write("Content-Type: text/html")
sys.stdout.write("\n")
sys.stdout.write("\n")

form = cgi.FieldStorage()

# studentDir should be in the form
# 'semester/department/course/assignment/studentId/
studentDir = form['studentDir'].value

# pageName should be in the form: pageX.grd'
pageName = form['pageName'].value

grade = form['grade'].value
print "Grade:",grade
remoteUser = form['remoteUser'].value
gradeMax = form['gradeMax'].value

authTime=time.time()
humanReadableAuthTime=str(datetime.datetime.fromtimestamp(authTime))

with open(dataDir+classesDir+studentDir+metadataDir+pageName, "wb") as f:
    f.write(grade+','+remoteUser+','+humanReadableAuthTime+','+repr(authTime)+','+gradeMax+'\n')
    
# update log file
now = time.strftime("%c")
with open(dataDir+logDir+'virtualgrade.log','a') as f:
    f.write('grade,'+remoteUser+','+
            now+','+
            studentDir+metadataDir+pageName+','+
            grade+','+
            gradeMax+','+
            '\n')

sys.stdout.write("Content-Type: text/html")
sys.stdout.write("\r\n")
sys.stdout.write("\r\n")
print ("Grade saved.")
