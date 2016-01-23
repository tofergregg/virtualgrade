#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
import json

def checkNames(roster,dirList):
        notInRoster = []
        notInAssignment = []
        for name in roster:
                if name not in dirList:
                        notInAssignment.append(name)
        for name in dirList:
                if name not in roster:
                        notInRoster.append(name)
                        
        return notInRoster,notInAssignment

cgitb.enable()
dataDir = "../data/"
classesDir = "classes/"
metaDataDir = "metadata/"

form = cgi.FieldStorage()

try:
        # semester should be in the form '2016-spring'
        semester = form['semester'].value
	deptName = form['department'].value
	course = form['classNum'].value
	assignment = form['assignment'].value
except:
        semester = "2016-spring"
	deptName = sys.argv[1]
	course = sys.argv[2]
	assignment = sys.argv[3]
	
assignmentDir = dataDir+classesDir+semester+'/'+deptName+'/'+course+'/'+assignment+'/'

# read in roster
roster = []
try:
        with open(dataDir+classesDir+semester+'/'+deptName+'/'+course+'/metadata/roster.txt','r') as f:
                for line in f:
                        roster.append(line[:-1])
        rosterFound = True
except EnvironmentError:
        # could not find roster
        rosterFound = False

# list the students in the class
try:
    dirList = os.listdir(assignmentDir)
    classFound = True
    if 'metadata' in dirList:
        dirList.remove('metadata')
    notInRoster,notInAssignment = checkNames(roster,dirList)
except OSError:
    quit()  

#print notInRoster
#print notInAssignment

sys.stdout.write("Content-Type: application/json")
#sys.stdout.write("Content-Type: text/html")
sys.stdout.write("\r\n")
sys.stdout.write("\r\n")

if rosterFound:
	print json.dumps([notInRoster,notInAssignment])
else:
	print json.dumps("Roster not Found") # not found


