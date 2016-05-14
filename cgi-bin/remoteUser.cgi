#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb
cgitb.enable()

import uuid
import time
import json

dataDir = "../data/"
classesDir = "classes/"
metadataDir = "metadata/"
userDatabase = "users.txt"
logDir = "log/"

def getUser():
        remoteUser = os.environ['REMOTE_USER']
        with open(dataDir+userDatabase,"r") as f:
                users = json.loads(f.read())
                rights = 'unauthorized'
                for userInfo in users:
                        if remoteUser == userInfo['user']:
                                rights = userInfo['status']
                                break
                return (remoteUser,rights)

if __name__ == '__main__':
        remoteUser,rights = getUser()
        sys.stdout.write("Content-Type: application/json")
        sys.stdout.write("\n")
        sys.stdout.write("\n")
        print json.dumps({'remoteUser':remoteUser,'rights':rights})
