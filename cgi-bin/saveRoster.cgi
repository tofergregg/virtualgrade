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
        roster = json.loads(form['roster'].value)
except:
        semester = "2016-spring"
	deptName = sys.argv[1]
	course = sys.argv[2]
        roster = ['abc','def']
	
# save roster
try:
        fullDir = dataDir+classesDir+semester+'/'+deptName+'/'+course+'/metadata/'
        # make the metadata directory if it doesn't exist
        if not os.path.exists(fullDir):
                    os.makedirs(fullDir)
        with open(fullDir+'roster.txt','w') as f:
                for student in roster:
                       f.write(student+'\n') 
        rosterFound = True
except EnvironmentError:
        # could not find roster
        rosterFound = False

sys.stdout.write("Content-Type: text/html")
sys.stdout.write("\r\n")
sys.stdout.write("\r\n")

if rosterFound:
	print "Saved roster" 
else:
	print "Could not save roster" # not found


