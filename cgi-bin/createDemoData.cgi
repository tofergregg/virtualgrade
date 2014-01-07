#!python2.7virt/venv/bin/python

import createAssignmentPage
import addBubblesToPDF
from subprocess import call

dataDir = "../data/"

department = 'COMP'
classNum = 15
assignment = 5
pagesPerAssignment = 8

userNames = ['aaly01','akapla05','akasem01','akim14','bdebut01',
'blewin01','cblum02','dgarfi01','dherna01','epeter09',
'jdesto01','kcrowe01','koleso01','mshah08','mtran01',
'ntelke01','nthoms01','rwb','sbutze01','sclela01']

for i,username in enumerate(userNames):
    print "processing %s" % username
    createAssignmentPage.bubblePageUpdate(department,int(classNum),int(assignment),username,int(pagesPerAssignment))
    # convert the new png to pdf for the merge
    call(["convert", "-density", "588", dataDir+"bubbleOverlay.png", dataDir+"bubbleOverlay.pdf"])
    
    assignmentFilename = 'demoScans/examScan'+str(i)+'.pdf'
    assignmentBubblesFilename = 'demoScans/examScan_bub'+str(i)+'.pdf'
    addBubblesToPDF.mergePDFs(assignmentFilename,assignmentBubblesFilename)