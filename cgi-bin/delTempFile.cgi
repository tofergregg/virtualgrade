#!python2.7virt/venv/bin/python

import cgi,sys,os
import cgitb

import time

cgitb.enable()

dataDir = "../data/"

form = cgi.FieldStorage()
fileToDelete = form['filename'].value

if not fileToDelete.startswith('data/'):
    fileToDelete = '../data/'+fileToDelete # a bit of input sanitization...
else:
    fileToDelete = '../'+fileToDelete

sys.stdout.write("Content-Type: text/html")
sys.stdout.write("\r\n")
sys.stdout.write("\r\n")

time.sleep(30)
try:
    os.remove(fileToDelete)
    sys.stdout.write("Successfully deleted file.\r\n")
except OSError:
    sys.stdout.write("Failed to delete file!\r\n")
    