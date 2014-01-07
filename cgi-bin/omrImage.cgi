#!python2.7virt/venv/bin/python

from scipy import ndimage
import numpy as np
#import matplotlib.pyplot as plt
from PIL import Image, ImageDraw
import sys,Queue,os
import math

dataDir = "../data/"

def imageToArray(imageBW):
    pixels = imageBW.getdata() # returns 1D list of pixels
    n = len(pixels)
    imSize=imageBW.size[::-1]
    bubbleDataOrig = np.reshape(pixels, imSize) # turn into 2D numpy array
    return bubbleDataOrig
    
def arrayToImage(data):
    h,w = data.shape
    bubbleImage = Image.new("1", (w,h))
    bubbleImage.putdata(np.reshape(data, [w*h, 1]))
    return bubbleImage
    
def bubbleFilled(data,x,y,dia,thresh=0.9):
    rad = dia/2.0-4
    area = math.pi * rad * rad
    
    x = int(x)
    y = int(y)
    dia = int(dia)
    bubbleSum = 0 # bubbleSum==0 is perfectly black
    for i in range(dia):
        for j in range(dia):
            distFromCenter = math.sqrt((i-rad)*(i-rad)+(j-rad)*(j-rad))
            if distFromCenter < rad:
                bubbleSum+=data[y+i][x+j]
    bubbleSum/=255.0
    bubblePerc = 1-(bubbleSum / area)
    #if bubblePerc > thresh-0.1: print "%0.2f" % bubblePerc
    if bubblePerc > thresh:
        return True
    else:
        return False

def findBlackLine(imageName):
    PAGE_CROP = 0.35 # bottom 35%
    #PERC_BLACK_THRESH = 0.68 # to find the black line denoting our bubbles

    image0 = Image.open(imageName)
    # crop to bottom 30%
    w,h = image0.size
    image0 = image0.crop((int(0.05*w),int(h-PAGE_CROP*h),int(0.95*w),h))
    imageBW = image0.convert('1',dither=0)
    w,h = imageBW.size

    bubbleDataOrig = imageToArray(imageBW)

    bubbleData = bubbleDataOrig.copy()
    # process bubbleData
    percentBlackLine = 0
    angle = 0
    while abs(angle) <= 5: # rotate by up to 5deg in both directions
        #print "angle:",angle
        #arrayToImage(bubbleData).show()
        
        pixCount = []
        for r,row in enumerate(bubbleData):
          pixCount.append((r,row.sum()/255))
        
        # first sort by length and take top 20
        mostBlack = sorted(pixCount,key=lambda x: x[1])[:20] 
        # next sort by line number
        mostBlack = list(sorted(mostBlack,key=lambda x: x[0]))
        
        # cut out non-contiguous rows in the top 20 and trim by one more on either end
        # We do this so we can determine if the line is straight or not
        shortestRow = mostBlack[0][0]
        mostBlack2 = [mostBlack[0]]
        for i,x in enumerate(mostBlack[1:]):
            if (x[0]-shortestRow) < 20:
                mostBlack2.append(x)
        mostBlack2 = mostBlack2[1:-1] # trim the first and last
        if len(mostBlack2) > 1:
            #print mostBlack2
            # find stdev for remaining values
            mostBlackStdev = np.std(np.array([x[1] for x in mostBlack2]))
            mostBlackAvg = np.average(np.array([x[1] for x in mostBlack2]))
            #print "Stdev:",mostBlackStdev
            #print "Avg:",mostBlackAvg
        else:
            mostBlackStdev = 1000000 # no good line

        if mostBlackStdev > 75 or mostBlackAvg > 400:
            if angle > 0:
                angle = -1 * angle
            else:
                angle = -1 * angle + 0.1
            bubbleData = ndimage.rotate(bubbleDataOrig, angle, cval=255,reshape=False,order=0)
            
            #print "Rotating through angle",angle
        else:
            break # found a good straight line
    if abs(angle) > 5:
      raise Exception("Could not find black line. Exiting.")

    #print "Topmost short line:",mostBlack2[0]

    # figure out the x-coordinate where the longest line starts
    y = mostBlack2[0][0]
    # we assume it will start immediately
    x = 0
    # in order to adjust for noise, wait until 95% of the last 20 pixels are black
    # and we will say that the first pixel in that group is the start of the line
    foundStart = False
    
    q = Queue.Queue()
    qSum = 0 # 95% black means that qSum <= 255 (only one white value)
    for i in range(20):
        q.put(255) # white
        qSum+=255
    
    # find the first black pixel and populate the queue
    #arrayToImage(bubbleData).show()
    while not foundStart and x<=0.25*w:
        x+=1
        qSum-=q.get()
        q.put(bubbleData[y][x])
        qSum += bubbleData[y][x]
        #print qSum,bubbleData[y][x],x,y
        if qSum <= 255:
            foundStart = True # the start is the first x value in the queue, or x-19
                              # may be off by one if first value is 0, so we'll say x-18
            x-=18
            
    if x > 0.25*w:
        raise Exception("Could not find bubbles (black line). Exiting.")
        
    
    xStart = x
    
    # find the end of the line so we can set the scale properly
    # start at 75% and go to 98%
    x = int(0.75*w)
    # in order to adjust for noise, wait until 95% of the last 20 pixels are white
    # and we will say that the first pixel in that group is the end of the line
    foundEnd = False
    
    q = Queue.Queue()
    qSum = 0 # 95% white means that qSum >= 255*19 >= 4845 (only one black value)
    for i in range(20):
        q.put(0) # black
    
    # find the first black pixel and populate the queue
    while not foundEnd and x<=0.98*w:
        x+=1
        qSum-=q.get()
        q.put(bubbleData[y][x])
        qSum += bubbleData[y][x]
        #print qSum,bubbleData[y][x],x,y
        if qSum >= 255*19:
            foundEnd = True # the start is the first x value in the queue, or x-19
            x-=19
            
    if x > 0.98*w:
        raise Exception("Could not find bubbles (black line 2). Exiting.")
    
    xEnd = x

    return xStart,y,(xEnd-xStart),bubbleData

def findBubbles(bl_x,bl_y,SCALE,bubbleData): 
    BUBBLE_X_OFFSET =  0.0105 * SCALE
    BUBBLE_Y_OFFSET = 0.046 * SCALE # y location ratio for first bubble
    BUBBLE_DIA = 0.022 * SCALE
    bubbleInc = 0.0271 * SCALE
    bubbleX = bl_x + BUBBLE_X_OFFSET
    bubbleY = bl_y + BUBBLE_Y_OFFSET

    #print BUBBLE_X_OFFSET,BUBBLE_Y_OFFSET,BUBBLE_DIA,bubbleX,bubbleY,bubbleInc
    #draw.ellipse((bubbleX,bl_y,bubbleX+BUBBLE_DIA,bl_y+BUBBLE_DIA),fill=0)
    #draw.line([(bubbleX,0),(bubbleX,200)],fill=0)
    #draw.line([(0,bubbleY),(500,bubbleY)],fill=0)
    #bubbleImage.show()
    bubbleImage = arrayToImage(bubbleData)
    draw = ImageDraw.Draw(bubbleImage)
    
    # Get Department Code
    bubbleVal = 0
    valCount = 8 # for the conversion from binary to decimal
    xStart = bubbleX
    yStart = bubbleY
    #print "xStart:",xStart,"yStart:",yStart
    for j in range(2):
        yVal = yStart+(j*bubbleInc)
        for i in range(4):
            valCount-=1
            xVal = xStart+(i*bubbleInc)
            #print "xval:",xVal,"yVal:",yVal,"dia:",BUBBLE_DIA
            if bubbleFilled(bubbleData,xVal,yVal,BUBBLE_DIA):
                bubbleVal+=pow(2,valCount)
            draw.line([(xVal,yVal),(xVal,yVal+BUBBLE_DIA)],fill=0)
            draw.line([(xVal,yVal),(xVal+BUBBLE_DIA,yVal)],fill=0)
            draw.line([(xVal+BUBBLE_DIA,yVal),(xVal+BUBBLE_DIA,yVal+BUBBLE_DIA)],fill=0)
            draw.line([(xVal,yVal+BUBBLE_DIA),(xVal+BUBBLE_DIA,yVal+BUBBLE_DIA)],fill=0)
    #print "Department Code:",bubbleVal
    dept = bubbleVal
    
    # Get Course Number
    bubbleVal = 0
    valCount = 12 # for the conversion from binary to decimal
    xStart = bubbleX+bubbleInc*5
    yStart = bubbleY
    for j in range(3):
        yVal = yStart+(j*bubbleInc)
        for i in range(4):
            valCount-=1
            xVal = xStart+(i*bubbleInc)
            if bubbleFilled(bubbleData,xVal,yVal,BUBBLE_DIA):
                bubbleVal+=pow(2,valCount)
            draw.line([(xVal,yVal),(xVal,yVal+BUBBLE_DIA)],fill=0)
            draw.line([(xVal,yVal),(xVal+BUBBLE_DIA,yVal)],fill=0)
    #print "Course Number",bubbleVal
    course = bubbleVal
                
    # Get Pages per Assignment
    bubbleVal = 0
    valCount = 5 # for the conversion from binary to decimal (up to 31 pages)
    xStart = bubbleX+bubbleInc*10
    yStart = bubbleY
    for j in range(2):
        yVal = yStart+(j*bubbleInc)
        for i in range(2): # we will skip the last three bubbles
            if j==1 and i>0: continue
            valCount-=1
            xVal = xStart+(i*bubbleInc)
            if bubbleFilled(bubbleData,xVal,yVal,BUBBLE_DIA):
                bubbleVal+=pow(2,valCount)
            draw.line([(xVal,yVal),(xVal,yVal+BUBBLE_DIA)],fill=0)
            draw.line([(xVal,yVal),(xVal+BUBBLE_DIA,yVal)],fill=0)
    #print "Assignment Number",bubbleVal
    pagesPerAssignment = bubbleVal

    # Get Assignment Number
    bubbleVal = 0
    valCount = 7 # for the conversion from binary to decimal
    xStart = bubbleX+bubbleInc*10
    yStart = bubbleY+bubbleInc
    for j in range(2):
        yVal = yStart+(j*bubbleInc)
        for i in range(4): # we will skip the first one
            if j==0 and i==0: continue
            valCount-=1
            xVal = xStart+(i*bubbleInc)
            if bubbleFilled(bubbleData,xVal,yVal,BUBBLE_DIA):
                bubbleVal+=pow(2,valCount)
            draw.line([(xVal,yVal),(xVal,yVal+BUBBLE_DIA)],fill=0)
            draw.line([(xVal,yVal),(xVal+BUBBLE_DIA,yVal)],fill=0)
    #print "Assignment Number",bubbleVal
    asmt = bubbleVal
            
    # Get Student ID
    bubbleStr = ''
    xStart = bubbleX
    yStart = bubbleY+bubbleInc*5
    for j in range(8):
        yVal = yStart+(j*bubbleInc)
        foundValue = False # a bit of error checking
        for i in range(36):
            xVal = xStart+(i*bubbleInc)
            if bubbleFilled(bubbleData,xVal,yVal,BUBBLE_DIA,thresh=0.5):
                #if foundValue:
                    # we already found a value, meaning the student put two bubbles in the same column!
                    #raise Exception("Error in student ID! Exiting.")
                    
                foundValue = True
                if i < 26:
                    bubbleStr+=chr(i+ord('a'))
                else:
                    bubbleStr+=chr(i-26+ord('0'))
            draw.line([(xVal,yVal),(xVal,yVal+BUBBLE_DIA)],fill=0)
            draw.line([(xVal,yVal),(xVal+BUBBLE_DIA,yVal)],fill=0)
        if not foundValue:
            bubbleStr+='_'
    #print bubbleStr
    id = bubbleStr
                
    #bubbleImage.show()
    return dept,course,asmt,id,pagesPerAssignment
    
def getDeptName(dept):
    deptName = ''
    with open(dataDir+"department_codes.txt","r") as codeList:
        for i in range(dept):
            deptName = codeList.readline()
    if deptName != '':
        return deptName.split(' ')[0]
    else:
        return 'No Department'

def compareResults(name,known,scanned):
    if known == scanned:
        print "%s: %s == %s" % (name,known,scanned)
    else:
        print "Incorrect %s! %s != %s" % (name,known,scanned)
        print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

def testScans(testData,imagesFolder,showImage=False,exceptions=True,onlyTest=-1):
    if onlyTest >= 0:
        testData = (testData[onlyTest],)
    for im in testData:
        print '------------------------------------'
        print "Scanning %s...(%s)" % (im[0],im[6])
        if (exceptions):
            try:
                bl_x,bl_y,bl_w,bubbleData = findBlackLine(imagesFolder+'/'+im[0])
                dept,course,asmt,id,pagesPerAssignment = findBubbles(bl_x,bl_y,bl_w,bubbleData)
                deptName = getDeptName(dept)
                compareResults("Department",im[1],deptName)
                compareResults("Course",im[2],course)
                compareResults("Assignment",im[3],asmt)
                compareResults("Pages per Assignment",im[4],pagesPerAssignment)
                compareResults("ID",im[5],id)

                print
            
            except Exception as ex:
                print "Failed on %s." % im[0]
                print "Exception: %s" % ex
                print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
                print
            
            finally:
                if showImage:
                    arrayToImage(bubbleData).show()
        else:
            bl_x,bl_y,bl_w,bubbleData = findBlackLine(imagesFolder+'/'+im[0])
            dept,course,asmt,id,pagesPerAssignment = findBubbles(bl_x,bl_y,bl_w,bubbleData)
            print "dept",dept
            deptName = getDeptName(dept)
            compareResults("Department",im[1],deptName)
            compareResults("Course",im[2],course)
            compareResults("Assignment",im[3],asmt)
            compareResults("Pages per Assignment",im[4],pagesPerAssignment)
            compareResults("ID",im[5],id)

            print

if __name__ == "__main__":
    testData = [('studentLettersCLASS.png','No Department',0,0,'',0,'Student Bubbles with letters and one class bubble.'),
            ('realScan4.png','COMP',15,1,1234567,0,'Student Bubbles with numbers'),
            ('test2a.png','No Department',0,0,0,0,'Perfect Blank Document'),
            ('test2.png','COMP',15,1,0,0,'Perfect Document'),
            ('realScans-0.png','COMP',15,1,9876543,0,'Good Document'),
            ('realScans-1.png','COMP',15,1,5454892,0,'Good Doc, a bit skewed'),
            ('realScans-1a.png','COMP',15,1,5454892,0,'Good Doc, unskewed'),
            ('realScans-2.png','COMP',15,1,-1,0,'Bad Student input'),
            ('realScans-2a.png','COMP',15,1,1012424,0,'Not the best bubbles'),
            ('realScans2-0.png','COMP',15,1,1234567,0,'Xs for bubbles'),
            ('realScans2-1.png','COMP',15,1,5555555,0,'Small dots for bubbles'),
            ('realScans2-2.png','COMP',15,1,2163222,0,'Good, messy bubbles'),
            ('realScans3.png','COMP',15,1,1234567,0,'Extraneous marks in assignment'),
            ('realScans3BadRot.png','COMP',15,1,1234567,0,'Really bad: skewed, extraneous marks in assignment, Xs for bubbles'),
            ]
    testData = [('studentLettersFilled1.png','No Department',15,1,0,'testid09','Student Bubbles with testID.'),
                ('realScansStudentData-0.png','No Department',15,1,0,'cgregg02','Decent real scan'),
                ('realScansStudentData-1.png','No Department',15,1,0,'qponmlkj','Decent real scan'),
                ('realScansStudentData-2.png','No Department',15,1,0,'__kNQrsu','BAD student ID'),
                ('realScansStudentData-3.png','No Department',15,1,0,'99999999','Decent real scan'),
                ('realScansStudentData-4.png','No Department',15,1,0,'cgregg02','Decent real scan'),
                ('realScansStudentData-5.png','No Department',15,1,0,'c_gregg_','BAD student ID')]
    if len(sys.argv) == 2:
        testImagesFolder=sys.argv[1]
    else:
        testImagesFolder='../../testImages'
    testScans(testData,testImagesFolder,exceptions=False)
    
