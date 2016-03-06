#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
import subprocess
import uuid
import threading
import time,datetime
import scipy as sp
from PIL import Image, ImageDraw, ImageFont

cgitb.enable()
dataDir = "../data/"
classesDir = "classes/"
metadataDir = "metadata/"
logDir = "log/"

try:
    form = cgi.FieldStorage()

    remoteUser = form['remoteUser'].value

    # assignmentDir should be in the form:
    # 'semester/department/course/assignment/'
    assignmentDir = form['assignmentDir'].value

except:
    remoteUser = sys.argv[1]
    assignmentDir = sys.argv[2]

assignment = assignmentDir.split('/')[-2]
# get list of student directories
dirListing = sorted(os.listdir(dataDir+classesDir+assignmentDir))
if 'metadata' in dirListing:
    dirListing.remove('metadata')

dirListing = [dataDir+classesDir+assignmentDir+x+'/'+x+'_Full.pdf' for x in dirListing]
zipFile = dataDir+classesDir+assignmentDir+metadataDir+'allExams.zip'
dirListing.insert(0,zipFile)

# remove zip file if it exists already
try:
    os.remove(zipFile)
except:
    pass # we don't care if this fails, as we're going to write to the file next
subprocess.call(["zip"]+['-jq']+dirListing)

# update log file
now = time.strftime("%c")
with open(dataDir+logDir+'virtualgrade.log','a') as f:
    f.write('zippedStudentPdfs,'+remoteUser+','+
            now+','+'\n')

sys.stdout.write("Content-Type: application/zip\n")
sys.stdout.write("Content-Disposition: attachment; filename="+assignment+"_PDFs.zip\n");
sys.stdout.write("\n")
with open(dataDir+classesDir+assignmentDir+metadataDir+'allExams.zip',"rb") as pdfFile:
     while 1:
        chunk = pdfFile.read(4096)
        if not chunk: break
        sys.stdout.write (chunk)

