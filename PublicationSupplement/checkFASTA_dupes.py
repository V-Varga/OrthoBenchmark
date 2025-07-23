#!/bin/python
# -*- coding: utf-8 -*-
"""

Title: checkFASTA_dupes.py
Date: 2023.04.27
Author: Vi Varga

Description:
	This program parses a file containing FASTA headers and file names for FASTA
		headers that were discovered, during the process of encoding, to be 
		repeated within a FASTA file. The sequences associated with these FASTA 
		headers are checked to determine whether or not they are identical.

List of functions:
	No functions are defined in this script.

List of standard and non-standard modules used:
	sys
	pandas

Procedure:
	1. Loading required modules & assigning command line argument.
    2. Load the reference file into a Pandas dataframe. 
	3. Parse the Pandas dataframe and open the FASTA files with duplications, 
		to determine whether sequences within the same file with the same FASTA
		headers also contain identical sequence lines. 

Known bugs and limitations:
	- There is virtually no quality-checking integrated into the code.
	- The output file names are not user-defined, but are instead based on the 
		input file name. 
	- This script must be run from the directory in which the FASTA files to be 
		searched are located. 

Usage
	./checkFASTA_dupes.py input_file
	OR
	python checkFASTA_dupes.py input_file
	
	Where the input_file must be in the format fasta_sequence_header\tfasta_file_name,
		where the fasta_sequence_header is the original FASTA sequence header
		which has been found to be duplicated, and the fasta_file_name is the 
		name of the FASTA file in which the sequence header duplication occurs. 

This script was written for Python 3.9.16, in Spyder 5.4.3. 

"""


# Part 1: Import modules & assign command line arguments

#import necessary modules
import sys #allows execution of script from command line
import pandas as pd #allows manipulation of dataframes


#load input and output files
input_file = sys.argv[1]
#input_file = "PA_EncodingSummary__DUPES__EXTRACT.txt"
output_file_dupes = ".".join(input_file.split('.')[:-1]) + '_True.txt'
output_file_diffs = ".".join(input_file.split('.')[:-1]) + '_False.txt'


# Part 2: Assign the alphanumeric headers and write out results files

with open(input_file, "r") as infile, open(output_file_dupes, "w") as outfile_dupes, open(output_file_diffs, "w") as outfile_diffs:
	#open the input and output files
	ref_df = pd.read_csv(input_file, sep="\t", header=None)
	#import the input file contents into a Pandas dataframe
	ref_df.columns =["seq_header", "origin_file"]
	#adding column names for easier parsing
	for index, row in ref_df.iterrows():
		#iterate over the dataframe via its rows
		source_file = row["origin_file"]
		dupe_header = row["seq_header"]
		dupe_header = ">" + dupe_header
		#save the contents of the row to variables
		seq_list = []
		#create an empty list to save the sequences into
		with open(source_file, "r") as search_file: 
			#open the source file in order to search for the sequence header
			for line in search_file:
				#iterate through the input file line by line
				if line.startswith(">"):
					#identify the header lines and remove the end-line character
					header = line.strip()
					#remove the end-line character from the header line
					if header == dupe_header: 
						#check to see if the header matches the header being searched
						sequence = next(search_file).strip()
						#extract the amino acid sequence and save it to a variable
						#and then append the sequence to the seq_list
						seq_list.append(sequence)
			#now check to see whether the sequences are all the same
			uniq_dupes_list = list(set(seq_list))
			if len(uniq_dupes_list) == 1: 
				#if the sequence was repeated, i.e., the same header meant the same sequence
				#print the header to the _True.txt duplicates file without the ">" character
				outfile_dupes.write(dupe_header[1:] + "\n")
			elif len(uniq_dupes_list) > 1: 
				#if the sequences are not the same, despite having the same sequence header
				#print the header to the _False.txt duplicates file without the ">" character
				outfile_diffs.write(dupe_header[1:] + "\n")
			else: 
				#if the list of duplicate sequences is empty
				print("The uniq_dupes_list for file " + source_file + " is empty. Check your input files.")
