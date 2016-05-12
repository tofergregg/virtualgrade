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

    # dirToChange should be in the following form: 
    # 'semester/department/course/assignment/studentId/'
    dirToChange = form['dirToChange'].value
    pageNum = int(form['pageNum'].value)
    newPoints = form['newPoints'].value

except:
    remoteUser = sys.argv[1]
    dirToChange = sys.argv[2]
    pageNum = sys.argv[3]
    newPoints = '10'
    
# update metadata/point_values.csv
pointsFile=dataDir+classesDir+dirToChange+"metadata/point_values.csv"
with open(pointsFile) as f:
        points = f.readline()[:-1].split(",")

points[pageNum]=newPoints

with open(pointsFile,"w") as f:
        line=','.join(points)
        f.write(line+'\n')

sys.stdout.write("Content-Type: text/html")
sys.stdout.write("\n")
sys.stdout.write("\n")
sys.stdout.write("Updated points for page "+str(pageNum)+" to "+str(newPoints)+"\n");
print(points)

# update log file
now = time.strftime("%c")
with open(dataDir+logDir+'virtualgrade.log','a') as f:
    f.write('updatedPagePoints,'+remoteUser+','+
            now+','+
            str(pageNum)+'\n')


