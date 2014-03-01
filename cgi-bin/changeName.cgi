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

    # dirToChange should be in the form:
    # 'semester/department/course/assignment/'
    dirToChange = form['dirToChange'].value
    
    # studentToChange should be in the form studentId
    studentToChange = form['studentToChange'].value

    # pageToLock should be in the form:
    # pageX.png
    newName = form['newName'].value
except:
    remoteUser = sys.argv[1]
    dirToChange = sys.argv[2]
    studentToChange = sys.argv[3]
    newName = sys.argv[4]

if newName == "...DELETE": # delete instead of remove
	deleteStudent = True
	try:
		shutil.rmtree(dataDir+classesDir+dirToChange+studentToChange+'/')
		deleted=True
	except:
		deleted=False
else:
	deleteStudent = False
        try:
		os.rename(dataDir+classesDir+dirToChange+studentToChange, dataDir+classesDir+dirToChange+newName)
		nameChanged = True
		try:
                        # also rename the PDF if it exists
                        oldPdfFilename = dataDir+classesDir+dirToChange+newName+'/'+studentToChange+'_Full.pdf'
                        newPdfFilename = dataDir+classesDir+dirToChange+newName+'/'+newName+'_Full.pdf'
                        if os.path.isfile(oldPdfFilename):
                                os.rename(oldPdfFilename,newPdfFilename)
                except:
                        print "Could not change PDF!"	        
	except OSError:
		nameChanged = False
        

sys.stdout.write("Content-Type: text/html")
sys.stdout.write("\n")
sys.stdout.write("\n")
if deleteStudent:
	if deleted:
		sys.stdout.write("Successfully deleted "+studentToChange+".");
	else:
		sys.stdout.write("Could not delete "+studentToChange+".");
		# update log file
		now = time.strftime("%c")
		with open(dataDir+logDir+'virtualgrade.log','a') as f:
		    f.write('deleted,'+remoteUser+','+
			    now+','+
			    studentToChange+'\n')
else:
	if nameChanged:
		sys.stdout.write("Successfully changed "+studentToChange+" to "+newName+"\n");
	else:
		sys.stdout.write("Could not change "+studentToChange+" to "+newName);
		# update log file
		now = time.strftime("%c")
		with open(dataDir+logDir+'virtualgrade.log','a') as f:
		    f.write('rename,'+remoteUser+','+
			    now+','+
			    studentToChange+','
			    +newName+'\n')



