#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
import subprocess
import uuid
import threading
import Queue
import traceback
from PIL import Image
import zbarlight
import re
import json

cgitb.enable()
dataDir = "../data/"
logDir = "log/"
tempPngsDir = "tempPngs/"
classesDir = "classes/"
semester = "2016-spring"

def convertPdfToPng(pdfFile,pngFile,pageNum): # pageNum is 0-based
    subprocess.call(["convert", "-density", "200", 
                         "-depth", "8", 
                         "-quality", "85",
                         pdfFile, 
                         pngFile[:-4]+'-'+str(pageNum)+'.png'])

def processPdf(pdf,q,outputFilename):
    global semester
    output = subprocess.check_output(["identify",pdfFolder+"/"+pdf])
    print output
    lastLine = output.split('\n')[-2]
    if '[' in lastLine:
        pagesInPdf = int(lastLine.split('[')[1].split(']')[0])+1
    else:
        pagesInPdf = 1
    workingPage = 0 # first page

    orphanId = None
    maxPagesPerStudent = 100 # don't know this yet, so start really high
    sem = None # we may need this for an initial orphan
    while workingPage < pagesInPdf:
        print "Working on page "+str(workingPage)
            	
        tempName=dataDir+tempPngsDir+str(uuid.uuid4())+'.png'

        convertPdfToPng(pdfFolder+"/"+pdf+'['+str(workingPage)+']',tempName,workingPage)
        tempName = tempName[:-4]+'-'+str(workingPage)+'.png' # convert puts the '-0' on automatically
        with open(tempName, 'rb') as image_file:
            image = Image.open(image_file)
            image.load()

        codes = zbarlight.scan_codes('qrcode', image)
        if codes:
                codes = json.loads(codes[0]) # only one QR per page
                q.put("Found "+str(codes))
                print codes
                # e.g.:
                # Found ['["agrubb01", "Akil", "Grubb", "S2016", "COMP11", 1, 12]']

                uid = codes[0]
                
                # skip codes[1] and codes[2] (student name)
                
                sem = codes[3][0]
                if sem == "S": sem = "spring"
                elif sem == "F": sem = "fall"
                year = codes[3][1:]
                semester = year+"-"+sem
                
                full_course = codes[4]
                m = re.search("\d", full_course)
                deptName = full_course[:m.start()]
                course = full_course[m.start():]
                
                assignmentNum = str(codes[5])
                page = codes[6]
                if maxPagesPerStudent < page or maxPagesPerStudent == 100:
                        maxPagesPerStudent = page
                orphanId = None # remove orphanId if necessary
                
        else:
                q.put("Could not decode QR code on page %d in file %s" % (workingPage+1,pdf))
                # we need to make some decisions here about where to put this page
                if (not orphanId) or (page > maxPagesPerStudent):
                        # if we don't already have recent orphaned pages,
                        # or if we've had too many orphaned pages in a row,
                        # create a new uid
                        orphanId = uid = str(uuid.uuid4()) # punt on userId
                        page = 1
                else:
                        # probably belongs with the last orphan
                        uid = orphanId
                        page += 1
                q.put("\tid will be: "+uid)
                
                # hopefully this isn't the first pages, and we already have
                # some information about the most recent assignment
                if not sem: # darn, we have to really orphan this one
                        # we already have a semester (defined at top of file)
                        q.put("This is really an orphan, and will be in the 'Orphaned' department")
                        deptName = 'Orphaned'
                        course = 'Unknown'
                        assignmentNum = '1'
                
        # create assignment dir, student dir, metadata dir, and lockfiles dir if it doesn't exist
        assignmentDir = dataDir+classesDir+semester+"/"+deptName+"/"+course+"/"+'assignment_'+assignmentNum+'/'
        print assignmentDir
        metadataDir = assignmentDir+uid+'/metadata/'
        
        try:
            os.makedirs(metadataDir+'lockfiles/')
        except OSError:
            print "failed making "+metadataDir+'lockfiles/'
            #pass # we don't care if this fails; it may be already created
        
        # put a 'numpages.txt' file in metadata
        with open(metadataDir+'numpages.txt',"w") as f:
            f.write(str(page)+'\n')
        
        # move first page into the folder, and rename "page1.png"
        studentDir = assignmentDir+uid+'/'
        os.rename(tempName,studentDir+'page'+str(page)+'.png')
        writeQueueToFile(q,outputFilename)
        workingPage+=1


def writeQueueToFile(q,fileName):
    # sequentially writes queue items to a file
    print dataDir+logDir+fileName
    with open(dataDir+logDir+fileName,"a") as f: # unbuffered
        while not q.empty():
            output = q.get()
            f.write(output+'\n')
            f.flush()
            os.fsync(f) # ensure flushing?
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
        remoteUser = form['remoteUser'].value
        
    except:
    	print "Using default fields"
        convertId = 'testId'
        remoteUser = 'nobody'
        pdfFolder = '/h/cgregg/testExam'

    print convertId
    print remoteUser

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
        processPdf(pdf,q,convertId+'.log')
        #th.start()
        #threads.append(th)

    #for th in threads:
    #    th.join()

    #fileWriteThread.stop()
    q.put("Finished.")
    writeQueueToFile(q,convertId+'.log')
    #fileWriteThread.join()
