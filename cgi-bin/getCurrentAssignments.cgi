#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
import json

cgitb.enable()
dataDir = "../data/"
classesDir = "classes/"
semester = "2014-spring"
metaDataDir = "metadata/"

form = cgi.FieldStorage()

try:
	deptName = form['department'].value
	course = form['classNum'].value
except:
	deptName = sys.argv[1]
	course = sys.argv[2]
	
# list the directories for the assignment
classDir = dataDir+classesDir+semester+'/'+deptName+'/'+str(course)+'/'

try:
    dirList = os.listdir(classDir)
    classFound = True
except OSError:
    classFound = False
    
assignmentList = []
sys.stdout.write("Content-Type: application/json")
#sys.stdout.write("Content-Type: text/html")
sys.stdout.write("\r\n")
sys.stdout.write("\r\n")
if classFound:
	# ditch everything that doesn't have a "_digit" extension,
	# and add the rest to assignmentList
	for f in dirList:
		assignmentNum = f.split('_')[-1]
		if assignmentNum.isdigit():
			assignmentList.append(int(assignmentNum))
	assignmentList.sort()
	assignmentList = [str(x) for x in assignmentList]
	
	# make into a hokey dictionary
	#print json.dumps(dict(zip(assignmentList,assignmentList)))
	print json.dumps(assignmentList,assignmentList)
else:
	print json.dumps([]) # not found


