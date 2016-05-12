#!python2.7virt/venv/bin/python
# return a list of semesters, departments, classes, assignments
# this is basically the folder structure for ../data/classes:
# ../data/classes/[semester]/[dept]/[class]/assignment_[assignmentNum]

import cgi,sys,os
import cgitb
import json

cgitb.enable()
dataDir = "../data/"
classesDir = "classes"
baseDirLen = len((dataDir+classesDir).split('/'))-1

def alpha_base26(n):
        '''converts integer n to a 5-digit alphabetic base 26 string
           representation. E.g., 0->aaaaa, 1->aaaab, 2->aaaac,...,26->aaaba, etc.
        '''
        result = ""
        while n >= 0:
                # special case for n < 26
                if n < 26:
                        result += chr(n + ord('a'))
                        break 
                result += chr(n / 26 + ord('a'))
                n = n - 26 * (n / 26) 
        # pad zeros at the front if length is less than 5
        for i in range(5 - len(result)):
                result = 'a' + result
        return result
                
def sort_multi_key(x):
        '''returns a key from a list of lists 
           (e.g.,[['2014-fall', 'COMP', '15'], 
           ['2014-fall', 'COMP', '11']]) that translates the last
           element to an alphabetic representation that will
           get sorted properly. E.g., 11 will come before 105.
           If the last element is not an int, this does not
           guarantee numeric correctness (e.g., 150WD could come
           before 18.
        '''
        try: 
                x_num = int(x[-1])
                # convert to alphabetic base 26
                x_str = alpha_base26(x_num)
                return ''.join(x[:-1])+x_str
                
        except ValueError:
                # must punt on this one
                return ''.join(x)

           
           
# traverse root directory, and list directories as dirs and files as files
dirStructure = []
semesters=[]
departments=[]
classes=[]
assignments=[]

for root, dirs, files in os.walk(dataDir+classesDir):
    if root.count(os.sep) >= 6:
    	del dirs[:]
    #print root,root.count(os.sep)
    if 'metadata' in root:
        continue
    if root.count(os.sep)==3:
        semesters.append(root.split(os.sep)[3:])
    elif root.count(os.sep)==4:
        departments.append(root.split(os.sep)[3:])
    elif root.count(os.sep)==5:
        classes.append(root.split(os.sep)[3:])
    elif root.count(os.sep)==6:
        try:
                with open(root+'/metadata/assignmentName.txt',"r") as f:
                        root = root + ' ('+f.readline()[:-1]+')'
        except:
                pass # no worries if the assignment name file doesn't exist
        assignments.append(root.split(os.sep)[3:])

semesters.sort()
departments.sort()
classes.sort(key=sort_multi_key)
assignments.sort()
dirStructure={'semester':semesters,'department':departments,'course':classes,'assignment':assignments}

sys.stdout.write("Content-Type: application/json")
sys.stdout.write("\n")
sys.stdout.write("\n")
print json.dumps(dirStructure)

