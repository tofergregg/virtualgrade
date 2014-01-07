#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb

dataDir = "../data/"
classesDir = "classes/"
logDir = "log/"

cgitb.enable()

sys.stdout.write("Content-Type: text/html")
sys.stdout.write("\n")
sys.stdout.write("\n")

form = cgi.FieldStorage()

# studentDir should be in the form
# 'semester/department/course/assignment/studentId/
studentDir = form['studentDir'].value

# pageName should be in the form: pageX_graded.png'
pageName = form['pageName'].value

imageData = form['imgBase64'].value.split(',',1)[1]
with open(dataDir+classesDir+studentDir+pageName, "wb") as f:
    f.write(imageData.decode('base64'))
    
sys.stdout.write("Content-Type: text/html")
sys.stdout.write("\r\n")
sys.stdout.write("\r\n")
print ("Saved image!")
