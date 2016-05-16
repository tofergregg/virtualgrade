#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
import subprocess
import uuid
import threading
import shutil
import time
import json

cgitb.enable()
dataDir = "../data/"
gradesDir = "../../grades/data/"
classesDir = "classes/"
userLockfilesDir = "metadata/lockfiles/"
logDir = "log/"

def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)

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
    unpublish = form['unpublish'].value
    
except:
    remoteUser = sys.argv[1]
    courseLocation = sys.argv[2]
    unpublish = "No"

publishedPath = dataDir+classesDir+courseLocation+'metadata/noStudentPDFs'

if os.path.exists(publishedPath):
        published = True
else:
        published = False

now = time.strftime("%c")

if unpublish == 'Yes':
        try:
                os.remove(publishedPath)
                published=False
        except IOError:
                pass # not much to do if it fails
else:                
        try:
                with open(publishedPath,"w"):
                        published = True
                        with open(dataDir+logDir+'virtualgrade.log','a') as f:
                                f.write('noStudentPDFs,'+remoteUser+','+
                                now+','+
                                courseLocation+'\n')
        except IOError:
                published = False
                print "Error in file:",dataDir+classesDir+courseLocation+'metadata/noStudentPDFs'
        
if published:
        sys.stdout.write("Students will not be shown PDFs: "+courseLocation+".");
else:
        sys.stdout.write("Students will be shown PDFs: "+courseLocation+".");


