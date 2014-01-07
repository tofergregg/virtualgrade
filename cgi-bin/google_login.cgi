#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
import urllib2, urllib
import json
import uuid
import time
import datetime
from loadPage import loadNewPage

cgitb.enable()
dataDir = "../data/"
logDir = "log/"

#sys.stdout.write("Content-Type: text/html")
#sys.stdout.write("\n")
#sys.stdout.write("\n")

form = cgi.FieldStorage()

sys.stdout.write("Content-Type: text/html")
sys.stdout.write("\r\n")
sys.stdout.write("\r\n")

code=form['code'].value

mydata=[('code',code),
        ('client_id','530177174781-jbceho0sc7huam39s44htgpigt9f068v.apps.googleusercontent.com'),
        ('client_secret','LwoGDvf3IaRyKUzgkYjSubIM'),
        ('redirect_uri','http://209-6-230-17.c3-0.smr-ubr2.sbo-smr.ma.cable.rcn.com:8000/web/cgi-bin/google_login.py'),
        ('grant_type','authorization_code')]
mydata=urllib.urlencode(mydata)
path='https://accounts.google.com/o/oauth2/token'    #the url you want to POST to
req=urllib2.Request(path, mydata)
req.add_header("Content-type", "application/x-www-form-urlencoded")
try:
    page=urllib2.urlopen(req).read()
except:
    # didn't process Google authentication properly, so reload login page
    print("<html>")
    print("<head>")
    print("<script>")
    print("function loginPage(){window.location='http://209.6.230.17:8000/web/loginPage.html';}")
    print("</script>")
    print("</head>")
    print("<body onload='loginPage();'>")
    print("</body>")
    quit()

data = json.loads(page)
access_token = data['access_token']

response = urllib2.urlopen('https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token='+access_token)
userInfo = json.loads(response.read())

# with open("../data/testLogin.txt","w") as f:
#     f.write("Got past the login!\n")
#     f.write('code:'+form['code'].value+"\n")
#     f.write('access_token:'+access_token+'\n')
#     f.write('User id:'+userInfo['id']+'\n')
#     f.write('Name:'+userInfo['name']+'\n')

# create user token and save authentication to log file
# TODO: migrate this process to mysql
userToken = str(uuid.uuid4())
authTime=time.time()
humanReadableAuthTime=str(datetime.datetime.fromtimestamp(authTime))

authorizedUsers=[]
with open(dataDir+'users.txt','r') as f:
    for line in f:
        authorizedUsers.append(line[:-1].split(','))
    
# make sure user is authorized
userAuthorized = False
for googleId,remoteUser,userType in authorizedUsers:
    if userInfo['id'] == googleId:
        userAuthorized=True
        break
        
if userAuthorized:
    with open(dataDir+logDir+'virtualgrade.log','a') as f:
        f.write('login,'+
                remoteUser+','+
                humanReadableAuthTime+','+
                repr(authTime)+','+
                userInfo['name']+','+
                userInfo['id']+','+
                userToken+','+
                'Authorized'+
                '\n')

    sys.stdout.write("Welcome, "+userInfo['given_name']+"!\n")
    if userType=='admin':
        loadNewPage('startPage',{'userToken':userToken,'remoteUser':remoteUser})
    elif userType=='grader':
        loadNewPage('gradeAssignments',{'userToken':userToken,'remoteUser':remoteUser})
    # read in setupAssignment.html and print it to the screen
    
else:
    with open(dataDir+logDir+'virtualgrade.log','a') as f:
        f.write('attemptedLogin,'+userInfo['name']+','+
                humanReadableAuthTime+','+
                repr(authTime)+','+
                userInfo['id']+','+
                userToken+','+
                'Unathorized'+
                '\n')
    sys.stdout.write("Unauthorized login attempt!\n")
    



