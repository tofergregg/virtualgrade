#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
import subprocess
import uuid
import threading
import time

cgitb.enable()
dataDir = "../data/"
classesDir = "classes/"
userLockfilesDir = "metadata/lockfiles/"
logDir = "log/"

try:
    form = cgi.FieldStorage()
    remoteUser = form['remoteUser'].value

    # studentToLock should be in the form:
    # 'semester/department/course/assignment/studentId/'
    studentToLock = form['studentToLock'].value

    # pageToLock should be in the form:
    # pageX.png
    pageToLock = form['pageToLock'].value
except:
    remoteUser = sys.argv[1]
    studentToLock = sys.argv[2]
    pageToLock = sys.argv[3]

# lock code modified from:
# http://stackoverflow.com/a/3322242/561677

user_lockfile = dataDir+classesDir+studentToLock+userLockfilesDir+pageToLock+'_'+remoteUser+'.lock'
page_lockfile = dataDir+classesDir+studentToLock+pageToLock+'.lock'

sys.stdout.write("Content-Type: text/html")
sys.stdout.write("\n")
sys.stdout.write("\n")

try:
    os.unlink(user_lockfile)
except:
    pass # we don't really care if this file gets deleted
         # If it stays, it will be junk, but not problematic

try:
    os.unlink(page_lockfile) # we do care that this one works.
    print "unlocked."
    unlocked='unlocked'
except OSError as e:
    # not good.
    print "ERROR: could not unlock file! Filename: "+page_lockfile
    unlocked='failed'

# update log file
now = time.strftime("%c")
with open(dataDir+logDir+'virtualgrade.log','a') as f:
    f.write('unlock,'+remoteUser+','+
            now+','+
            studentToLock+pageToLock+','+
            unlocked+'\n')



