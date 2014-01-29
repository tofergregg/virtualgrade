#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
import subprocess
import uuid
import threading
import time
import json

cgitb.enable()
dataDir = "../data/"
classesDir = "classes/"
metadataDir = "metadata/"
pointValuesFilename = "point_values.csv"
logDir = "log/"

def specialSort(listToSort):
    # takes a list of files where some files are named "pageX.png" and X can be an integer.
    # We arrange the files so that all the "pageX.png" files are in ascending order by X
    # parse the list, pick out the pageX.png files and parse the X as an integer
    partialList = []
    for value in listToSort:
        if value.startswith('page'):
            if '_graded' in value:
                pageNum = int(value[4:].split('_')[0])
            else:
                pageNum = int(value[4:].split('.')[0])
        else:
            pageNum = 0 # we will sort all other files to the beginning
        partialList.append((value,pageNum))
    partialList = sorted(partialList, key = lambda bothValues: bothValues[1])
    partialList = [x[0] for x in partialList]
    return partialList
try:
    form = cgi.FieldStorage()

    # assignment should be in the form:
    # 'semester/department/course/assignment/'
    assignment = form['assignment'].value

except:
    assignment = sys.argv[1]

sys.stdout.write("Content-Type: application/json")
sys.stdout.write("\n")
sys.stdout.write("\n")

# # get points information for assignment
# pointsFile = dataDir+classesDir+assignment+metadataDir+pointValuesFilename
# with open(pointsFile,"r") as f:
#     points = f.readline()[:-1].split(',')
#     if points!=['']: # we have scores
#         points = [int(x) for x in points]
#     else:
#         points = -1
    
# find all files with ".grd"
assignmentDir = dataDir+classesDir+assignment

output = subprocess.check_output(["find",assignmentDir,'-iname','*.grd'])[:-1]

gradesList = []
if len(output) > 0:
    for line in output.split('\n'):
        studentId = line.split('/')[7]
        pageNum = line.split('/')[9].replace('page','').replace('.grd','')
        with open(line,"r") as f:
            grade,remoteUser,humanReadableTime,timestamp,gradeMax=f.readline()[:-1].split(',')
            gradesList.append({'grade':grade,'remoteUser':remoteUser,
                                'readableTime':humanReadableTime,'timestamp':timestamp,
                                'studentId':studentId,'pageNum':pageNum,'gradeMax':gradeMax})
#print gradesList

print json.dumps({'gradesList':gradesList})
