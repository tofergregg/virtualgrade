#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
import subprocess
import uuid
import threading
import shutil
import time
import json
from subprocess import call

cgitb.enable()
dataDir = "../data/"
classesDir = "classes/"
userLockfilesDir = "metadata/lockfiles/"
logDir = "log/"

database='../.htgroup.dbase'
groupName='graders'

try:
        form = cgi.FieldStorage()
        remoteUser = form['remoteUser'].value
        toAdd = json.loads(form['toAdd'].value)
        toDelete = json.loads(form['toDelete'].value)

except:
        remoteUser = sys.argv[1]
        toAdd = '' 
        toDelete = '' 

# read and parse database
users=[]
with open(database,"r") as f:
        for line in f:
                line = line[:-1] # remove newline
                if groupName in line or line.startswith('#'): 
                        # ignore groupName and comments
                        # (comments will be discarded)
                        continue
                username = line.split(' ')[0]
                if username != '':
                        users.append(username) # assume one user per line

for user in toDelete:
        # remove users first
        if user in users:
                users.remove(user)

for user in toAdd:
        # add the toAdd users
        if user not in users:
                users.append(user)

# save the new list of users
with open(database,"w") as f:
        f.write(groupName+': \\\n') # group name
        for user in users:
                f.write(user+' \\\n')
        f.write('\n') # need the extra newline
'''
# add users
# called like this: ./updateGradersDatabase cgregg add abc01
for user in toAdd:
        call(['./updateGradersDatabase',remoteUser,'add',user])

# delete users
# called like this: ./updateGradersDatabase cgregg add abc01
for user in toDelete:
        call(['./updateGradersDatabase',remoteUser,'remove',user])
'''

sys.stdout.write("Content-Type: text/plain")
sys.stdout.write("\n")
sys.stdout.write("\n")
print('Added and deleted users')

now = time.strftime("%c")
with open(dataDir+logDir+'virtualgrade.log','a') as f:
        f.write('add_delete_users,'+remoteUser+','+
                        now+'\n')



