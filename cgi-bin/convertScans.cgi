#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
import subprocess
import uuid
import omrImage
import threading
import Queue
import traceback

cgitb.enable()
dataDir = "../data/"
logDir = "log/"
tempPngsDir = "tempPngs/"
classesDir = "classes/"
semester = "2015-spring"

def convertPdfToPng(pdfFile,pngFile,pageNum): # pageNum is 0-based
    subprocess.call(["convert", "-density", "200", 
                         "-depth", "8", 
                         "-quality", "85",
                         pdfFile, 
                         pngFile[:-4]+'-'+str(pageNum)+'.png'])

def convertAndRenamePage(pdfFolder,pdf,page,studentDir,pagesPerAssignment):
    convertPdfToPng(pdfFolder+"/"+pdf+'['+str(page)+']',studentDir+'page.png',page)
    # need to rename because convert added a number
    os.rename(studentDir+'page-'+str(page)+'.png',studentDir+'page'+str((page%pagesPerAssignment)+1)+'.png')

def processPdf(pdf,q,assignmentDir,pagesPerAssignment,outputFilename,darkScans):
    output = subprocess.check_output(["identify",pdfFolder+"/"+pdf])
    print output
    lastLine = output.split('\n')[-2]
    if '[' in lastLine:
        pagesInPdf = int(lastLine.split('[')[1].split(']')[0])+1
    else:
        pagesInPdf = 1
    workingPage = 0 # first page
    while workingPage < pagesInPdf-1:
        print "Working on page "+str(workingPage)
    	foundName = False # we don't have a name yet
        # OMR first page, which should have bubbles
        # output png into data folder with a temporary name, will move once we determine the studentID
        tempName=dataDir+tempPngsDir+str(uuid.uuid4())+'.png'

        convertPdfToPng(pdfFolder+"/"+pdf+'['+str(workingPage)+']',tempName,workingPage)
        tempName = tempName[:-4]+'-'+str(workingPage)+'.png' # convert puts the '-0' on automatically

        #bl_x,bl_y,bl_w,bubbleData = omrImage.findBlackLine(tempName)
        boxX,boxY,boxW,bubbleData = omrImage.findBlackBox(tempName)
        if bubbleData == None:
                print "didn't find black box"
                print "Could not find bubbles! File: "+pdf+" Page: "+str(workingPage+1)
                q.put("Could not find bubbles! File: "+pdf+" Page: "+str(workingPage+1))
                writeQueueToFile(q,outputFilename)
                #workingPage+=1
                #continue
        
        #dept,course,assignmentNum,id,pagesPerAssignment = omrImage.findBubbles(bl_x,bl_y,bl_w,bubbleData)
        else:
        	try:
        	        print "finding bubbles"
                	dept,course,assignmentNum,id,pagesPerAssignmentDummy = omrImage.findBubbles(boxX,boxY,boxW,bubbleData,darkScans)
        	except:
        	        print traceback.format_exc()
			# could not find bubbles!
			print "Could not find bubbles! File: "+pdf+" Page: "+str(workingPage+1)
			q.put("Could not find bubbles! File: "+pdf+" Page: "+str(workingPage+1))
			writeQueueToFile(q,outputFilename)
			dept = 0
			id = ''
			#workingPage+=1
			#continue
        # now we have the data we need to create the file structure for the student scans
        deptName = omrImage.getDeptName(dept)
        # student ID may have trailing underscores if len(id)<8
        id = id.rstrip('_')
        if pagesPerAssignment == 0 or deptName != "COMP" or id == "" or (not id[0].isalpha()):
                # can't process
                id = str(uuid.uuid4()) # punt on userId
                print ("Could not find bubbles! File: "+pdf+" Page: "+str(workingPage+1)+
                	"\nTemp name will be: "+id)
                q.put("Could not find bubbles! File: "+pdf+" Page: "+str(workingPage+1)+
                	"\nTemp name will be: "+id)
                writeQueueToFile(q,outputFilename)
                
                #workingPage+=1
                #continue
        else: 
        	print 'Found first page for student %s, Course: %s, Assignment: %d, Number of Pages in assignment:%d' % (id, deptName+str(course),assignmentNum,pagesPerAssignment)
        	q.put('Found first page for student %s, Course: %s, Assignment: %d, Number of Pages in assignment:%d' % (id, deptName+str(course),assignmentNum,pagesPerAssignment))
                writeQueueToFile(q,outputFilename)

        # create assignment dir, student dir, metadata dir, and lockfiles dir if it doesn't exist
        #assignmentDir = dataDir+classesDir+semester+'/'+deptName+'/'+str(course)+'/'+'assignment_'+str(assignmentNum)+'/'
        metadataDir = assignmentDir+id+'/metadata/'
        
        try:
            os.makedirs(metadataDir+'lockfiles/')
        except OSError:
            pass # we don't care if this fails; it may be already created
        
        # put a 'numpages.txt' file in metadata
        with open(metadataDir+'numpages.txt',"w") as f:
            f.write(str(pagesPerAssignment)+'\n')
        
        # move first page into the folder, and rename "page1.png"
        studentDir = assignmentDir+id+'/'
        os.rename(tempName,studentDir+'page1.png')
        
        # create the remaining pages in the proper folder
        threads = []
        for page in range(workingPage+1,workingPage+pagesPerAssignment):
            q.put("\tConverting page %d for student %s." % ((page%pagesPerAssignment)+1,id))
            writeQueueToFile(q,outputFilename)
            convertAndRenamePage(pdfFolder,pdf,page,studentDir,pagesPerAssignment)
            # more parallelism
            #th = FuncThread(convertAndRenamePage,pdfFolder,pdf,page,studentDir,pagesPerAssignment)
            #th.start()
            #threads.append(th)
        #for th in threads:
            #th.join()
            
        workingPage+=pagesPerAssignment

def writeQueueToFile(q,fileName):
    # sequentially writes queue items to a file
    with open(dataDir+logDir+fileName,"a") as f: # unbuffered
        while not q.empty():
            output = q.get()
            f.write(output+'\n')
            f.flush()
            sys.stdout.write(output+'\n')
            sys.stdout.flush()

if __name__ == "__main__":
    sys.stdout.write("Content-Type: text/plain")
    sys.stdout.write("\n")
    sys.stdout.write("\n")
    sys.stdout.write("starting scans.\n")
    sys.stdout.flush()

    try:
        form = cgi.FieldStorage()
        pdfFolder = form['pdfFolder'].value
        convertId = form['guid'].value
        semester = form['semester'].value
        department = form['department'].value
        course = form['course'].value
        assignment = form['assignment'].value
        pagesPerStudent = int(form['pagesPerStudent'].value)
        remoteUser = form['remoteUser'].value
        darkScans = form['darkScans'].value
        if darkScans == 'True':
                darkScans = True
        else:
                darkScans = False
        
    except:
    	print "Using default fields"
        pdfFolder = '/h/cgregg/testExam'
        convertId = 'testId'
        semester = '2015-spring'
        department = 'COMP'
        course = '11'
        assignment = 'assignment_3'
        pagesPerStudent = 8
        remoteUser = 'nobody'
        darkScans = False
        
    assignmentDir = dataDir+classesDir+semester+'/'+department+'/'+course+'/'+assignment+'/'
        
    #convertId = 'abcdef'
    #pdfFolder = "../data/demoScans"

    print pdfFolder
    print convertId
    print assignmentDir,pagesPerStudent,remoteUser

    # pagesPerAssignment = 8 # will read these from first page!
    # department = "COMP"
    # classNum = 15
    # assignmentNum = 1

    # convert the scans to png files (one file per page)
    # possibly change density to 300... (takes longer)

    # find PDF files in folder

    pdfFiles = []
    for filename in os.listdir(pdfFolder):
        if filename.endswith(".pdf"):
            pdfFiles.append(filename)

    # set up queue for status updates
    q = Queue.Queue()
    #fileWriteThread = FuncThread(writeQueueToFile,q,convertId+'.log')
    #fileWriteThread.start()

    threads=[]

    print pdfFiles

    for pdf in pdfFiles:
        #th = FuncThread(processPdf,pdf,q,assignmentDir,pagesPerStudent)
        processPdf(pdf,q,assignmentDir,pagesPerStudent,convertId+'.log',darkScans)
        #th.start()
        #threads.append(th)

    #for th in threads:
    #    th.join()

    #fileWriteThread.stop()
    q.put("Finished.")
    writeQueueToFile(q,convertId+'.log')
    #fileWriteThread.join()
