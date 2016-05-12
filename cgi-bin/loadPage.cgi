#!/usr/sup/bin/python2.7
#
# loadPage.cgi
#
#  purpose: pass arguments to an html page (using a simple mailmerge idea)
#     idea: an html page is not really a function, so passing
#           args to an html page is a little bizarre.
#      BUT: if the html page has a chunk of javascript that looks like:
#           var xyz = '';
#           var abc = '';
#           var pqr123 = '';
#           ...
#      AND we are given a hash with kes "xyz", "abc", "pqr123", ...
#     THEN we can plug in those values in the html page as we print
#          the page to the browser (via stdout)
#
# summary: we can make an html form into a template with places
#          for form variables.
#
#     NEW: special handling for grade_a_page
#	   we get the dimensions of the image and
#	   insert those into the form data
#    NOTE: this special handling should be moved to a separate module
#          designed for function-specific data but I don't think there
#          is any other cases right now.  When we get to two cases
#	   we can think about how to abstract the problem.
#
import cgi,sys,os
import cgitb
import json
import uuid
import subprocess
import re

cgitb.enable()

dataDir    = "../data/"			# path start for page name
classesDir = "classes/"
non_scaled_width = 850

def main():

	form = cgi.FieldStorage()		# get hash of cgi form data

	start_http_reply()
	page_ID = is_user_ok(form)		# authenticate user
	process_page( page_ID, form )		# find and process html page

#
# insert_dims: find the height and width of the image and
#              add those values to the form data set
#
#  args:  form hash
#  rets:  modified form
#  Add those pairs to the current form ( a dictionary )
#
def insert_dims( form ):


	if  "pageToLoad" not in form :	# get this out of the way
		return

	output = ""

	img_file = dataDir + classesDir + get_val(form, "pageToLoad" )
	try:
		output = subprocess.check_output( [ "file", img_file ] )
	except:
		print "Cannot run the file command"
		return form

	form = insert_from_info( output, form )
	return form

#
# read output of file(1) and put the height and width into the form
# args: string like: 
#   "page2.png: PNG image data, 1700 x 2200, 4-bit grayscale, non-interlaced"
#                                          ^--- note
# rets: modified form
#
def insert_from_info( file_output, form ):

	xform = {}
	words = file_output.split(" ")
	pos   = 0
	for w in words:
		if w == "x":
			wid = int( words[pos-1] )
			h   = (words[pos+1].split(","))[0]
			hgt = int( h )
			if wid != non_scaled_width:
				wid = str(wid/2)
				hgt = str(hgt/2)
			xform["canvasWidth"]  = str(wid)
			xform["canvasHeight"] = str(hgt)
			return xform
		pos = pos + 1

	return xform

#
#  is_user_ok -- get pageID to load AND check if user is valid
#    args: the form from the cgi request
#    rets: the pageID used to select the actual html page
#    note: if remoteUser sent from caller is not $REMOTE_USER, report/quit
#
def is_user_ok(form):
	
	remote_user = ""
	page        = ""
	try:
		page        = get_val(form, 'page'      )
		remote_user = get_val(form, 'remoteUser')
	except:
            print "Location: https://www.eecs.tufts.edu/~cgregg/virtualgrade\n"

	if remote_user != os.environ['REMOTE_USER']:
		print page
		sys.stdout.write("Unauthorized.\n")
		quit()
	#
	# I do not know why this is done. formKeys is not used
	# anywhere else
	#
	formKeys = list(form.keys())
	formKeys.pop(formKeys.index('page'))

	return page

#
# wrapper for getvalue to allow two kinds of storage
#
def get_val( form, key ):

	rv = ""
	try:
		rv = form[key].value
	except:
		rv = form[key]

	return rv
#
# load_new_page(html_file, form_data)
#   purp: plug in values from form_data[] into the vars in html_file
#   args: the name of an html file (assumed to be in html/ dir)
#         the hash of form_data
#   rets: nothing
#   outp: the html_file with data merged in
#
def load_new_page(html_file, form_data, xtra_data ):

	# TODO: Authenticate user
	# ...if userInfo['id']== '106628659834464477412':
	# read in html_file, insert data, print it to stdout

	with open( "html/" + html_file + ".html","r") as f:
		for line in f:
			foundKey=False
			for key in form_data.keys():
				if re.search("^var "+key+" = '';", line):
				# found an insertion spot!
				#   get value and insert it
					formValue = get_val(form_data, key)
					print("var "+key+" = '"+formValue+"';")
					print("// inserted normal value here")
					foundKey=True
					break

			for key in xtra_data.keys():
				if re.search("^var "+key+" = [0-9]*;", line):
					formValue = get_val(xtra_data, key)
					print("var "+key+" = "+formValue+";")
					print("// inserted xtra value here")
					foundKey=True
					break

			if not foundKey:
				sys.stdout.write(line)

def start_http_reply():
	sys.stdout.write("Content-Type: text/html")
	sys.stdout.write("\r\n")
	sys.stdout.write("\r\n")

#
# process_page -- insert data into an html form and print the form
#  args: id for page (mapped to actual html filename)
#        dictionary of cgi data
#
def process_page( page_ID, form ):

	xform = {}

	#userToken = form.getvalue('userToken')
	if page_ID == 'create':
		load_new_page( 'setupAssignment', form, xform)
	elif page_ID == 'processScans':
		load_new_page( 'processScannedPdfs', form, xform)
	elif page_ID == 'grade':
		load_new_page( 'gradeAssignments', form, xform)
	elif page_ID == 'gradeAnAssignment':
		load_new_page( 'startGrading', form, xform)
	elif page_ID == 'gradeOnePage':
		xform = insert_dims( form )
		load_new_page( 'grade_a_page', form, xform)
	elif page_ID == 'fullStatistics':
		load_new_page( 'fullStats', form, xform)
	elif page_ID == 'startAdmin':
		load_new_page( 'startPage', form, xform)
	elif page_ID == 'processStudentPDFs':
		load_new_page( 'processStudentPdfs', form, xform)
	elif page_ID == 'processQRpdfs':
		load_new_page( 'processQRpdfs', form, xform)
	else:
		print page_ID
		sys.stdout.write("Unauthorized.\n")


# -------------------------------------------------------------------
#  call main() here
# -------------------------------------------------------------------

if __name__ == "__main__":
	main()
