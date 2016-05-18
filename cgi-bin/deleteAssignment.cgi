#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
import subprocess
import uuid
import threading
import shutil
import time
import json
import math

cgitb.enable()
dataDir = "../data/"
gradesDir = "../../grades/data/allGrades/"
classesDir = "classes/"
logDir = "log/"

sys.stdout.write("Content-Type: text/html")
sys.stdout.write("\n")
sys.stdout.write("\n")

try:
    form = cgi.FieldStorage()
    #print form.keys()
    remoteUser = form['remoteUser'].value
    
    if remoteUser != os.environ['REMOTE_USER']:
        print "Unauthorized"
        quit()

    # courseLocation should be in the form:
    # 'semester/department/course/assignment/'
    courseLocation = form['courseLocation'].value
    
except:
    remoteUser = sys.argv[1]
    courseLocation = sys.argv[2]

now = time.strftime("%c")

try:
        # kill assignment with fire
        dirToDelete = dataDir+classesDir+courseLocation
        print(dirToDelete)
        print(subprocess.check_output(['rm','-r',dirToDelete]))
        # delete published assignments        
#        grades_filename = gradesDir+courseLocation.replace('/','-')
#        if grades_filename[-1]=='-':
#                grades_filename = grades_filename[:-1]
#        grades_filename += ".txt"
#        os.remove(grades_filename)
#        with open(dataDir+logDir+'virtualgrade.log','a') as f:
#            f.write('deleted_assignment,'+remoteUser+','+
#                    now+','+
#                    courseLocation+'\n')
        print("Deleted assignment.")
except OSError:
        print "Could not delete assignment."
        

