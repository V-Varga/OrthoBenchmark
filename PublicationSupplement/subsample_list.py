#!/bin/python
# -*- coding: utf-8 -*-
"""

Title: subsample_list.py
Date: 2025.02.19
Author: Vi Varga

Description:
	This program parses an input list of file names and randomly subsamples n 
		elements from the file list, based on user input. 
	A required file that must be in the output may be provided by the user.

List of functions:
	No functions are defined in this script.

List of standard and non-standard modules used:
	sys
	random

Procedure:
	1. Importing modules & assigning command line arguments.
    2. Processing input file list.
	3. Subsampling the file name list.
	4. Writing out results.

Known bugs and limitations:
	- There is no quality-checking integrated into the code.

Usage
	./subsample_list.py input_list output_name seed_no out_count [required_file]
	OR
	python subsample_list.py input_list output_name seed_no out_count [required_file]
	
	Where the input_list file must have be in the format: 
		file_name\nfile_name etc.

This script was written for Python 3.9.19, in Spyder 5.4.5. 

"""


# Part 1: Import modules & assign command line arguments

# import necessary modules
import sys # allows execution of script from command line
import random # enables random number generation/processing


# process input arguments
# input file name list
input_list = sys.argv[1]
#input_list = "FASTA_list.txt"
# output file name
output_name = sys.argv[2]
#output_name = "OrthoBenchmark_subsample_1M.txt"
# set the seed number
seed_no = int(sys.argv[3])
#seed_no = 42
# get the number of desired files from the sample list
out_count = int(sys.argv[4])
#out_count = 167

# required file
if len(sys.argv) == 6: 
	# if there is a required file
	required_file = sys.argv[5]
	#required_file = "Pseudomonas_aeruginosa_PAO1_107_CopyN_edit.fasta"


# Part 2: Process input file list


# create empty list to populate with file names
file_list = []

with open(input_list, "r") as infile: 
	# open the file for reading
	for line in infile:
		# loop over the file contents line by line
		fasta_name = line.strip()
		# remove the end-line character
		# and append the file name to the file
		file_list.append(fasta_name)


if 'required_file' in globals():
	# check if a required file name has been defined
	# if so, remove the file from the file list
	# ref: https://www.geeksforgeeks.org/python-remove-string-from-string-list/
	file_list = [i for i in file_list if i != required_file]
	# also reduce the sampling count by 1
	out_count = out_count - 1


# Part 3: Subsample the file name list

# set the seed for reproducible subsampling
# ref: https://stackoverflow.com/questions/65649821/random-sample-how-to-control-reproducibility
random.seed(seed_no)

# randomly subsample the list
# ref: https://www.geeksforgeeks.org/randomly-select-n-elements-from-list-in-python/
out_list = random.sample(file_list, out_count)


# Part 4: Write out results

with open(output_name, "w") as outfile: 
	# open the output file for writing
	if 'required_file' in globals():
		# check if a required file name has been defined
		# write the required file name to the output file if so
		outfile.write(required_file + "\n")
	for j in out_list:
		# iterate over the elements of the outfile list
		# and write them to the output file
		outfile.write(j + "\n")
