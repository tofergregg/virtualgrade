#!/usr/sup/bin/python2.7
######!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
import addBubblesToPDF
import createAssignmentPage
import subprocess
import shutil
import uuid
import time

cgitb.enable()
dataDir = "../data/"

form = cgi.FieldStorage()

# save PDF

assignmentFilename = dataDir+'outputfiles/'+str(uuid.uuid4())
assignmentBubblesFilename = dataDir+'outputfiles/'+str(uuid.uuid4())+'.pdf'

with open(assignmentFilename,"wb") as f:
     pdfFile = form['fileToUpload'].file
     while 1:
        chunk = pdfFile.read(4096)
        if not chunk: break
        f.write (chunk)

department = form['department'].value
classNum = form['classNum'].value
assignment = form['assignment'].value

output = subprocess.check_output(["identify",assignmentFilename])
lastLine = output.split('\n')[-2]
pagesInPdf = int(lastLine.split('[')[1].split(']')[0])+1

pagesInPdf = 8
createAssignmentPage.bubblePageUpdate(department,int(classNum),int(assignment),'',pagesInPdf)
# convert the new png to pdf for the merge
subprocess.call(["convert", "-density", "588", dataDir+"bubbleOverlay.png", dataDir+"bubbleOverlay.pdf"])

addBubblesToPDF.mergePDFs(assignmentFilename,assignmentBubblesFilename)

try:
    os.remove(assignmentFilename)
except OSError:
    pass

# fileSize = os.stat(dataDir+assignmentBubblesFilename).st_size
# #sys.stdout.write("Content-Type: application/pdf\r\n")
# #sys.stdout.write("Prama: no-cache\r\n")
# sys.stdout.write("Pragma: public\r\n")
# sys.stdout.write("Cache-Control: must-revalidate, post-check=0, pre-check=0\r\n")
# sys.stdout.write("Cache-Control: private\r\n")
# #sys.stdout.write("Expires: 0\r\n")
# sys.stdout.write("Content-Type: application/octet-stream\r\n")
# sys.stdout.write("Content-Disposition: attachment; filename='"+assignmentBubblesFilename+"'\r\n")
# #sys.stdout.write("Content-Transfer-Encoding: binary\r\n")
# sys.stdout.write("Content-Length: "+str(fileSize)+"\r\n")
# sys.stdout.write("\r\n")
# 
# with open(dataDir+assignmentBubblesFilename,"rb") as f:
#     shutil.copyfileobj(f, sys.stdout)

sys.stdout.write("Content-Type: text/html")
sys.stdout.write("\r\n")
sys.stdout.write("\r\n")
sys.stdout.write(assignmentBubblesFilename+"\n")
sys.stdout.write(str(pagesInPdf)+"\n")



