import random
from random import randint
from copy import copy
import numpy as np

def parsetxt(str,filename,pathstr=None):
	""" Takes a textfile containing financial data, and a string indicating 
	what kind of data we shall extract from the file. Returns a list of 
	values corresponding to the data taken from the file. pathstr=None if 
	working in the directory where the file is stored 
	"""
	# open the file. For now only opening in read only mode
	if pathstr!=None:
		fpath=pathstr+'/'+filename
	else:
		fpath=filename
	file=open(fpath,'r')
      

	datalist=[]

	#it's more efficient to import functions once:
	dappend=datalist.append

	index=None

	# scan through all lines in the file
	with open(fpath) as file:
		for line in file:

			# these conditions should always be satisfied for valid 
			# textfiles
			if (index==None) and (str in line.split()):
					index=line.split().index(str)

			# However if you use a bad text file or pass in a bad 
			# string: 
			elif (index==None) and (str not in line.split()):
				print('This is a bad file, or you have passed in a bad string. ')
				return 'This is a bad file, or you have passed in a bad string. '
			elif (index!=None) and (str in line.split()):
				print('This is a bad file, or you have passed in a bad string.')
				return 'This is a bad file, or you have passed in a bad string.'

			# this part collects the data in the column by reading 
			# through all other lines of the file
			else:
				new_val=float(line.split()[index])
				dappend(new_val)

	#print(datalist)
	return datalist

def chunks(dlist,classifiers,length,num_chunks):
	""" Takes some data in the form of a list of lists(dlist), and some classifiers
	(classifiers) corresponding to the data. "Length" specifies how many randomly selected
	data points to be chosen from the list. It returns "length" randomly selected data 
	points as well as "length" randomly selected rows of the classifier matrix. 
	"Classifiers" right now is a list of arrays, although it could still work
     for a list of lists.
	"""
	randindexes=[]
	rappend=randindexes.append
	for num in range(num_chunks):
		while True:
			randindex=randint(0,length)
			if randindex not in randindexes:
				rappend(randindex)
				break

	randdata=[copy(dlist[index:index+length+1]) for index in randindexes]
	randclassifiers=[classifiers[index:index+length+1,:] for index in randindexes]

	return (randdata,randclassifiers)

# testcase for parsetxt
#data=parsetxt('Close','ford_5Y.txt')

# testcase for chunks
#dlist=[random.random() for j in range(10)]
#classifiers=[np.random.randint(1,10,(2,2)) for j in range(10) for k in range(10)]
#chunks(dlist,classifiers,5)