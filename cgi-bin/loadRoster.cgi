#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
import json

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
except:
        semester = "2016-spring"
	deptName = sys.argv[1]
	course = sys.argv[2]
	
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

sys.stdout.write("Content-Type: application/json")
#sys.stdout.write("Content-Type: text/html")
sys.stdout.write("\r\n")
sys.stdout.write("\r\n")

if rosterFound:
	print json.dumps(roster)
else:
	print json.dumps([]) # not found


