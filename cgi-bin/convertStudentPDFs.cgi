#!/usr/sup/bin/python2.7

#
#  convertStudentPDFs.cgi 
#   handle student submitted PDF files NOT SCANNED
#
#   ARGS: passed as form variables
#		srcDir = form['pdfFolder'].value
#				absolute path to dirs with pdfs
#				path ends with "/"
#		dstDir = form['assignmentDir'].value;
#				relative to ../data/classes
#				path ends with "/"
#		convID = form['guid'].value
#				a magic cookie
#
#   overview:
#	A student 'provides' several PDF files to a directory .
#	Say the assignment is number A.
#	The names are something like p1.pdf, p2.pdf ... pN.pdf
#	This script goes to each student directory in the
#		specified assignment and converts each of
#		the pX.pdf files to a png file OR files
#		in ~vg/.../COMP/170/assignment_ApX/<logname>
#		If we are doing multi-page processing, then
#		we produce files page1.png page2.png ...
#		If we are doing one-page per pdf, we just get
#		page1.png
#
#	details: loop through all dirs in /comp/170/grading/hwA
#		 find most recent submission for each student
#		 then loop through the pdf files in that dir
#		 and make a dir for that student for each problem
#		 and then in that dir make the png files
#
#	When it makes a new problem dir, it goes to the parent
#	dir and in the metadata dir is the point_values.csv file for
#	the set of parts.  Take the item that corresponds to the
#	problem number and copy THAT value into the metadata file
#	for the new problem.
#
#	For example, if hw9 has four problems called p1, p2, p3, p4
#	with points 2,3,1,5 then the assignment_9/metadata/point_values.csv
#	contains 2,3,1,5 and the
#	assignment_9p1/metadata/point_values.csv will have 2
# 
#
import cgi,sys,os
import errno
import cgitb
import subprocess
import uuid
import threading
import Queue
import re
import shutil

cgitb.enable()
# --------------- settings for this file ------------
#
semester = "2016-spring"
#
# ---------------------------------------------------
# settings that do not depend on current term
#
dataDir = "../data/"
logDir = "log/"
classesDir = "classes/"
stand_alone=0			# to run in terminal, not website
#
# disabled for now, turn on for more debugging
#
def add_to_log(msg):

	return
        with open( 'debuglog.txt', "a") as f:
		f.write( msg + '\n' )
		f.flush()
		f.close()

add_to_log('hello')
#
# prov_root is abs path to provide dir of multiple subdirs, one per submission
# png_dir  is relative to current dir via 
#
#    ../data/classes/2016-spring/COMP/170/assignment_X  
#
# where X is the assignment number
#
def main():
	start_narration
	(prov_root, png_dir, conv_ID, onePNG) = read_form_data()
	src_dirs                      = get_newest_provide_dirs(prov_root)
	convert_pdfs_from( prov_root, src_dirs, png_dir, conv_ID , onePNG)

# ----------------------------------------------------------------------------
# - FIRST: get data from form/page that called this program ------------------
#
# read_form_data()
#   purp: get 'assignmentDir', 'pdfFolder', 'guid', "merge" from form
#   rets: those values as a tuple
#   note: if missing data, then default to silly bogus values
#   note: the srcDir is the full path, including the trailing "/"
#   note: the dstDir is the path from here (including ../data/classes) 
#    but: the dstDir dir has the trailing / removed
#         because we build dirs with names 2016-spring/COMP/170/assignment_1A
#         where A is the problem number based on the submitted filename.
#         I think it is easier to remove the / here rather than 
#	  to keep taking it off later
#
def read_form_data():
	#
	# assignment dir should be in form
	# 2016-spring/COMP/15/assignment_12
	#
	if stand_alone == 1:
		srcDir = "/g/170/2016s/grading/hw4/"		# abs path
		dstDir = "2016-spring/COMP/170/assignment_4"	# rel path
		convID = "abcdef"				# cookie
		merge  = 1

	else:
		form = cgi.FieldStorage()
		print form.keys()		# huh?
		try:
			srcDir = form['pdfFolder'].value
			dstDir = form['assignmentDir'].value;
			convID = form['guid'].value
			merge  = form['merge'].value
		except:
			srcDir = "/g/170/2016s/grading/hw5_mini/"
			dstDir = "2016-spring/COMP/170/assignment_5"
			convID = "abcdef"
			merge  = 0

	#
	# remove trailing "/" from png (dst) dir
	#
	if dstDir[-1] == '/':
		dstDir = dstDir[:-1]

	# may be for debugging...
	print srcDir
	print dstDir
	print convID

	# then prepend path for dest (png) dir
	# dataDir is "../data/", classesDir is "classes/"
	# and dstDir is "2016-spring/COMP/170/assignment_1/"
	dstDir = dataDir + classesDir + dstDir

	add_to_log( 'ret: ' + srcDir + ' ' + dstDir + ' ' + convID )

	return (srcDir, dstDir, convID, merge)

# ----------------------------------------------------------------------------
# -- TWO: Find dirs of submitted pdf files.  Find newest for each student ----
#
# get_newest_provide_dirs()
#
#   Take the name of the dir holding all provide submissions
#   and get the newest one for each student.
#   Use a hash mapping stud_uid -> largest submission number
#
def get_newest_provide_dirs(provide_root):

	all_dirs = os.listdir(provide_root)
	maxsub  = {}
	for d in all_dirs:				# jsmith02.3
		p = d.split('.')			# [jsmith02 3]
		if len(p) == 2 and is_a_num(p[1]):	#
			if p[0] in maxsub:
				curr = int(maxsub[p[0]])
				if ( int(p[1]) > curr ):
					maxsub[p[0]] = p[1]
			else:
				maxsub[p[0]] = p[1]
	#
	# Now: build the list of all dirs in alpha order by name
	#
	usernames = sorted(maxsub.keys())
	newest_dirs = []
	for u in usernames:
		latest = u + "." + maxsub[ u ]
		add_to_log("adding dir " + latest )
		newest_dirs.append( latest )

	return newest_dirs

#
# cute hack from stackoverflow
#
def is_a_num(n):
	try:
		int(n)
		return True
	except ValueError:
		return False

# ----------------------------------------------------------------------------
# -- THREE: Do the conversion from pdf to png --------------------------------
# ------ A: Set up the directories for the problems --------------------------
#
# convert_pdfs_from -- do the conversion
#   prov_root   -- full path to the directory that contains submission dirs
#		   this has a trailing slash
#   newest_dirs -- the smith02.3 subdirs under orig_dir with pdf files
#   png_dir     -- path to current script to place to make dirs and store imags
#		   this path does NOT have a trailing slash
#		   It looks like  .../COMP/170/assignment_3
#
#   conv_ID     -- ID for the conversion
#   m		-- boolean for 'merge pdf pages into one png?'
#
#   does: for each student dir in prov_root, convert all pdfs to pngs
#
def convert_pdfs_from(prov_root, newest_dirs, png_dir, convID, m):

	add_to_log('convert_pdfs_from has merge = ' + str(m) )
	# first, make a hash from studentdir to file list
	# and    a list of all problem names
	(prov_dir2files, prob_names) = get_file_lists_and_prob_names(
						newest_dirs, prov_root)

	make_prob_dirs(png_dir, prob_names)

	q = Queue.Queue()
	q = process_all_prov_dirs( prov_root, prov_dir2files, 
				   png_dir  , convID, q, m )
	q.put("Finished")

#
# Loop through all provide dirs to get 
#     map of jsmith02.12 -> list of pdf files
#     set of problem names
#
# for each provide dir, list all pdf files and use their
# names (p1, p2, ...) to build a set and use their filenames
# to build a map of provide do to set of pdf files
# Rets: a tuple of the hash and the set of names
#
def get_file_lists_and_prob_names(newest_dirs, prov_root):

	prov_dir2files = {}
	prob_names = set()

	for prov_dir in newest_dirs:
		# this is the list of pdf files for a student dir
		pdf_files = []
		# this loop stores filenames, no paths
		# BUT the last part of the path is the key
		# each fn will be something like p1.pdf, p2.pdf ...
		for fn in os.listdir( prov_root + prov_dir ):
			if fn.endswith(".pdf"):
				pdf_files.append( fn )
				prob_names.add( fn.split('.')[0] )
		# prov_dir is just jsmith02.12
		prov_dir2files[prov_dir] = pdf_files
		# print prov_dir2files[student]

	print prob_names			# DEBUG
	return ( prov_dir2files, prob_names )
	
#
#  make_prob_dirs -- make all the dirs for the problems in this assignment
#    png_dir is a relative path (does not matter if rel or abs, though)
#    it looks like .../COMP/170/assignment_200
#    note: png_dir does not have a trailing "/"?
#    append to that path each probname and make a metadata subdir in each
#
def make_prob_dirs( png_dir, prob_names ):
	#
	# create subfolders for each problem based on assn number
	# name is ..../assignment_3  (no trailing /)
	#   add something like p3 then "/"
	#
	if png_dir[-1] == "/":
		png_dir = png_dir[:-1]

	for hw in prob_names:
		prob_dir = png_dir + hw + "/"
		try:
			os.makedirs( prob_dir )
		except OSError:
			pass		# dont' care if already there

		try:
			shutil.copytree( png_dir  + "/metadata/", 
					 prob_dir + "/metadata/")
		except OSError:
			pass		# probably already copied

		set_point_values( hw, prob_dir + "/metadata/point_values.csv" )

#
# set_point_values -- modify the point_values.csv file to contain only
#		      the point values for this problem
#
# args: hwID  (e.g. p3), point_values_filename
# rets: nothing
# does: opens file, splits comma-sep list of numbers
#		    extracts the one in position for the problem number
#		    and writes that number back
#
# todo: make this more flexible so the problem can have multiple pages
#	OR so that a map attaches points to each problem name
#
#
def set_point_values( hwID, point_values_file ):

	prob_num_list = re.findall('\d+', hwID)

	if ( len(prob_num_list) == 0 ):
		return

	pos = int(prob_num_list[0]) - 1	# ordinal to offset

	# get data from file
	try:
		file = open( point_values_file )
	except OSError:
		return
	vals = file.read()
	file.close()

	# look up value and rewrite file
	vals = vals.split(",")
	if ( pos < len(vals) ):
		points = vals[pos]
		try:
			file = open( point_values_file, "w" )
		except OSError:
			return
		file.write( points + '\n' )
		file.close()

# ----------------------------------------------------------------------------
# -- THREE: Do the conversion from pdf to png --------------------------------
# ------ B: now loop through submission dirs and process files ---------------
#
# process_all_prov_dirs
#   args: prov_root    e.g. /g/170/2016s/grading/hw3/
#         pd2files     e.g. jsmith02.13 -> p1.pdf, p2.pdf, p3.pdf
#                           jumbo23.3   -> p1.pdf, p2.pdf, p5.pdf
#         png_dir      e.g. ../data/classes/2016-spring/COMP/170/assignment_3
#	  onePNG	1 or 0
#
#   note: prov_root has trailing slash
#    and: png_dir   does NOT have trailing slash
#
def process_all_prov_dirs( prov_root, prov_dir2files, png_dir, convID, q, m ):

	for prov_dir in prov_dir2files:
		utln = prov_dir.split('.')[0]
		process_student( prov_root + prov_dir, 
					   utln, 
					   prov_dir2files[prov_dir],
					   png_dir,
					   q,
					   convID + ".log",
					   m
		)
	return q

#
# wrapper for processing one student
#
#  args: full-path-to-student-provide_dir   # a string
#        jsmith,                            # username
#        [ p1.pdf p2.pdf ... pN.pdf ],      # list of pdf files
#	  ".../assignment_3/",              # pngdir without slash
#	  q, blah.log                       # Q and q log
#
#  todo: make the merging more sophisticated
#
def process_student( stud_provdir, utln, pdf_list, png_dir, q, qfn, onePNG):

	add_to_log('processing student with merge = ' + str(onePNG) )
	if int(onePNG) == 1:
		add_to_log('doing SINGLE PAGE  version')
		processStudentSp(stud_provdir, utln, pdf_list, png_dir, q, qfn)
	else:
		add_to_log('doing multipage version')
		processStudentMp(stud_provdir, utln, pdf_list, png_dir, q, qfn)

# ----------------------------------------------------------------------------
# -- THREE: Do the conversion from pdf to png --------------------------------
# ------ C: take one pdf file and make one or more png files  ----------------
# ------    There are two versions: all into one image or one image per page -
#
#  process one student singlePage
#     args: student_provide_dir   -- full path to student submission (no /)
#           user_id of student
#           pdf_list : array of pdf files for that student
#           png_dir  : ../2016-spring/COMP/170/assignment_3 (no slash)
#           Q        : where to write messages as we go
#           Qfilename: write Q here (?) I'm not sure
#
def processStudentSp(prov_fullpath, stud_uid, pdf_list, png_dir, q, qFileName):
    #
    # ORIG: place all PDFs for student into student folder,
    # ORIG: numbered page1.png, page2.png, etc.
    # NEW:  combine all images into a single png
    # ARGS:  prov_fullpath : /comp/170/grading/hw3/jsmith01.3
    #        stud_uid      : name without a sequence suffix  (acrook01)
    #        pdfList       : p1.pdf p2.pdf ... p5.pdf
    #        png_dir       : 2016-spring/COMP/170/assignment_3 
    #	     q             : a queue for narrating progress
    #	     qFileName	   ; I guess we write to this (not sure)
    #
    # note: each set is in /comp/170/grading/hw3/jsmith01.3/p?.pdf
    #
    #       so each src dir maps the N files to N subdirs in VG dirs
    #       that is, loop through all the p?.pdf files in the pdflist
    #       and put each one in 2016-spring/COMP/170/assignment_3p?/jsmith01
    #       in a file called page1.png
    #
    # loop  through all pdf files p1.pdf p2.pdf ... p5.pdf
    #
    # Note: if there is a _graded version of a png file, then
    #       do NOT over-write the original
    #
    for filename in pdf_list:

	#
	# build path to orig file and path to dest dir
	# All orig files for one student are in same dir
	#   /comp/170/grading/hw4/jsmith01.3  + "/" + p2.pdf
	# All dest files for one student are in diff dirs
	#   .../COMP/170/assignment_4p2 + "/" + jsmith01
	#
	pdf_file = prov_fullpath + "/" +  filename
	png_path = build_dirs_for( stud_uid, png_dir, filename, 1 )

	#
	# prevent over-writing answers already graded
	#
	if os.path.isfile( png_path + "/" + "page1_graded.png" ):
		msg = ("NOT converting %s for student %s, already graded," 
			% (filename, stud_uid ) )
		writeQueueToFile(q, qFilename)
	else:
	#
        # For single page, just make one page: page1.png
	#
		convertPdfToPng( pdf_file, (png_path + "/" + "page1.png") , 1 )
		msg = ("\tConverting file %s for student %s to page1.png." 
			% (filename, stud_uid) )

	q.put( msg )
	writeQueueToFile(q, qFileName)


#
# convertPdfToPng -- does what the name says
#
# args: src file, dest file, combine
#  if combine is true, then make one file
#
def convertPdfToPng(pdfFile,pngFile,combine):

	print "convert "+ pdfFile + " -> " + pngFile + " ("+str(combine)+")"

	if combine:
        	subprocess.call(["convert", "-density",	"200", 
					"-depth",	"8", 
					"-quality", 	"90",
					"-append",
					pdfFile, 
					pngFile])
	else:
		subprocess.call(["convert", "-density",	"200", 
					"-depth",	"8", 
					"-quality", 	"90",
					pdfFile, 
					pngFile])

#
# build_dirs_for( jsmith01, png_dir, .../assignment_3/ )
#
#   does: build .../170/assignment_3p2/jsmith02
#		 and its lockfile subdir for a student
#   Regardless of number of pages in png, we need a dir for the
#         student and its subdirs for lockfiles
#      args:	student userID, 	    ( e.g. jsmith02 )
#		dir where pngs should go    ( e.g. ../COMP/170/assingment_2 )
#		name of pdf file submitted  ( e.g. p2.pdf )
#
#   RETURNS: path to the new dir it built (no slash at end)
#
def build_dirs_for( stud_uid, png_dir, ans_file, num_pages ):
	#
        # [1] Create student directory (don't fail if it exists already)
        #     The directory should be based on the PDF name.
	#     e.g. if pdf file is called p5.pdf
	#     then fullAssignmentDir: 2016-spring/COMP/170/assignment_3 + p5
	#     then append jsmith01 to make
	#		2016-spring/COMP/170/assignment_3 + p5/jsmith01
	#

	prob_id       = ans_file.split('.')[0]		# p2.pdf -> p2
        prob_dir      = png_dir + prob_id		# ... + nt_3p2
	stud_dir      = prob_dir + '/' + stud_uid	# ... + nt_3p2/jumbo

	#
	# now make .../assignment_3p2/jumbo
	#
        try:
		os.makedirs( stud_dir )

        except OSError as exc: 			# Python >2.5
		if exc.errno == errno.EEXIST and os.path.isdir( stud_dir ):
			pass
		else:
			raise
        
        # create assignment dir, student dir, 
	# metadata dir, and lockfiles dir if it doesn't exist

        metadataDir = stud_dir + '/metadata/'
    
        try:
            os.makedirs(metadataDir + 'lockfiles/')

        except OSError:
            pass 	# ignore locfiles/ fail ; probably created before
    
	#
        # put a 'numpages.txt' file in metadata
	#
        with open( metadataDir + 'numpages.txt', "w") as f:
		f.write( str(num_pages) + '\n') 
		f.close()

	return stud_dir

#  process one student MultiPage
#
#     args: student_provide_dir   -- full path to student submission (no /)
#           userID of student
#           pdf_list : array of pdf files for that student
#           png_dir  : ../2016-spring/COMP/170/assignment_3 (no slash)
#           Q        : where to write messages as we go
#           Qfilename: write Q here (?) I'm not sure
#
#
def processStudentMp(prov_fullpath, stud_id, pdf_list, png_dir, q, qFileName):

	add_to_log('doing MP for ' + stud_id )
	#
	# loop  through all pdf files p1.pdf p2.pdf ... p5.pdf
	# make each into as many png files as the pdf has pages
	#
	for filename in pdf_list:
		add_to_log('MP: handling file ' + filename + ' for ' + stud_id )
		#
		# build path to orig file and path to dest dir
		# All orig files for one student are in same dir
		#   /comp/170/grading/hw4/jsmith01.3  + "/" + p2.pdf
		# All dest files for one student are in diff dirs
		#   .../COMP/170/assignment_4p2 + "/" + jsmith01
		#   so: make those dest dirs and put 0 in metadata/numPgs
		#
		pdf_file = prov_fullpath + "/" +  filename
		png_path = build_dirs_for( stud_id, png_dir, filename, 0 )

		pages_in_pdf = count_pages_in_pdf( pdf_file )
		add_to_log('MP: file:' + pdf_file 
					+ ' pages:' + str(pages_in_pdf) )
		add_to_log('MP: png_path: ' + png_path )

		#
		# extract all pages from PDF and number starting at 1 #####
		#
		for i in range( pages_in_pdf ):
			src_pnum = str(i)
			dst_pnum = str(i+1)
			src_name = pdf_file + '['     + src_pnum + ']'
			dst_name = png_path + '/page' + dst_pnum + '.png'
			grd_name = png_path + '/page' + dst_pnum + '_graded.png'

			if os.path.isfile( grd_name ):
				msg = ( "\tNOT converting page " + dst_pnum 
					+ ' from file ' + filename
					+ ' for student ' + stud_id 
					+ ' [already graded]' )
			else:
				convertPdfToPng( src_name, dst_name, 0 )

				msg = ( "\tConverting page " + dst_pnum
					+ ' from file ' + filename
					+ ' for student ' + stud_id )
			q.put( msg )
			writeQueueToFile(q, qFileName)

#
# count_pages_in_pdf -- 
#   args: name of pdf file
#   rets: number of pages OR -1 if error
#
def count_pages_in_pdf( fn ):

	add_to_log( "counting pages in " + fn )
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

	add_to_log( " page count is " + str(pagesInPdf) )
	return pagesInPdf

# ----------------------------------------------------------------------------
# --- Narration of progress for User to watch --------------------------------
# 

def writeQueueToFile(q, fileName):

	#
	# sequentially writes queue items to a file
	# unbuffered, append
	#
	with open( dataDir + logDir + fileName, "a") as f:
		while not q.empty():
			output = q.get()
			f.write(output+'\n')
			f.flush()
			sys.stdout.write(output+'\n')
			sys.stdout.flush()

def start_narration():
	sys.stdout.write("Content-Type: text/plain")
	sys.stdout.write("\n")
	sys.stdout.write("\n")
	sys.stdout.write("starting conversion.\n")
	sys.stdout.flush()

# ----------------------------------------------------------------------------
# -- MAIN --------------------------------------------------------------------

add_to_log('calling cgi to convert PDFs')
add_to_log('my name is:[' + __name__ + ']')

# call main function here
#
if __name__ == "__main__":
	main()
	exit(0)

