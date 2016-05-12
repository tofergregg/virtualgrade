#!/usr/sup/bin/python2.7
#
#!python2.7virt/venv/bin/python
#
#  convertScansPython -- convert pdf scans of bubbled sheets
#
#   hist: 2016-03-04 added the clump feature and rearranged some code
#
#   args: passed using cgi form
#
#        pdfFolder = form['pdfFolder'].value
#        convertId = form['guid'].value
#        semester = form['semester'].value
#        department = form['department'].value
#        course = form['course'].value
#        assignment = form['assignment'].value
#        pagesPerStudent = int(form['pagesPerStudent'].value)
#        remoteUser = form['remoteUser'].value
#        darkScans = form['darkScans'].value
#        if darkScans == 'True':
#                darkScans = True
#	 clumps = form['clumps'].value
#
#  NEW: we add the idea of page CLUMPS
#	idea: 	if a problem spans several pages and one
#		grader needs to do all parts of it, and 
#		there may be flow-through on answers
#		OR if a page has extra space for long answers
#		THEN those pages should all be combined into
#		one bigger png image
#	SO:	a clump_list is a string of sequences of page#s
#		as in: "1 2 3,4,5 6,7 8"
#		which will make 1 -> 1
#		2 -> 2
#		3,4,5 -> 3
#		6,7 -> 4
#		8 -> 5
#	HOW:	convert will accept a list of files and will
#		also allow the -append option to combine images
#	SO:	we just parse the string splitting on spaces then
#		on commas and build command arrays for subprocess.call
#		

import cgi,sys,os
import cgitb
cgitb.enable()
#print "Context-Type:text/plain\n"
#print os.environ["LD_LIBRARY_PATH"]

conv_density = "200"		# used to conver pdf to png
conv_quality = "85"		# used to conver pdf to png

import subprocess
import uuid
import omrImage
import threading
import Queue
import traceback

dataDir     = "../data/"
logDir      = "log/"			# relative to dataDir
tempPngsDir = "tempPngs/"		# relative to dataDir
classesDir  = "classes/"		# relative to dataDir

# -----------------------------------------------------------------------
# global variables 
#	-- these are global to make the status reporting available to all

q		= ""			# 
status_log_file = ""			# these are global to handle
					# global access to status log

# -----------------------------------------------------------------------
# main code for scan processing
# -----------------------------------------------------------------------

def main():

	start_narration()
	params    = read_form_data()
	pdf_files = get_pdf_file_list( params['pdfFolder'] )

	# set up queue for status updates
	global q
	q = Queue.Queue()

	for pdf in pdf_files:
		status_report( "Processing file " + pdf , True )
		process_one_pdf( pdf, params )

	status_report( "Finished", True )

#
# just run ls *.pdf on the pdfFolder, return the array
#	these are JUST the filenames, not the entire paths
#
def get_pdf_file_list( pdfFolder ):

	pdfFiles = []
	for filename in os.listdir( pdfFolder ):
		if filename.endswith( ".pdf" ):
			pdfFiles.append(filename)
	return pdfFiles

# ----------------------------------------------------------------------------
# process_one_pdf -- 	convert a pdf scan into sets of png images, one imgSet
#			per student
#  args: pdf    		-- source file of scans (full path)
#
#  note: Each pdf file has zero or more exam scans.  An exam scan is
#	 a sequence of pages, all scans have the same number of pages.
#	 Each exam belongs to a student, identified by the bubbles on
#	 the first page in the exam.
#
#	 Therefore, we read the cover page for each exam, find the
#	 student name, and then extract the pdf pages from the pdf file
#	 and convert those into png files in the assignment dir for
#	 that student.
#
#	 We use a base_pg to hold the page number of the cover page
#	 in the pdf file.  That index will advance by pagesPerStudent
#	 for each loop.
#
#	 As a new (as of March 2016) feature, those ppS pages can be
#	 clumped into bunches and assigned to single pngs for easier
#	 grading. 
#
#	 the params arg is a dict with useful infor
#
def process_one_pdf( pdf , params ):

	pdf = params['pdfFolder'] + "/" + pdf	# prepend full path
	pages_in_pdf = count_pages_in_pdf(pdf)	# find number of pages
	base_pg      = 0			# base of current page set
	clump_list   = params['clumps'].split();# split defaults to /\s+/
	ppS	     = params['ppS']
	assgnDir     = params['asgnDir']
	cpS	     = params['cpS']
	darkScans    = params['darkScans']

	print "for pdf: ", pdf, "clump list is ", clump_list

	while base_pg < pages_in_pdf:
		#
		# process first page to get name, make a dir, 
		# note: if the name cannot be read, the 'student_name'
		# is a unique string
		#
		(studID, studDir) = process_cover_page(pdf, base_pg, ppS,
							    assgnDir, cpS,
							    darkScans)

		print "Working on page", (base_pg+1)
		# we already did page1, that was the cover page
		# now each clump will be stored as a page starting with page2
		# until all clumps are done
		png_pgnum = 2
		for clump in clump_list:
			pngFile = studDir + "page" + str(png_pgnum) + ".png"
			convert_one_clump(pdf, base_pg, clump, pngFile, studID)
			png_pgnum += 1

		base_pg += params['ppS']

# -------------------------------------------------------------------------
#
# convert_one_clump 
#	purp: take clump of pages from the pdf and make png
#	      put the result in the correct directory
#	note: the main reason for this function is to narrate
#	      which keeps the main loop cleaner
#	args:	pdf 	the file containing all the pages
#		base_pg	the page number in that file holding cover page
#		clump	which pages to combine into an image
#		pngFile	name of png file
#		studID	student Id (for reporting)
#
def convert_one_clump( pdf, base_pg, clump, pngFile, studID):

	if len( clump.split(",") ) == 1:	# if one page in clump
		pages = "page " + clump		# use singular
	else:
		pages = "pages " + clump	# else use plural
	
	msg = "\tConverting " + pages + " for student " + studID
	msg = msg + " saving as " + ( pngFile.split("/")[-1] )
	status_report( msg, True )

	rv = convert_pdf_clump_to_png( pdf, base_pg, clump, pngFile )
	if rv != 0:
		err_msg = " Error converting " + pages + " for " + studID 
		status_report( err_msg, True )

# -------------------------------------------------------------------------
#
# convert_pdf_clump_to_png
#
#	args: pdfFile		- read pages from here (full pathname)
#	      base		- the base pagenumber for the current scan
#				  note: base page is 0-based in pdf file
#	      clump		- a string of comma-separated numbers
#	      pngFile		- where to put result
#
#	note:	the pdf has several scans in it (with ppS pages per assignment)
#		so if we ask for a clump of 2,3,4  and the current
#		frame in the pdf file starts at offset 'base'
#		then we extract pages base+2-1, base+3-1, base+4-1
#		
#	      so page x will be page (x-1), then ppS+(x-1), then 2*ppS+(x-1)
#
#	rets:   the return code from convert
#	NOTE:   convert wants the page number to be 0-based
#
def convert_pdf_clump_to_png(pdfFile, base, clump, pngFile):

	arg_list = [ "convert", "-append",
			 	"-density", conv_density,
				"-quality", conv_quality  ];

	page_list = clump.split(",")
	for pg in page_list:
		real_page = str(base + int(pg) - 1)	# -1 for zero-base
		arg_list.append( pdfFile + "[" + real_page + "]" )

	arg_list.append( pngFile )
	# print "About to execute: ", arg_list
	rv = subprocess.call( arg_list )
	return rv

# -------------------------------------------------------------------------
# process_cover_page
#   this function reads one pdf page into a png
#   then scans the png to find the student ID name
#   then makes a dir for that name
#   then moves that png into that dir with name page1.png
#   then returns (student name, full path to the student dir)
#   NOTE: if the student name is not readable, we get back
#	  a long unique string to use until we figure out the actual name
#   RETS: a pair: jsmith01, full path to student directory with "/" at end
#   ARGS: pdf        -- name of complete pdf file of all scans
#	  base_page  -- the page in that file to examine
#	  ppS
#	  assignmentDir 
#	  cpS
#	  darkScans
#

def process_cover_page( pdf, base_page, ppS, assignmentDir, cpS, darkScans ):

	tmpID  = str(uuid.uuid4())
	tmpPNG = dataDir + tempPngsDir + tmpID + ".png"
	pg     = str(base_page + 1)

	#
	# need to check return code to make sure the conversion worked
	#
	print "Working on page " + pg + " in " + pdf

	rv = convert_pdf_clump_to_png( pdf, base_page, "1", tmpPNG )
	if rv != 0:
		return rv

	#
	# now, extract data from bubble page
	#
	id = analyze_cover_page( pdf, pg, tmpPNG, tmpID, ppS, 
					assignmentDir, darkScans )

	#
	# then build dir and move file there
	# student_dir will have full path to student dir with trailing "/"
	#
	student_dir = setup_student_dir( assignmentDir, id, cpS )
        os.rename(tmpPNG, student_dir + 'page1.png')
	return (id, student_dir)

# -------------------------------------------------------------------------
#
# analyze_cover_page -- scan png of cover page for user input
#	args: 
#		pdf		name of orig pdf file (for reporting)
#		pg		page number in file (for reporting only)
#		tmpPNG		image file holding the cover page
#		tmpID		user Id to return if cannot find valid name
#		ppS		pages per student
#		assignemnetDir	where results go
#		darkScans	omr code needs this
#	rets:
#		userID		of student, as written on bubbles
#
def analyze_cover_page( pdf, pg, tmpPNG, tmpID, ppS, assignmentDir, darkScans ):

	dept = 0
	id   = tmpID		# default to this until we read one from form
	msg  = ""

	#
	# Analyze the image to find box and bubble data
	#
	print "About to find blackbox..."
	(boxX, boxY, boxW, bubbleData) = omrImage.findBlackBox(tmpPNG)
	if bubbleData == None:
		print "did not find black box"
		msg = "Can't find black box! File: " + pdf + " Page: " + pg
	else:
		try:
			print "Finding bubbles"
			(dept, crs, assn_num, id, ppS_junk) =		    \
				omrImage.findBubbles(boxX, boxY, boxW,      \
						     bubbleData, darkScans)
		except:
			print traceback.format_exc()
			msg = ( "Can't find bubbles! File: " + pdf
			    + " Page: " + pg )

	print "OMR done, id is [", id, "]"
	#
	# map number to 4-letter code by asking the dept codes db
	#
        deptName = omrImage.getDeptName(dept)

        # student ID may have trailing underscores if len(id)<8
        id = id.rstrip('_')

	#
	# if this is not a valid first page, we stay with the temp Id
	# I don't know why we care if pages per student is 0 
	#
        if ppS == 0 or id == tmpID or id == "" or (not id[0].isalpha()):
		id = tmpID
		msg += "Could not find bubbles! "		\
		     + "File: " + pdf + " Page: " + pg		\
		     + "\nTemp name will be: "    + id 
        else: 
		msg = ( ( 'Found first page for student %s, '
		          + 'Course: %s, '
		          + 'Assignment: %d, '
		          + 'Number of Pages in assignment: %d' )
		    % (id, (deptName + str(crs)), assn_num, ppS) )

	print msg
	status_report( msg, True )

	return id

# -------------------------------------------------------------------------
#
# setup_student_dir -- build the student directory and install metadata
#
#	args:
#		assignmentDir	dir above it (.../COMP/15/assignment_3/)
#		id		student ID (jsmith01)
#		cpS		clumps per student
#	rets:
#		name of directory for student (with trailing "/")
#	does:
#		create dir, metadatadir, logfiles dir it not there already
#
def setup_student_dir( assignment_dir, id , cpS):

	metadata_dir = assignment_dir + id + '/metadata/'
	try:
		os.makedirs( metadata_dir + 'lockfiles/' )

	except OSError:
		pass		# don't care, it may be already there
        
	#
	# put a 'numpages.txt' file in metadata
	#
	with open(metadata_dir + 'numpages.txt',"w") as f:
		f.write( str(cpS) + '\n' )
		f.close()
        
	return (assignment_dir + id + "/")


def start_narration():
	sys.stdout.write("Content-Type: text/plain")
	sys.stdout.write("\n")
	sys.stdout.write("\n")
	sys.stdout.write("starting scans.\n")
	sys.stdout.flush()

#
# read_form_data -- extract form data and populate dict then return dict
#
#
def read_form_data():

	rv = {}

	try:
		form            = cgi.FieldStorage()
		pdfFolder       = form['pdfFolder'].value
		convertId       = form['guid'].value

		semester        = form['semester'].value
		department      = form['department'].value
		course          = form['course'].value
		assignment      = form['assignment'].value

		pagesPerStudent = int(form['pagesPerStudent'].value)
		remoteUser      = form['remoteUser'].value
		darkScans       = form['darkScans'].value
		clumps		= form['clumps'].value

		
	except:
		print "Using default fields"
		pdfFolder = 	'/comp/170/admin/scans/testDir/'
		convertId = 	'testId'
		semester = 	'2016-spring'
		department = 	'COMP'
		course = 	'170'
		assignment = 	'assignment_999'
		pagesPerStudent = 6
		remoteUser = 'nobody'
		darkScans = "False"
		clumps    =  "1 2,3,4 5,6"

	assignmentDir 	=  dataDir + classesDir + semester 	\
			+ '/' + department + '/' + course 	\
			+ '/' + assignment + '/'

	global status_log_file
	status_log_file = convertId + ".log"

	if darkScans == 'True':
		darkScans = True
	else:
		darkScans = False

	clumps = clean_clump_list( clumps, pagesPerStudent )
	if clumps == "" or clumps == "0":
		clumps = make_single_clumps( pagesPerStudents )

	#
	# The number of clumps is how many clumps are in the list.
	# We have to add 1 back because we took 1 out of the list.
	#
	clumpsPerStudent = 1 + len( clumps.split() )

	rv['pdfFolder'] = pdfFolder;
	rv['ppS']       = pagesPerStudent;
	rv['cpS'] 	= clumpsPerStudent
	rv['asgnDir']	= assignmentDir
	rv['darkScans'] = darkScans
	rv['clumps']	= clumps

	return rv

# ----------------------------------------------------------------------
# if no clumps are given, then make default clumps, each one page
# if clumps are given, remove page 1 from list
#
def clean_clump_list( clumps, packet_len ):

	clump_list = []

	if clumps == "" or clumps == "0":
		for i in range( 2, packet_len+1 ):
			clump_list.append( str(i) )
	else:
		# otherwise just remove a page1 anywhere it appears
		# I know there must be a concise python way to do this
		# but this clumsy one works
		temp_list = clumps.split()
		for t in temp_list:
			pages = t.split(",")
			pages_no_1 = []
			for p in pages:
				if p != "1":
					pages_no_1.append(p)
			
			clump_list.append( ",".join(pages_no_1) )

	return " ".join(clump_list)

# ---------------------------------------------------------------
# helper code down here
# ---------------------------------------------------------------

#
# count_pages_in_pdf --
#   args: name of pdf file
#   rets: number of pages OR -1 if error
#
def count_pages_in_pdf( fn ):

	# add_to_log( "counting pages in " + fn )
	output = ""
	try:
		# identify will print one line per pdf page in file
		output = subprocess.check_output( ["identify", fn],
						stderr=subprocess.STDOUT )
	except:
		# could not process PDF
		add_to_log('count_pages_in_pdf failed')
		print  "Could not process PDF! " + fn
		add_to_log('output is ' + output)
		return -1

	lastLine = output.split('\n')[-2]

	# output of identify looks like one of two formats:
	#
	#     p5.pdf PDF 612x792 612x792+0+0 16-bit Bilevel DirectClass ...
	# OR
	#     p5.pdf[0] PDF 612x792 612x792+0+0 16-bit Bilevel ...
	#     p5.pdf[1] PDF 612x792 612x792+0+0 16-bit Bilevel DirectCla ...
	# THUS
	#     lastLine will have the [ or it won't.
	#     If has a  [ then grab the number and add 1 (note: 0 based)
	#     If has no [ then set count to 1
	# the last page number (not present for PDFs with one page)
	#
	if '[' in lastLine:
		pagesInPdf = int( lastLine.split('[')[1].split(']')[0] ) + 1
	else:
		pagesInPdf = 1

	# add_to_log( " page count is " + str(pagesInPdf) )
	return pagesInPdf

# ----------------------------------------------------------------------
# send a message to the status report Q and then flush it to file
#
def status_report( msg, do_flush ):

	q.put( msg )
	if do_flush:
		writeQueueToFile( q, status_log_file )

# ----------------------------------------------------------------------
# read from Q, copy to logfile, AND write to stdout as we go
#	args: q 	-- message Q : read strings from here
#	      fileName	-- a file relative to logDir in dataDir
#
def writeQueueToFile(q,fileName):

	#
	# sequentially writes queue items to a file
	#
	with open(dataDir + logDir + fileName, "a") as f: 	# unbuffered
		while not q.empty():
			output = q.get()
			f.write(output+'\n')
			f.flush()
			sys.stdout.write(output+'\n')
			sys.stdout.flush()

# -------------------------------------------------------------------------
# call main from here
# -------------------------------------------------------------------------

if __name__ == "__main__":
	main()

