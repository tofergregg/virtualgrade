#!python2.7virt/venv/bin/python

import cgi,sys,os
import errno
import cgitb
import subprocess
import uuid
import threading
import Queue
import re
import shutil

cgitb.enable()
dataDir = "../data/"
logDir = "log/"
classesDir = "classes/"
semester = "2015-spring"

def convertPdfToPng(pdfFile,pngFile): # pageNum is 0-based
    subprocess.call(["convert", "-density", "200", 
                         "-depth", "8", 
                         "-quality", "90",
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

def processStudent(student,studentIdOnly,pdfList,assignmentDir,q,qFileName):
    # place all PDFs for student into student folder,
    # numbered page1.png, page2.png, etc.
    
    for pdf in pdfList:
        pageNumber = 1
        # create student directory (don't fail if it exists already)
        # the directory should be based on the PDF name
        #fullAssignmentDir = assignmentDir[:-1]+pdf.split('.')[0]+'/'
        fullAssignmentDir = assignmentDir

        try:
            os.makedirs(fullAssignmentDir+studentIdOnly)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(fullAssignmentDir+studentIdOnly):
                pass
            else: raise
        
        # create assignment dir, student dir, metadata dir, and lockfiles dir if it doesn't exist
        metadataDir = fullAssignmentDir+studentIdOnly+'/metadata/'
    
        try:
            os.makedirs(metadataDir+'lockfiles/')
        except OSError:
            pass # we don't care if this fails; it may be already created
    
        # put a 'numpages.txt' file in metadata
        with open(metadataDir+'numpages.txt',"w") as f:
            f.write(str(0)+'\n') # 0 pages means that the pagecount isn't standard

        # count pages in PDF
        try:
                output = subprocess.check_output(["identify",pdfFolder+student+'/'+pdf])
        except:
                # could not process PDF
                print "Could not process PDF! "+pdfFolder+student+'/'+pdf
                continue
        lastLine = output.split('\n')[-2]
        if '[' in lastLine: # the last page number (not present for PDFs with one page)
            pagesInPdf = int(lastLine.split('[')[1].split(']')[0])+1
        else:
            pagesInPdf = 1
        
        # extract all pages from PDF and number starting at 1 #####
        for i in range(pagesInPdf):
            convertPdfToPng(pdfFolder+student+'/'+pdf+'['+str(i)+']',
                            fullAssignmentDir+studentIdOnly+'/'+'page'+str(pageNumber)+'.png')
            q.put("\tConverting page %d from file %s for student %s." % (i+1,pdf,studentIdOnly))
            writeQueueToFile(q,qFileName)
            pageNumber+=1

def writeQueueToFile(q,fileName):
    # sequentially writes queue items to a file
    with open(dataDir+logDir+fileName,"a") as f: # unbuffered, append
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
        # assignmentDir should be in the form: 2015-spring/COMP/15/assignment_12/
        assignmentDir = dataDir+classesDir+form['assignmentDir'].value
        # pdfFolder should have the form: /g/comp/15/hw1/
        pdfFolder = form['pdfFolder'].value
        convertId = form['guid'].value
    except:
        pdfFolder = "/g/170/2015s/grading/hw1p1/"
        convertId = 'abcdef' 
        assignmentDir = dataDir+classesDir+'2015-spring/COMP/170/assignment_1/' 

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
    
    studentFilesSet = set()
    
    for student in studentFolders:
        pdfFiles = []
        for filename in os.listdir(pdfFolder+student):
            if filename.endswith(".pdf"):
                pdfFiles.append(filename)
                studentFilesSet.add(filename.split('.')[0])
        studentDict[student]=pdfFiles
        #print studentDict[student]    

    print studentFilesSet
    # create subfolders for each assignment
    for assignment in studentFilesSet:
        # create subfolder
        subAssignmentDir = assignmentDir[:-1]+assignment+"/"
        try:
                os.makedirs(subAssignmentDir)
        except OSError:
                pass # we don't care if this fails; it may be already created
        # copy metadata from original assignment
        try:
                shutil.copytree(assignmentDir+"/metadata/", subAssignmentDir+"/metadata/")
        except OSError:
                pass # again, we don't really care if this fails as it may already be created
    
    # set up queue for status updates
    q = Queue.Queue()
    #fileWriteThread = FuncThread(writeQueueToFile,q,convertId+'.log')
    #fileWriteThread.start()

    #threads=[]
        
    for student in studentDict:
        # strip off characters after the period in the name
        studentIdOnly = student.split('.')[0]
        processStudent(student,studentIdOnly,studentDict[student],assignmentDir,q,convertId+'.log')
        #th = FuncThread(processStudent,student,studentDict[student],assignmentDir,q)
        #th.start()
        #threads.append(th)
        

    #for th in threads:
    #    th.join()
    #fileWriteThread.stop()
    q.put("Finished.")
    #fileWriteThread.join()
