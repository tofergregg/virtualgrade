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

def addToAllGrades(gradeDirectory):
        gradesLocked = True
        count = 0
        # see if grade file is locked
        while gradesLocked and count < 5:
                if (not os.path.isfile(gradesDir+"allGrades.lck")):
                        gradesLocked = False
                else:
                        print "sleeping"
                        time.sleep(1) # wait a second for the grades to become unlocked
                        count+=1
        
        if count==5:
                print "Grade file was locked."
                quit()
        
        # if grade file is unlocked, lock it and update
        touch(gradesDir+"allGrades.lck")
        
        # update the grades file
        with open(gradesDir+"allGrades.txt","r") as f:
                oldAssignmentDataList = json.loads(f.read())
        
        # get a list of all graded exams in assignment folder
        # traverse assignment directory, and list directories as dirs and files as files
        dirStructure = []
        for root, dirs, files in os.walk(gradeDirectory):
        
                #dirStructure.append(root+'/'+remoteUser)
                for dir in dirs:
                        if dir=='metadata': continue
                        if dir=='lockfiles': continue
                        # check for first page graded (meaning that the grade exists)
                        gradedPage1 = root+'/'+dir+'/metadata/'+'page1_totalGrade.png'
                        if os.path.isfile(gradedPage1):
                                dirStructure.append(root+dir)
        
        assignmentDataList = getAssignmentList(dirStructure)
        
        # check each name against elements in list, and replace if necessary
        for newGrade in assignmentDataList:
                for idx,oldGrade in enumerate(oldAssignmentDataList):
                        if newGrade['student'] == oldGrade['student']:
                                if newGrade['assignment'] == oldGrade['assignment']:
                                        if newGrade['class'] == oldGrade['class']:
                                                if newGrade['department'] == oldGrade['department']:
                                                        if newGrade['semester'] == oldGrade['semester']:
                                                                if 'totalPoints' in oldGrade:
                                                                        oldAssignmentDataList[idx]=newGrade
        # save the updated list to the file
        with open(gradesDir+'allGrades.txt', 'w') as outfile:
                json.dump(oldAssignmentDataList, outfile)

        # unlock grade file
        os.remove(gradesDir+"allGrades.lck")

def getAssignmentList(dirStructure):
        assignmentDataList = []

        for assignment in dirStructure:
                assignmentData = {}
                fullMetadataDir = '/'.join(assignment.split('/')[:-1])+'/metadata/'
                if os.path.exists(fullMetadataDir+'published'):
                        # grades have been published
                        try:
                                with open(fullMetadataDir+'assignmentName.txt','r') as f:
                                        assignmentData['assignmentName']=f.readline()[:-1]
                        except IOError:
                                assignmentData['assignmentName']=''
                        assignment = assignment.replace('//','/')
                        assignmentParts = assignment.split('/')

                        assignmentData['semester']=assignmentParts[3]
                        assignmentData['department']=assignmentParts[4]
                        assignmentData['class']=assignmentParts[5]
                        assignmentData['assignment']=assignmentParts[6].split('_')[-1]
                        assignmentData['student']=assignmentParts[7]
                
                        gradeFiles = os.listdir(assignment+'/metadata/')
                        studentScore = 0
                        totalPoints = 0
                        for gradeFile in gradeFiles:
                                if '.grd' in gradeFile:
                                        with open(assignment+'/metadata/'+gradeFile,"r") as f:
                                                line = f.readline()[:-1].split(',')
                                                studentScore+=float(line[0])
                                                totalPoints+=float(line[4])
                                        assignmentData['score']=studentScore
                                        assignmentData['totalPoints']=totalPoints
                        assignmentDataList.append(assignmentData)
        return assignmentDataList


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

unpublished = False
published = False

now = time.strftime("%c")

if unpublish == "Yes":
        try:
                os.remove(dataDir+classesDir+'/'+courseLocation+'metadata/published')
                unpublished = True
                with open(dataDir+logDir+'virtualgrade.log','a') as f:
		    f.write('unpublished,'+remoteUser+','+
			    now+','+
			    courseLocation+'\n')
        except OSError:
                unpublished = False
        
else:
        try:
                with open(dataDir+classesDir+courseLocation+'metadata/published',"w"):
                        published = True
                        with open(dataDir+logDir+'virtualgrade.log','a') as f:
		                f.write('published,'+remoteUser+','+
			        now+','+
			        courseLocation+'\n')
		addToAllGrades(dataDir+classesDir+'/'+courseLocation)
		published = True
	except IOError:
	        published = False
	        print "Error in file:",dataDir+classesDir+courseLocation+'metadata/published'
        
if unpublish == "Yes":
        if unpublished:
		sys.stdout.write("Unpublished grades for course: "+courseLocation+".");
	else:
		sys.stdout.write("Could not unpublish grades for course: "+courseLocation+".");
		
else:
	if published:
		sys.stdout.write("Published grades for course: "+courseLocation+".");
	else:
		sys.stdout.write("Could not publish grades for course: "+courseLocation+".");


