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

if os.path.isfile(dataDir+classesDir+'/'+courseLocation+'metadata/published'):
        print "true"
else:
        print "false"
