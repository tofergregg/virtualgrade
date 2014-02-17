#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
import subprocess
import uuid
import threading
import shutil
import time

cgitb.enable()
dataDir = "../data/"
classesDir = "classes/"
userLockfilesDir = "metadata/lockfiles/"
logDir = "log/"


sys.stdout.write("Content-Type: text/html")
sys.stdout.write("\n")
sys.stdout.write("\n")

try:
    form = cgi.FieldStorage()
    print form.keys()
    remoteUser = form['remoteUser'].value
    
    if remoteUser != os.environ['REMOTE_USER']:
        print "Unauthorized"
        quit()

    # courseLocation should be in the form:
    # 'semester/department/course/assignment/'
    courseLocation = form['courseLocation'].value
    unpublish = form['unpublish'].value
    
except:
    remoteUser = sys.argv[1]
    courseLocation = sys.argv[2]
    unpublish = "No"

unpublished = False
published = False

now = time.strftime("%c")

if unpublish == "Yes":
        try:
                os.remove(dataDir+classesDir+'/'+courseLocation+'metadata/published')
                unpublished = True
                with open(dataDir+logDir+'virtualgrade.log','a') as f:
		    f.write('unpublished,'+remoteUser+','+
			    now+','+
			    courseLocation+'\n')
        except OSError:
                unpublished = False
        
else:
        try:
                with open(dataDir+classesDir+courseLocation+'metadata/published',"w"):
                        published = True
                        with open(dataDir+logDir+'virtualgrade.log','a') as f:
		                f.write('published,'+remoteUser+','+
			        now+','+
			        courseLocation+'\n')
		published = True
	except IOError:
	        published = False
	        print "Error in file:",dataDir+classesDir+courseLocation+'metadata/published'
        
if unpublish == "Yes":
        if unpublished:
		sys.stdout.write("Unpublished grades for course: "+courseLocation+".");
	else:
		sys.stdout.write("Could not unpublish grades for course: "+courseLocation+".");
		
else:
	if published:
		sys.stdout.write("Published grades for course: "+courseLocation+".");
	else:
		sys.stdout.write("Could not publish grades for course: "+courseLocation+".");


