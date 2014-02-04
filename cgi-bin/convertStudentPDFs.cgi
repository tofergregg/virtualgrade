#!python2.7virt/venv/bin/python

import cgi,sys,os
import errno
import cgitb
import subprocess
import uuid
import threading
import Queue
import re

cgitb.enable()
dataDir = "../data/"
logDir = "log/"
classesDir = "classes/"
semester = "2014-spring"

def convertPdfToPng(pdfFile,pngFile): # pageNum is 0-based
    subprocess.call(["convert", "-density", "200", 
                         "-depth", "8", 
                         "-quality", "85",
                         pdfFile, 
                         pngFile])

def convertAndRenamePage(th,pdfFolder,pdf,page,studentDir,pagesPerAssignment):
    convertPdfToPng(pdfFolder+pdf+'['+str(page)+']',studentDir+'page.png',page)
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

def processStudent(th,student,pdfList,assignmentDir,q):
    # place all PDFs for student into student folder,
    # numbered page1.png, page2.png, etc.
    
    # create student directory (don't fail if it exists already)
    try:
        os.makedirs(assignmentDir+student)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(assignmentDir+student):
            pass
        else: raise
        
    # create assignment dir, student dir, metadata dir, and lockfiles dir if it doesn't exist
    metadataDir = assignmentDir+student+'/metadata/'
    
    try:
        os.makedirs(metadataDir+'lockfiles/')
    except OSError:
        pass # we don't care if this fails; it may be already created
    
    # put a 'numpages.txt' file in metadata
    with open(metadataDir+'numpages.txt',"w") as f:
        f.write(str(0)+'\n') # 0 pages means that the pagecount isn't standard
    
    pageNumber = 1
    for pdf in pdfList:
        # count pages in PDF
        output = subprocess.check_output(["identify",pdfFolder+student+'/'+pdf])
        lastLine = output.split('\n')[-2]
        if '[' in lastLine: # the last page number (not present for PDFs with one page)
            pagesInPdf = int(lastLine.split('[')[1].split(']')[0])+1
        else:
            pagesInPdf = 1
        
        # extract all pages from PDF and number starting at 1
        for i in range(pagesInPdf):
            convertPdfToPng(pdfFolder+student+'/'+pdf+'['+str(i)+']',
                            assignmentDir+student+'/'+'page'+str(pageNumber)+'.png')
            q.put("\tConverting page %d from file %s for student %s." % (i+1,pdf,student))
            pageNumber+=1

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

def sortBySuffix(listToSort):
    # takes a list of files with extensions ".#" where number is any number 
    # returns a list of files sorted by that number, ascending
    partialList = []
    for value in listToSort:
        suffix = value.split('.')[-1]
        partialList.append((value,suffix))
    partialList = sorted(partialList, key = lambda bothValues: bothValues[1])
    partialList = [x[0] for x in partialList]
    return partialList

if __name__ == "__main__":
    sys.stdout.write("Content-Type: text/plain")
    sys.stdout.write("\n")
    sys.stdout.write("\n")
    sys.stdout.write("starting conversion.\n")
    sys.stdout.flush()
    form = cgi.FieldStorage()
    print form.keys()
    try:
        # assignmentDir should be in the form: 2014-spring/COMP/15/assignment_12/
        assignmentDir = dataDir+classesDir+form['assignmentDir'].value
        # pdfFolder should have the form: /g/comp/15/hw1/
        pdfFolder = form['pdfFolder'].value
        convertId = form['guid'].value
    except:
        pdfFolder = "/g/170/2014s/grading/hw1/"
        convertId = 'abcdef' 
        assignmentDir = dataDir+classesDir+'2014-spring/COMP/170/assignment_15/' 

    print pdfFolder
    print convertId
    # pagesPerAssignment = 8 # will read these from first page!
    # department = "COMP"
    # classNum = 15
    # assignmentNum = 1

    # convert the scans to png files (one file per page)
    # possibly change density to 300... (takes longer)

    # get list of student folders
    studentFoldersTemp = os.listdir(pdfFolder)
    #print studentFoldersTemp
    #studentFoldersTemp.reverse()
    # remove files/folders that do not end with ".number"
    studentFoldersTemp = [x for x in studentFoldersTemp if filter(lambda x: x.isdigit(),x.split('.')[-1]) != ""]

    studentFolders = []
    for f in studentFoldersTemp:
        filePrefix = f.split('.')[0]
        fileSuffix = filter(lambda x: x.isdigit(),f.split('.')[-1])
        thisStudentFolders = sortBySuffix([x for x in studentFoldersTemp if re.match('^'+filePrefix+'\..*',x)])
        if not thisStudentFolders[-1] in studentFolders:
                studentFolders.append(thisStudentFolders[-1])        
                
    # find PDF files in student folders
    studentDict = {}
    
    for student in studentFolders:
        pdfFiles = []
        for filename in os.listdir(pdfFolder+student):
            if filename.endswith(".pdf"):
                pdfFiles.append(filename)
        studentDict[student]=pdfFiles
        #print studentDict[student]

    
    # set up queue for status updates
    q = Queue.Queue()
    fileWriteThread = FuncThread(writeQueueToFile,q,convertId+'.log')
    fileWriteThread.start()

    threads=[]
    for student in studentDict:
        th = FuncThread(processStudent,student,studentDict[student],assignmentDir,q)
        th.start()
        threads.append(th)

    for th in threads:
        th.join()
    fileWriteThread.stop()
    q.put("Finished.")
    fileWriteThread.join()
