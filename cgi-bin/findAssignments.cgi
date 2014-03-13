#!python2.7virt/venv/bin/python
# return a list of semesters, departments, classes, assignments
# this is basically the folder structure for ../data/classes:
# ../data/classes/[semester]/[dept]/[class]/assignment_[assignmentNum]

import cgi,sys,os
import cgitb
import json

cgitb.enable()
dataDir = "../data/"
classesDir = "classes"
baseDirLen = len((dataDir+classesDir).split('/'))-1

# traverse root directory, and list directories as dirs and files as files
dirStructure = []
semesters=[]
departments=[]
classes=[]
assignments=[]

for root, dirs, files in os.walk(dataDir+classesDir):
    if root.count(os.sep) >= 6:
    	del dirs[:]
    #print root,root.count(os.sep)
    if 'metadata' in root:
        continue
    if root.count(os.sep)==3:
        semesters.append(root.split(os.sep)[3:])
    elif root.count(os.sep)==4:
        departments.append(root.split(os.sep)[3:])
    elif root.count(os.sep)==5:
        classes.append(root.split(os.sep)[3:])
    elif root.count(os.sep)==6:
        try:
                with open(root+'/metadata/assignmentName.txt',"r") as f:
                        root = root + ' ('+f.readline()[:-1]+')'
        except:
                pass # no worries if the assignment name file doesn't exist
        assignments.append(root.split(os.sep)[3:])

semesters.sort()
departments.sort()
classes.sort()
assignments.sort()
dirStructure={'semester':semesters,'department':departments,'course':classes,'assignment':assignments}

sys.stdout.write("Content-Type: application/json")
sys.stdout.write("\n")
sys.stdout.write("\n")
print json.dumps(dirStructure)

