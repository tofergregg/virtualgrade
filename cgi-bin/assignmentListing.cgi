#!python2.7virt/venv/bin/python
# return a list of semesters, departments, classes, assignments
# this is basically the folder structure for ../data/classes:
# ../data/classes/[semester]/[dept]/[class]/assignment_[assignmentNum]

import cgi,sys,os
import cgitb
import json

cgitb.enable()
dataDir = "../data/"
classesDir = "classes/"
baseDirLen = len((dataDir+classesDir).split('/'))-1

# traverse root directory, and list directories as dirs and files as files
dirStructure = []
for root, dirs, files in os.walk(dataDir+classesDir):
    rootPartial = root[len(dataDir+classesDir):]
    if rootPartial.startswith('.'): continue # ignore folders that start with period
    if rootPartial.startswith('metadata'): continue # ignore metadata directories
    dirsPartial=sorted([x for x in dirs if not (x.startswith('.') or x.startswith('metadata'))])
    filesPartial=sorted([x for x in files if not (x.startswith('.') or x.startswith('metadata'))])
    if 'assignmentName.txt' in filesPartial:
        # append (assignment name) onto the assignment (hacky...)
        with open(root+'/assignmentName.txt',"r") as f:
            assignmentName = f.readline()[:-1]
        partialAssignment = rootPartial.split('/')[-2]
        rootToFind = ''.join([x+'/' for x in rootPartial.split('/')[:3]])[:-1]
        for rp,dp,fp in dirStructure:
            if rp==rootToFind:
                dp[dp.index(partialAssignment)]=partialAssignment+' ('+assignmentName+')'
        
    dirStructure.append((rootPartial,dirsPartial,filesPartial))

sys.stdout.write("Content-Type: application/json")
sys.stdout.write("\n")
sys.stdout.write("\n")
print json.dumps(dirStructure)


