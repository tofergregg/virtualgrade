#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
import subprocess
import uuid
import threading
import time
import json

#cgitb.enable()
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

# get points information for assignment
pointsFile = dataDir+classesDir+assignment+metadataDir+pointValuesFilename
with open(pointsFile,"r") as f:
    points = f.readline()[:-1].split(',')
    points = [int(x) for x in points]
    
# list students in directory
assignmentDir = dataDir+classesDir+assignment
dirListing = sorted(os.listdir(assignmentDir))
if 'metadata' in dirListing:
    dirListing.remove('metadata')

# list graded and ungraded assignments per student
studentAssignments = []
for student in dirListing:
    studentDir = assignmentDir+student+'/'
    filesList = sorted(os.listdir(studentDir))
    # sort so page9.png comes before page10.png, etc.
    specialSort(filesList)
    filesList = specialSort(filesList)

    partialUngraded=[]
    ungradedToRemove=[]
    graded=[]
    locked=[]
    for file in filesList:
        if 'metadata' in file:
            continue
        elif '.lock' in file:
            # read lock file for info
            with open(studentDir+file,"r") as f:
                remoteUser=f.readline()[:-1]
                lockTime=f.readline()[:-1]
            locked.append((student,file,remoteUser,lockTime))
        elif '_graded' in file:
            graded.append(file)
            ungradedToRemove.append(file.replace('_graded',''))
        elif file.endswith('.pdf'):
            continue
        else:
            partialUngraded.append(file)
    # create the proper ungraded file
    ungraded = [x for x in partialUngraded if x not in ungradedToRemove]
    studentAssignments.append((student,ungraded,graded,locked))

print json.dumps({'points':points,'students':studentAssignments})
