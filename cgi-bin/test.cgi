#!python2.7virt/venv/bin/python
import cgi,sys,os
import cgitb

cgitb.enable()

sys.stdout.write("Content-Type: text/html")
sys.stdout.write("\r\n")
sys.stdout.write("\r\n")
print "testing.\n"
print "remote user:",os.environ['REMOTE_USER']
# for k in os.environ.keys():
#     print '<p>'+k+':'+os.environ[k]

