#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
import json

cgitb.enable()
dataDir = "../data/"
classesDir = "classes/"
semester = "2014-fall"
metaDataDir = "metadata/"

sys.stdout.write("Content-Type: text/html")
sys.stdout.write("\r\n")
sys.stdout.write("\r\n")

form = cgi.FieldStorage()
formData = json.loads(form['data'].value)
deptName = formData['department']
course = formData['classNum']
assignmentNum = formData['assignmentNum']
assignmentName = formData['assignmentName']
if assignmentName == '':
    assignmentName = 'assignment'

# create assignment folder and metadata folder if they don't exist
assignmentDir = dataDir+classesDir+semester+'/'+deptName+'/'+str(course)+'/'+'assignment_'+str(assignmentNum)+'/'
try:
    os.makedirs(assignmentDir+metaDataDir)
except OSError:
    pass # we don't care if this fails; it may be already created

# permissions might not be set correctly, so set them to 0770...TODO:fix this hack...
#os.chmod(dataDir+classesDir+semester+'/',0770)
#os.chmod(dataDir+classesDir+semester+'/'+deptName+'/',0770)
#os.chmod(dataDir+classesDir+semester+'/'+deptName+'/'+str(course)+'/',0770)
#os.chmod(assignmentDir,0770)
#os.chmod(assignmentDir+metaDataDir,0770)
    
# save a file called 'point_values.csv' in the new folder
with open(assignmentDir+metaDataDir+'point_values.csv',"w") as f:
    for i,pointValue in enumerate(formData['pagePoints']):
        if i<len(formData['pagePoints'])-1:
            f.write(pointValue+',')
        else:
            f.write(pointValue+"\n")

# save a file called "assignmentName.txt" with the name of the assignment
with open(assignmentDir+metaDataDir+'assignmentName.txt','w') as f:
    f.write(assignmentName+'\n')

sys.stdout.write("points saved.\n")
print assignmentDir
#sys.stdout.write(str(json.loads(form['data'].value))+"\n")



