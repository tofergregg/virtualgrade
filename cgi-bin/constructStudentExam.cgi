#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
import subprocess
import uuid
import threading
import time,datetime
import scipy as sp
from PIL import Image, ImageDraw, ImageFont

cgitb.enable()
dataDir = "../data/"
classesDir = "classes/"
metadataDir = "metadata/"
logDir = "log/"

def createScoreTotal(studentDir,studentScore,totalPoints,testComplete):
    # place a total score box at the top of the first page (page1_graded.png or page1.png)
    # if the score is incomplete, append with "(inc)" for incomplete
    # We save the file in the metadata directory to retain the original page .png file
    dirListing = sorted(os.listdir(dataDir+classesDir+studentDir))
    if 'page1_graded.png' in dirListing:
        pageFile='page1_graded.png'
    else:
        pageFile='page1.png'
    
    font_fname = dataDir+'Courier New Bold.ttf'
    font_size = 40
    font = ImageFont.truetype(font_fname, font_size)
    try:
        image = Image.open(dataDir+classesDir+studentDir+pageFile)
    except IOError:
        # could not find the file
        return False
    #image = image.convert("RGB")
    width,height = image.size
    
    draw = ImageDraw.Draw(image)
    scoreText = studentScore+"/"+totalPoints
    if testComplete=='incomplete':
        scoreText+='(inc)'
    textWidth, textHeight = draw.textsize(scoreText, font=font)
    print "image mode:",image.mode
    if 'RGB' in image.mode:
    	draw.rectangle(((width/2)-(textWidth/2),25,(width/2)+(textWidth/2),35+textHeight),fill=(135,206,235))
    	draw.text(((width/2)-(textWidth/2), 25), scoreText, (0,51,102), font=font) # midnight blue!
    	#draw.rectangle(((width/2)-(textWidth/2),25,(width/2)+(textWidth/2),25+textHeight))
    elif 'LA' in image.mode:
    	draw.text(((width/2)-(textWidth/2), 25), scoreText, font=font,fill=(0,255))
    else:
    	#draw.rectangle(((width/2)-(textWidth/2),25,(width/2)+(textWidth/2),25+textHeight),fill='black')
    	draw.text(((width/2)-(textWidth/2), 25), scoreText, font=font,fill=0)
    print scoreText
    print width/2,textWidth/2

    #image.show()
    image.save(dataDir+classesDir+studentDir+metadataDir+'page1_totalGrade.png',"PNG")
    #img_resized = image.resize((188,45), Image.ANTIALIAS)
    return True

def specialSort(listToSort):
    # takes a list of files where some files are named "pageX.png" and/or "pageX_graded" 
    # and X can be an integer.
    # We arrange the files so that all the "pageX.png" files are in ascending order by X
    # We parse the list, pick out the pageX.png and pageX_graded.png files and parse the 
    # X as an integer
    partialList = []
    for value in listToSort:
        if value.startswith('page'):
            if '_graded' in value:
                pageNum = int(value[4:].split('_')[0])
            else:
                pageNum = int(value[4:].split('.')[0])
        else:
            pageNum = 0 # we will sort all other files to the beginning
        partialList.append((value,pageNum))
    partialList = sorted(partialList, key = lambda bothValues: bothValues[1])
    partialList = [x[0] for x in partialList]
    return partialList

try:
    form = cgi.FieldStorage()

    remoteUser = form['remoteUser'].value

    # studentDir should be in the form:
    # 'semester/department/course/assignment/studentId/'
    studentDir = form['studentDir'].value
    studentScore = form['studentScore'].value
    totalPoints = form['totalPoints'].value
    completeExam = form['completeExam'].value

except:
    remoteUser = sys.argv[1]
    studentDir = sys.argv[2]
    studentScore = sys.argv[3]
    totalPoints = sys.argv[4]
    completeExam = sys.argv[5]

sys.stdout.write("Content-Type: text/plain")
sys.stdout.write("\n")
sys.stdout.write("\n")

scoreSucceeded = createScoreTotal(studentDir,studentScore,totalPoints,completeExam)
student = studentDir.split('/')[-2]
if not scoreSucceeded:
        sys.stdout.write("Content-Type: text/plain")
        sys.stdout.write("\n")
        sys.stdout.write("\n")
        sys.stdout.write("Could not create PDF for "+student+"!\n")
        quit()
# get list of files, and only keep graded and ungraded pages
dirListing = sorted(os.listdir(dataDir+classesDir+studentDir))
for file in list(dirListing):
    if not file.endswith('.png'):
        dirListing.remove(file)
    if '_graded' in file:
        dirListing.remove(file.split('_')[0]+".png")
dirListing = specialSort(dirListing)
# first page needs to be the temp file we put in metadata
dirListing[0]=metadataDir+'page1_totalGrade.png'
dirListing = [dataDir+classesDir+studentDir+x for x in dirListing]

subprocess.call(["convert"]+dirListing+[dataDir+classesDir+studentDir+student+"_Full.pdf"])

# update log file
now = time.strftime("%c")
with open(dataDir+logDir+'virtualgrade.log','a') as f:
    f.write('createdExam,'+remoteUser+','+
            now+','+student+'\n')

sys.stdout.write("Full PDF created for "+student+"\n")

