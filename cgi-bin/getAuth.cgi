#!python2.7virt/venv/bin/python

# https://accounts.google.com/o/oauth2/token
# code=4/rUTEFBuSgtJFaNde5fr84ycHXG4S.4q8o98xWX44faDn_6y0ZQNgONGpZhgI
# client_id=530177174781-jbceho0sc7huam39s44htgpigt9f068v.apps.googleusercontent.com
# client_secret=LwoGDvf3IaRyKUzgkYjSubIM
# redirect_uri=http://209-6-230-17.c3-0.smr-ubr2.sbo-smr.ma.cable.rcn.com:8000/web/cgi-bin/google_login.py
# grant_type=authorization_code

import urllib2, urllib
mydata=[('code','4/rUTEFBuSgtJFaNde5fr84ycHXG4S.4q8o98xWX44faDn_6y0ZQNgONGpZhgI'),
        ('client_id','530177174781-jbceho0sc7huam39s44htgpigt9f068v.apps.googleusercontent.com'),
        ('client_secret','LwoGDvf3IaRyKUzgkYjSubIM'),
        ('redirect_uri','http://209-6-230-17.c3-0.smr-ubr2.sbo-smr.ma.cable.rcn.com:8000/web/cgi-bin/google_login.py'),
        ('grant_type','authorization_code')]
mydata=urllib.urlencode(mydata)
path='https://accounts.google.com/o/oauth2/token'    #the url you want to POST to
req=urllib2.Request(path, mydata)
req.add_header("Content-type", "application/x-www-form-urlencoded")
page=urllib2.urlopen(req).read()
print page
