#!/usr/sup/bin/python2.7

####!python2.7virt/venv/bin/python

import sys

#sys.path.insert(0,'/h/cgregg/public_html/web/cgi-bin/python2.7virt/venv/lib/python2.7/site-packages/PIL')

import cgitb
cgitb.enable()
import sys,os

sys.path.insert(0,'/h/cgregg/public_html/virtualgrade/cgi-bin/python2.7virt/venv/lib/python2.7/site-packages')

from PIL import Image, ImageDraw, ImageFont

dataDir = "../data/"

def bubblePageUpdate(deptName,courseNumber,assignmentNumber,studentId='',pagesPerAssignment=0):
    import scipy as sp

    font_fname = dataDir+'Courier New Bold.ttf'
    font_size = 140
    font = ImageFont.truetype(font_fname, font_size)

    #image0 = Image.fromarray(bg_image)
    image0 = Image.open(dataDir+"bubble_template.png")

    image0.paste(255,(50+417,50,1550+417,180))
    draw = ImageDraw.Draw(image0)

    radius = 80
    xInc = 112.9
    yInc = 112.9
    xTopLeft = 466
    yTopLeft = 200
    # Department
    deptName = deptName.upper()
    with open(dataDir+"department_codes.txt","r") as codeList:
        count = 1
        for line in codeList:
            if line.startswith(deptName+" -"):
              break
            count += 1
    b = bin(count)[2:].zfill(8)
    # b=bin(255)[2:] # for testing
    xStart = xTopLeft
    yStart = yTopLeft
    draw.text((90+417, 40), deptName, font=font, fill='rgb(0, 0, 0)')
    for j in range(2):
        yVal = yStart+(j*yInc)
        for i in range(4):
            xVal = xStart+(i*xInc)
            if b[i+4*j] == '1':
                draw.ellipse((xVal,yVal,xVal+radius,yVal+radius),fill=0)
    
    # Course Number
    b = bin(courseNumber)[2:].zfill(12)
    xStart = xTopLeft+xInc*5
    yStart = yTopLeft
    draw.text((700+417,40),str(courseNumber).zfill(3),font=font,fill='rgb(0,0,0)')
    for j in range(3):
        yVal = yStart+(j*yInc)
        for i in range(4):
            xVal = xStart+(i*xInc)
            if b[i+4*j] == '1':
                draw.ellipse((xVal,yVal,xVal+radius,yVal+radius),fill=0)

    # Assignment Number
    b = bin(assignmentNumber)[2:].zfill(7) # 128 possible assignments
    xStart = xTopLeft+xInc*10 # we will skip the first bubble
    yStart = yTopLeft+yInc
    draw.text((1270+417,40),str(assignmentNumber).zfill(3),font=font,fill='rgb(0,0,0)')
    for j in range(2):
        yVal = yStart+(j*yInc)
        for i in range(4):
            if i==0 and j==0:
                continue # we only use seven bubbles, not eight, so skip the first bubble
            xVal = xStart+(i*xInc)
            if b[(i+4*j)-1] == '1':
                draw.ellipse((xVal,yVal,xVal+radius,yVal+radius),fill=0)
                
    # pages per assignment
    b = bin(pagesPerAssignment)[2:].zfill(5) # up to 31 pages per assigment
    xStart = xTopLeft+xInc*10
    yStart = yTopLeft
    for j in range(2):
        yVal = yStart+(j*yInc)
        for i in range(4): # we'll skip the last three bubbles
            if j==1 and i > 0:
                continue # skip the last three bubbles
            xVal = xStart+(i*xInc)
            if b[i+4*j] == '1':
                draw.ellipse((xVal,yVal,xVal+radius,yVal+radius),fill=0)
    # student ID
    if (studentId != ''):
        image0.paste(255,(10+417,550,1430+417,750))
        draw.text((50+417,550),('Student Username: '+studentId).zfill(3),font=font,fill='rgb(0,0,0)')
        xStart = xTopLeft
        yStart = yTopLeft+yInc*5
        for j,letter in enumerate(studentId.lower()):
            yVal = yStart+(j*yInc)
            if letter >= 'a' and letter <= 'z':
                xVal = xStart+((ord(letter)-ord('a'))*xInc)
            elif letter >= '0' and letter <= '9':
                xVal = xStart+(26*xInc+(ord(letter)-ord('0'))*xInc)
            else:
                continue # no letter or number in studentId!
            draw.ellipse((xVal,yVal,xVal+radius,yVal+radius),fill=0)
    if __name__ == "__main__": image0.show()
    image0.save(dataDir+'bubbleOverlay.png')

if __name__ == "__main__":
    # args: dept (e.g., "COMP")
    #       class number (e.g., "15"), 
    #       assignment number (e.g., "1")
    #       <= 8 char student name (e.g., "cgregg02") (optional)
    #bubblePageUpdate("COMP",15,1,'testId09')
    #bubblePageUpdate("COMP",15,1,'')
    dept = sys.argv[1]
    classNum = int(sys.argv[2])
    assignmentNum = int(sys.argv[3])
    if len(sys.argv) >= 5:
        studentId = sys.argv[4]
    else:
        studentId = ''
    if len(sys.argv) >= 6:
        pagesPerAssignment = int(sys.argv[5])
    else:
        pagesPerAssignment = 0
    bubblePageUpdate(dept,classNum,assignmentNum,studentId,pagesPerAssignment)
    