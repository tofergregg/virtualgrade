#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
import subprocess
import uuid
import omrImage
import threading
import Queue

cgitb.enable()
dataDir = "../data/"
logDir = "log/"
classesDir = "classes/"
semester = "2014-spring"

def convertPdfToPng(pdfFile,pngFile,pageNum): # pageNum is 0-based
    subprocess.call(["convert", "-density", "200", 
                         "-depth", "8", 
                         "-quality", "85",
                         pdfFile, 
                         pngFile[:-4]+'-'+str(pageNum)+'.png'])

def convertAndRenamePage(th,pdfFolder,pdf,page,studentDir,pagesPerAssignment):
    convertPdfToPng(pdfFolder+"/"+pdf+'['+str(page)+']',studentDir+'page.png',page)
    # need to rename because convert added a number
    os.rename(studentDir+'page-'+str(page)+'.png',studentDir+'page'+str((page%pagesPerAssignment)+1)+'.png')

class FuncThread(threading.Thread):
    def __init__(self, target, *args):
        super(FuncThread, self).__init__()
        self._stop = threading.Event()
        
        self._target = target
        self._args = args
        threading.Thread.__init__(self)
 
    def run(self):
        self._target(self, *self._args)

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

def processPdf(th,pdf,q):
    output = subprocess.check_output(["identify",pdfFolder+"/"+pdf])
    lastLine = output.split('\n')[-2]
    if '[' in lastLine:
        pagesInPdf = int(lastLine.split('[')[1].split(']')[0])+1
    else:
        pagesInPdf = 1
    
    workingPage = 0 # first page
    while workingPage < pagesInPdf-1:
        # OMR first page, which should have bubbles
        # output png into data folder with a temporary name, will move once we determine the studentID
        tempName=dataDir+str(uuid.uuid4())+'.png'

        convertPdfToPng(pdfFolder+"/"+pdf+'['+str(workingPage)+']',tempName,workingPage)
        tempName = tempName[:-4]+'-'+str(workingPage)+'.png' # convert puts the '-0' on automatically

        bl_x,bl_y,bl_w,bubbleData = omrImage.findBlackLine(tempName)
        dept,course,assignmentNum,id,pagesPerAssignment = omrImage.findBubbles(bl_x,bl_y,bl_w,bubbleData)
        # now we have the data we need to create the file structure for the student scans
        deptName = omrImage.getDeptName(dept)
        # student ID may have trailing underscores if len(id)<8
        id = id.rstrip('_')
        
        q.put('Found first page for student %s, Course: %s, Assignment: %d, Number of Pages in assignment:%d' % (id, deptName+str(course),assignmentNum,pagesPerAssignment))
        
        # create assignment dir, student dir, metadata dir, and lockfiles dir if it doesn't exist
        assignmentDir = dataDir+classesDir+semester+'/'+deptName+'/'+str(course)+'/'+'assignment_'+str(assignmentNum)+'/'
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
            # more parallelism
            th = FuncThread(convertAndRenamePage,pdfFolder,pdf,page,studentDir,pagesPerAssignment)
            th.start()
            threads.append(th)
        for th in threads:
            th.join()
            
        workingPage+=pagesPerAssignment

def writeQueueToFile(th,q,fileName):
    # sequentially writes queue items to a file
    with open(dataDir+logDir+fileName,"w") as f: # unbuffered
        while(not th.stopped()):
            output = q.get()
            f.write(output+'\n')
            f.flush()
            sys.stdout.write(output+'\n')
            sys.stdout.flush()
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
    except:
        pdfFolder = '/h/cgregg/testExam'
        convertId = 'testId'
    #convertId = 'abcdef'
    #pdfFolder = "../data/demoScans"

    print pdfFolder
    print convertId

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
    #print pdfFiles

    # set up queue for status updates
    q = Queue.Queue()
    fileWriteThread = FuncThread(writeQueueToFile,q,convertId+'.log')
    fileWriteThread.start()

    threads=[]
    for pdf in pdfFiles:
        #processPdf(pdf)
        th = FuncThread(processPdf,pdf,q)
        th.start()
        threads.append(th)

    for th in threads:
        th.join()
    fileWriteThread.stop()
    q.put("Finished.")
    fileWriteThread.join()
