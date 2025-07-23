# -*- coding: utf-8 -*-
#!/bin/python
"""

Title: og_membership_test.py
Date: 2025.07.19
Author: Vi Varga

Description:
	This program compares the parsed results files from 4 orthologous clustering
        programs in order the score the similarity of the orthologous clusters 
        created by these programs.
	The user can set a target threshold average similarity value, under which results
		should not be reported. Default is 50%.

List of functions:
	list_of_strings(arg): 
		Parses argument input into a list from comma-separated string.
	data_2_pandas(prog1_input, prog2_input, prog3_input, prog4_input):
		Loads input parsed OG databases into Pandas dataframes and dictionaries. 
	create_prot_dict(prog1_df, prog2_df, prog3_df, prog4_df):
		Creates the protein query ID to list of assigned OGs dictionary.
	filter_prot_dict(prog1_df, prog2_df, prog3_df, prog4_df):
		Filter the contents of the protein query ID to list of assigned OGs
		dictinary to only include those OGs as keys that were clustered by more than 1
		clustering program.
	membership_test(filt_prot_dict, prog1_dict, prog2_dict, prog3_dict, prog4_dict):
		Create all-vs-all membership test and compile results.
	avg_membership_scores(comparison_dict):
		Calculate the mean average the scores in the comparison dictionary.
	threshold_test(og_score_dict):
		Test which program overlaps meet the testing threshold percent value.

List of standard and non-standard modules used:
	argparse
	pandas
	json
	difflib
	statistics
	tqdm

Procedure:
	1. Loading required modules, setting the threshold value, identifier and program names
		to be used in the comparison filtration and the corresponding output file name.
	2. Determining input files as command-line arguments, and importing the contents
		of these JSON dictionaries as Pandas dataframes. Checkpoint 1 is reached at 
		the completion of this step.
	3. Creation of the protein query ID to OG cluster assignments list dictionary.
		Checkpoint 2 is reached at the conclusion of this step, when this dictionary
		is exported in JSON format.
	4. Filtration of the protein query ID to OG assignment list dictionary to exclude
		protein queries that were only clustered by one program. Checkpoint 3 is reached
		at the conclusion of this step, when the new dictionary is exported in JSON
		format.
	5. The all-vs-all OG membership tests are completed, and a dictionary is created
		containing the similarity scores of the clusters created by the programs.
		Checkpoint 4 is reached at the conclusion of this step, when this comparison
		dictionary is exported in JSON format.
	6. The scores inside of the comparison dictionary are averaged. Checkpoint 5 is
		reached at the conclusion of this step, when this smaller dictionary is exported
		in JSON format.
	7. The threshold membership percentage value is used to filter the programs with
		the most similar clusters, and a new dictionary is created to containing only
		this data. Checkpoint 6 is reached at the conclusion of this step.
	8. The contents of the dictionary created in the final step (ie. the final,
		membership threshold-filtered data) is written out to a text file.

Known bugs and limitations:
	- There is no quality-checking integrated into the code.
	- The membership_percent threshold value must be given as an integer, not as a
		decimal percentage.

Version: 
	This is version 2.5 of this program.
	Version 1.0 was initially published as og_membership_test.py in the
		https://github.com/V-Varga/TrichoCompare/tree/main GitHub repository. 
	Version 2.0 is not publicly available, but can be provided on request. It is essentially this 
		script, but implemented with sys rather than with argparse.

Usage:
	The full program can be run with:
		./og_membership_test.py [-h] (-a | -c CHECKPOINT_NUM) [-j INPUT_JSON] [-i TEST_IDENTIFIER] 
			[-p MEMBERSHIP_PERCENT] [-o OUT_NAME] [-d INPUT_FILES] [-n PROGRAM_NAMES] [-v]
		OR
		python og_membership_test.py [-h] (-a | -c CHECKPOINT_NUM) [-j INPUT_JSON] [-i TEST_IDENTIFIER] 
			[-p MEMBERSHIP_PERCENT] [-o OUT_NAME] [-d INPUT_FILES] [-n PROGRAM_NAMES] [-v]

		* Where the membership_percent threshold value should be given as an integer percentage value.
			Default value is 50.
		
		* Where argument co-dependencies are as follows: 
			- -a requires -d
			- -c=2 or -c=3 requires -d
			- -j requires -i and -j

		* Where the acceptable input JSON files include:
			- prot_dict_[TEST_IDENTIFIER].json: This will start the program after Checkpoint 2, by providing a
				complete version of the prot_dict protein query to OG list dictionary.
			- filt_prot_dict_[TEST_IDENTIFIER].json: This will start the program after Checkpoint 3, by providing
				a complete version of the filt_prot_dict filtered protein query to OG list,
				from which queries only predicted to cluster by one program have been removed.
			- compare_OG_dict_[TEST_IDENTIFIER].json: This will start the program after Checkpoint 4, by
				providing a version of the compare_dict clustering program to cluster score list
				dictionary.
			- og_score_dict_[TEST_IDENTIFIER].json: This will start the program after Checkpoint 5, by providing
				a version of the OG scoring dictionary in which the average scores have already
				been calculated.


This script was written for Python 3.9.18, in Spyder 5.4.3. 

"""


#################################   ARGPARSE   #######################################


import argparse
# the argparse module allows for a single program script to be able to carry out a variety of specified functions
# this can be done with the specification of unique flags for each command

# Define a custom argument type for a list of strings
# ref: https://www.geeksforgeeks.org/python/how-to-pass-a-list-as-a-command-line-argument-with-argparse/
def list_of_strings(arg):
	'''Parses custom argument-type of a comma-separated string into a list.'''
	# split a string into a list based on comma placement
	return arg.split(',')

parser = argparse.ArgumentParser(description =
								 'This program compares the parsed results files from 4 orthologous clustering \
									 programs in order the score the similarity of the orthologous clusters \
							        created by these programs. \
								The user can set a target threshold average similarity value, under which results \
									should not be reported. Default is 50%.')
# The most general description of what this program can do is defined here


# adding the arguments that the program can use
# set up the two run types: complete or checkpoint-based
run_group = parser.add_mutually_exclusive_group(required=True)
run_group.add_argument(
	'-a', '--run_all',
	action='store_true',
	help = 'Runs the entire program from start, rather than from a checkpoint. Requires --program_names argument.'
	)
	# the '-a' flag will call for the program to be run in its entirety
run_group.add_argument(
	'-c', '--checkpoint',
	dest='checkpoint_num',
	metavar='CHECKPOINT_NUM',
	type=int, 
	choices={2, 3, 4, 5}, 
	help='Specify the last completed checkpoint, from which the program should resume: 2, 3, 4 or 5.'
	)
	# the '-c' flag will call to resume a previous run from a given checkpoint

# add inputs as optional arguments
parser.add_argument(
	'-j', '--json',
	dest='input_json',
	metavar='INPUT_JSON',
	type=argparse.FileType('r'), 
	help='Specify the name of the JSON file output at the last completed checkpoint, \
		from which processing should be resumed. Please ensure the correct JSON file is submitted!'
	)
	# the '-j' flag should be used to specify the checkpoint-generated JSON to use as input
parser.add_argument(
	'-i', '--identifier',
	dest='test_identifier',
	metavar='TEST_IDENTIFIER',
	type=str,
	help = 'Specify an identifier keyword to use. Useful in cases where multiple \
		values for some parameter are being tested by the user. Default is datetime. Required for resuming run from a checkpoint.'
	)
	# the '-i' flag will allow the user to specify an identifier
parser.add_argument(
	'-p', '--threshold_percent',
	dest='membership_percent',
	metavar='MEMBERSHIP_PERCENT',
	type=int,
	default=50,
	help='Specify the desired membership overlap threshold percent to test. Value should be \
		an integer, not a percent. Ex.: -p 50 for 50%% overlap testing. Default is 50%%.'
	)
	# the '-c' flag will call to resume a previous run from a given checkpoint
parser.add_argument(
	'-o', '--out_name',
	metavar='OUT_NAME',
	dest='out_name',
	default='OG_membership_results_',
	help = 'This argument allows the user to define an output file basename. \
		The default basename is "OG_membership_results_".'
	)
	# the '-o' flag allows the user to define a the output file basename
parser.add_argument(
	'-d', '--input_databases',
	dest='input_files',
	metavar='INPUT_FILES',
	type=list_of_strings, 
	help = 'Provide the names of the input cluster databases output by the __ script in a \
		comma-separated list. Exactly four (4) file names must be provided. Ex.: \
			-d prog1_parsed.json,prog2_parsed.json,prog3_parsed.json,prog4_parsed.json \
       Required for complete run & runs from checkpoints 2 or 3.'
	)
	# the '-d' flag will expect 4 cluster databases to be provided as input
parser.add_argument(
	'-n', '--program_names',
	dest='program_names',
	metavar='PROGRAM_NAMES',
	type=list_of_strings, 
	help = 'Provide the names of the clustering programs used in a comma-separated list. \
		Exactly four (4) names must be provided. Default is: "Program1,Program2,Program3,Program4"'
	)
	# the '-n' flag will expect 4 clustering program names to be provided as input

parser.add_argument(
	'-v', '--version',
	action='version',
	version='%(prog)s 2.5'
	)
	# This portion of the code specifies the version of the program; currently 1.0
	# The user can call this flag ('-v') without specifying input and output files


args = parser.parse_args()
# this command allows the program to execute the arguments in the flags specified above


# Argparse references used:
# https://docs.python.org/3/library/argparse.html
# https://stackoverflow.com/questions/11154946/require-either-of-two-arguments-using-argparse
# https://stackoverflow.com/questions/14067553/restricting-values-of-command-line-options
# https://stackoverflow.com/questions/15753701/how-can-i-pass-a-list-as-a-command-line-argument-with-argparse
# https://www.geeksforgeeks.org/python/how-to-pass-a-list-as-a-command-line-argument-with-argparse/
# https://stackoverflow.com/questions/8107713/using-argparse-argumenterror-in-python
# https://thomas-cokelaer.info/blog/2014/03/python-argparse-issues-with-the-help-argument-typeerror-o-format-a-number-is-required-not-dict/


# Sanity Check Provided Arguments

# ensure input file names are provided
if args.run_all and not args.input_files:
	parser.error('-d is required when -a is set')
# ensure proper inputs for checkpoints
if args.checkpoint_num:
	# for checkpoints 2 & 3, input database file names are still required
	if (args.checkpoint_num == 2) and not args.input_files:
		parser.error('-d is required when running -c 2 or -c 3')
	# JSON files are required for checkpoints
	if args.checkpoint_num and not args.input_json:
		parser.error('-j is required when -c is set')
	# identifier is required for resuming runs from a checkpoint
	if args.checkpoint_num and not args.test_identifier:
		parser.error('-i is required when -c is set')

print("Sanity checks completed, proceeding to program execution.")
print("Note that this program does not check that the correct files were submitted according to the requirements of each argument. If this is the case, error messages may be less than helpful.")


#################################   Main Program   ######################################


# Part 1: Loading required modules & load global variables

#import necessary modules
import pandas as pd #facilitates manipulation of dataframes in Python
import json #allows import and export of data in JSON format
import difflib #compare and calculate differences between datasets
import statistics #simplify computation of basic statistics in Python
from tqdm import tqdm #enable progress bar generation
# ref: https://stackoverflow.com/questions/43259717/progress-bar-for-a-for-loop-in-python-script


# set up the identifier
if args.test_identifier:
	# if an identifier was provided
	# save it to a variable
	run_identifier = args.test_identifier
else:
	# if no identifier was provided, use datetime
	from datetime import datetime # access data from system regarding date & time
	# first determine date & time of query
	now = datetime.now()
	# and then save it to the identifier variable
	run_identifier = now.strftime("%d-%m-%Y--%H%M%S")

# set up program names for column headers
if args.program_names:
	# if a list of program names was provided
	# save it to a variable
	program_list = args.program_names
	# then extract the individual names to their own variables
	prog1_colname = program_list[0] + '_OG'
	prog2_colname = program_list[1] + '_OG'
	prog3_colname = program_list[2] + '_OG'
	prog4_colname = program_list[3] + '_OG'
else:
	# if no list of program names was provided
	# create default OG column name list
	program_list = ['Program_1', 'Program_2', 'Program_3', 'Program_4']
	# then extract the individual names to their own variables
	prog1_colname = program_list[0] + '_OG'
	prog2_colname = program_list[1] + '_OG'
	prog3_colname = program_list[2] + '_OG'
	prog4_colname = program_list[3] + '_OG'


# Part 2: Defining program functions

# function to import data into Pandas dataframes
def data_2_pandas(prog1_input, prog2_input, prog3_input, prog4_input):
	'''Import data into Pandas dataframes.'''
	# Parse input files as command-line arguments, and import the contents
	# of these dictionaries from JSON into Pandas dataframes. 
	# Checkpoint 1 is reached at the completion of this step.

	# import Program_1 dictionary into a Pandas dataframe
	# ref: https://www.geeksforgeeks.org/convert-json-to-dictionary-in-python/
	with open(prog1_input, "r") as json_file:
		# open the JSON file for reading
		# and extract its contents to a dictionary
		prog1_dict = json.load(json_file)
	# create a Pandas dataframe from the dictionary
	# ref: https://stackoverflow.com/questions/50751184/pandas-dataframe-from-dictionary-of-list-values
	prog1_df = pd.DataFrame([(key, var) for (key, L) in prog1_dict.items() for var in L], 
						 columns=[prog1_colname, 'Query'])
	# switch the column order
	# ref: https://stackoverflow.com/questions/25649429/how-to-swap-two-dataframe-columns
	columns_titles = ['Query', prog1_colname]
	prog1_df = prog1_df.reindex(columns=columns_titles)
	
	# import Program_2 dictionary into a Pandas dataframe
	with open(prog2_input, "r") as json_file:
		# open the JSON file for reading
		# and extract its contents to a dictionary
		prog2_dict = json.load(json_file)
	# create a Pandas dataframe from the dictionary
	prog2_df = pd.DataFrame([(key, var) for (key, L) in prog2_dict.items() for var in L], 
						 columns=[prog2_colname, 'Query'])
	# switch the column order
	columns_titles = ['Query', prog2_colname]
	prog2_df = prog2_df.reindex(columns=columns_titles)
	
	# import Program_3 dictionary into a Pandas dataframe
	with open(prog3_input, "r") as json_file:
		# open the JSON file for reading
		# and extract its contents to a dictionary
		prog3_dict = json.load(json_file)
	# create a Pandas dataframe from the dictionary
	prog3_df = pd.DataFrame([(key, var) for (key, L) in prog3_dict.items() for var in L], 
						 columns=[prog3_colname, 'Query'])
	# switch the column order
	columns_titles = ['Query', prog3_colname]
	prog3_df = prog3_df.reindex(columns=columns_titles)
	
	# import Program_4 dictionary into a Pandas dataframe
	with open(prog4_input, "r") as json_file:
		# open the JSON file for reading
		# and extract its contents to a dictionary
		prog4_dict = json.load(json_file)
	# create a Pandas dataframe from the dictionary
	prog4_df = pd.DataFrame([(key, var) for (key, L) in prog4_dict.items() for var in L], 
						 columns=[prog4_colname, 'Query'])
	# switch the column order
	columns_titles = ['Query', prog4_colname]
	prog4_df = prog4_df.reindex(columns=columns_titles)
	
	#Checkpoint 1 - let the user know program progress
	print("1st Checkpoint: All input datasets have been imported as Pandas dataframes.")


	#define objects to return
	return prog1_df, prog1_dict, prog2_df, prog2_dict, prog3_df, prog3_dict, prog4_df, prog4_dict


# function to create protein query ID to OG cluster assignments list dictionary
def create_prot_dict(prog1_df, prog2_df, prog3_df, prog4_df):
	'''Create protein query ID to OG cluster assignments list dictionary.'''
	# Create the protein query ID to OG cluster assignments list dictionary.
	# Checkpoint 2 is reached at the conclusion of this step, when this dictionary is exported in JSON format.

	#get lists of query proteins from the imported dataframes
	#Program_1
	prog1_queries = prog1_df['Query'].to_list()
	#Program_2
	prog2_queries = prog2_df['Query'].to_list()
	#Program_3
	prog3_queries = prog3_df['Query'].to_list()
	#Program_4
	prog4_queries = prog4_df['Query'].to_list()

	#concatenate the lists of queries
	prot_queries = prog1_queries + prog2_queries + prog3_queries + prog4_queries
	#turn the list of queries into a set to eliminate duplicates
	prot_queries = set(prot_queries)


	#create an empty dictionary to populate
	prot_dict = {}
	
	print("Commencing creation of protein ID to cluster ID dictionary.")
	
	for prot in tqdm(prot_queries):
		#iterate through the protein query IDs
		#initially, set the variables for all og categories as "-"
		#these will be overwritten in loops if the protein query was used in the given dataframe
		prog1_og = "-"
		prog2_og = "-"
		prog3_og = "-"
		prog4_og = "-"
		if prot in prog1_queries:
			#see if protein query ID is in the Program_1 dataframe
			prog1_og = prog1_df.loc[prog1_df['Query'] == prot, prog1_colname].iloc[0]
			#with .loc, find the location where the protein query ID is found in the 'Query' column
			#then extract the contents of that cell, as well as the cell in the same row that is in the 'prog1_OG' column
			#use slicing and .iloc to extract the contents of the 'Program_1_OG' column
			#and replace the contents of variable prog1_og ("-") with the OG ID
		if prot in prog2_queries:
			#see if protein query ID is in the Program_2 dataframe
			prog2_og = prog2_df.loc[prog2_df['Query'] == prot, prog2_colname].iloc[0]
			#with .loc, find the location where the protein query ID is found in the 'Query' column
			#then extract the contents of that cell, as well as the cell in the same row that is in the 'prog2_OG' column
			#use slicing and .iloc to extract the contents of the 'prog2_OG' column
			#and replace the contents of variable prog2_og ("-") with the OG ID
		if prot in prog3_queries:
			#see if protein query ID is in the Program_3 dataframe
			prog3_og = prog3_df.loc[prog3_df['Query'] == prot, prog3_colname].iloc[0]
			#with .loc, find the location where the protein query ID is found in the 'Query' column
			#then extract the contents of that cell, as well as the cell in the same row that is in the 'prog3_OG' column
			#use slicing and .iloc to extract the contents of the 'prog3_OG' column
			#and replace the contents of variable prog3_og ("-") with the OG ID
		if prot in prog4_queries:
			#see if protein query ID is in the Program_4 dataframe
			prog4_og = prog4_df.loc[prog4_df['Query'] == prot, prog4_colname].iloc[0]
			#with .loc, find the location where the protein query ID is found in the 'Query' column
			#then extract the contents of that cell, as well as the cell in the same row that is in the 'prog4_OG' column
			#use slicing and .iloc to extract the contents of the 'prog4_OG' column
			#and replace the contents of variable prog4_og ("-") with the OG ID
		prot_dict[prot] = [prog1_og, prog2_og, prog3_og, prog4_og]
		#populate the prot_dict dictionary with the protein query IDs as the keys
		#and a list of the Program_1, Program_2, Program_3 & Program_4 OGs assigned to that protein query as the values


	#Checkpoint 2 - let the user know program progress
	print("2nd Checkpoint: Protein query to OG match list dictionary has been successfully created. Printing dicitonary to file.")

	# create the output JSON file name
	output_json_name = 'prot_dict_' + run_identifier + '.json'
	#write out the filtered protein query database
	with open(output_json_name, 'w') as temp_file:
		#open the JSON outfile for writing
		#and write out the contents of the filt_prot_dict dictionary
		json.dump(prot_dict, temp_file)


	#define objects to return
	return prot_dict


# function to filter the protein query ID to OG assignment list dictionary to exclude
# protein queries that were only clustered by one program
def filter_prot_dict(prot_dict):
	'''Filter the protein query ID to OG assignment list dictionary to exclude 
		protein queries that were only clustered by one program.'''
	# Filter the protein query ID to OG assignment list dictionary to exclude
	# protein queries that were only clustered by one program. Checkpoint 3 is reached
	# at the conclusion of this step, when the new dictionary is exported in JSON format.

	#remove from the dictionary proteins that only occur in 1 program
	remove_list = []
	#create an empty list for the protein queries to be deleted

	for key in prot_dict.keys():
		#iterate over the keys of the prot_dict dictionary
		prot_OG_test = set(prot_dict[key])
		#save the value list as a set, eliminating duplicates
		if len(prot_OG_test) == 2:
			#if the length of the set is 2 (ie. the query protein is only clustered by one of the programs)
			#add the protein query key to the list of queries to remove
			remove_list.append(key)


	#create empty dictionary for first filtration - removal of proteins with only 1 OG match
	filt_prot_dict = {}

	for key in prot_dict.keys():
		#iterated through the prot_dict dictionary keys (ie. protein query IDs)
		if key not in remove_list:
			#for keys that aren't in the list of queries that need to be removed
			#save both the key and the value to the new filtered dictionary
			filt_prot_dict[key] = prot_dict[key]


	#Checkpoint 3 - let the user know program progress
	print("3rd Checkpoint: Protein queries only clustered by one program have been eliminated from the protein query to OG list dictionary.")
	print("Printing dictionary to file.")

	# create the output JSON file name
	output_json_name = 'filt_prot_dict_' + run_identifier + '.json'
	#write out the filtered protein query database
	with open(output_json_name, 'w') as temp_file:
		#open the JSON outfile for writing
		#and write out the contents of the filt_prot_dict dictionary
		json.dump(filt_prot_dict, temp_file)


	#define objects to return
	return filt_prot_dict


# function to create all-vs-all membership test & compile results
def membership_test(filt_prot_dict, prog1_dict, prog2_dict, prog3_dict, prog4_dict):
	'''Create all-vs-all membership test and compile results.'''
	# All-vs-all OG membership tests are completed, and a dictionary is created
	# containing the similarity scores of the clusters created by the programs.
	# Checkpoint 4 is reached at the conclusion of this step, when this comparison dictionary is exported in JSON format.

	#create empty dictionary for comparison data
	#dictionary format: comparison_dict[og_vs_pair] = list_Prog2_protein_group_comparison_values
	comparison_dict = {}
	# define the dictionary key names based on program names
	comparison_1_name = program_list[0] + '_vs_' + program_list[1]
	comparison_2_name = program_list[0] + '_vs_' + program_list[2]
	comparison_3_name = program_list[0] + '_vs_' + program_list[3]
	comparison_4_name = program_list[1] + '_vs_' + program_list[2]
	comparison_5_name = program_list[1] + '_vs_' + program_list[3]
	comparison_6_name = program_list[2] + '_vs_' + program_list[3]
	#define the keys of the dictionary with empty lists as associated values
	comparison_dict[comparison_1_name] = [] #Program_1 vs Program_2
	comparison_dict[comparison_2_name] = [] #Program_1 vs Program_3
	comparison_dict[comparison_3_name] = [] #Program_1 vs Program_4
	comparison_dict[comparison_4_name] = [] #Program_2 vs Program_3
	comparison_dict[comparison_5_name] = [] #Program_2 vs Program_4
	comparison_dict[comparison_6_name] = [] #Program_3 vs Program_4

	print("Commencing all-vs-all cluster membership comparisons.")

	for key in tqdm(filt_prot_dict.keys()):
		#iterate through the prot_dict dictionary using both keys and values
		#only calculate comparisons in places where both of the compared programs have results for that protein
		if filt_prot_dict[key][0] != "-" and filt_prot_dict[key][1] != "-":
			#comparing OGs where a protein query ID is found in both Program_1 and Program_2
			Prog1_OG = filt_prot_dict[key][0]
			#extract the OG that the protein query belongs to within the Program_1 results
			Prog1_OG_compare = prog1_dict[Prog1_OG]
			#use the extracted OG ID to query the Program_1 OG dictionary, to get the list of proteins in that OG
			Prog2_OG = filt_prot_dict[key][1]
			#extract the OG that the protein query belongs to within the Program_2 results
			Prog2_OG_compare = prog2_dict[Prog2_OG]
			#use the extracted OG ID to query the Program_2 OG dictionary, to get the list of proteins in that OG
			sm=difflib.SequenceMatcher(None,Prog1_OG_compare,Prog2_OG_compare)
			#compare the similarity of the two protein lists
			#and compute a numerical ratio of that similarity
			Prog1_vs_Prog2 = sm.ratio()
			#append the similarity ratio to the list associated with the 'Prog1_vs_Prog2' key in the comparison dictionary
			comparison_dict[comparison_1_name].append(Prog1_vs_Prog2)
		if filt_prot_dict[key][0] != "-" and filt_prot_dict[key][2] != "-":
			#comparing OGs where a protein query ID is found in both Program_1 and Prog3eqs2
			Prog1_OG = filt_prot_dict[key][0]
			#extract the OG that the protein query belongs to within the Program_1 results
			Prog1_OG_compare = prog1_dict[Prog1_OG]
			#use the extracted OG ID to query the Program_1 OG dictionary, to get the list of proteins in that OG
			Prog3_OG = filt_prot_dict[key][2]
			#extract the OG that the protein query belongs to within the Program_3 results
			Prog3_OG_compare = prog3_dict[Prog3_OG]
			#use the extracted OG ID to query the Program_3 OG dictionary, to get the list of proteins in that OG
			sm=difflib.SequenceMatcher(None,Prog1_OG_compare,Prog3_OG_compare)
			#compare the similarity of the two protein lists
			#and compute a numerical ratio of that similarity
			Prog1_vs_Prog3 = sm.ratio()
			#append the similarity ratio to the list associated with the 'Prog1_vs_Prog3' key in the comparison dictionary
			comparison_dict[comparison_2_name].append(Prog1_vs_Prog3)
		if filt_prot_dict[key][0] != "-" and filt_prot_dict[key][3] != "-":
			#comparing OGs where a protein query ID is found in both Program_1 and Program_4
			Prog1_OG = filt_prot_dict[key][0]
			#extract the OG that the protein query belongs to within the Program_1 results
			Prog1_OG_compare = prog1_dict[Prog1_OG]
			#use the extracted OG ID to query the Program_1 OG dictionary, to get the list of proteins in that OG
			Prog4_OG = filt_prot_dict[key][3]
			#extract the OG that the protein query belongs to within the Program_4 results
			Prog4_OG_compare = prog4_dict[Prog4_OG]
			#use the extracted OG ID to query the Program_4 OG dictionary, to get the list of proteins in that OG
			sm=difflib.SequenceMatcher(None,Prog1_OG_compare,Prog4_OG_compare)
			#compare the similarity of the two protein lists
			#and compute a numerical ratio of that similarity
			Prog1_vs_Prog4 = sm.ratio()
			#append the similarity ratio to the list associated with the 'Prog1_vs_Prog4' key in the comparison dictionary
			comparison_dict[comparison_3_name].append(Prog1_vs_Prog4)
		if filt_prot_dict[key][1] != "-" and filt_prot_dict[key][2] != "-":
			#comparing OGs where a protein query ID is found in both Program_2 and Prog3eqs2
			Prog3_OG = filt_prot_dict[key][2]
			#extract the OG that the protein query belongs to within the Program_3 results
			Prog3_OG_compare = prog3_dict[Prog3_OG]
			#use the extracted OG ID to query the Program_3 OG dictionary, to get the list of proteins in that OG
			Prog2_OG = filt_prot_dict[key][1]
			#extract the OG that the protein query belongs to within the Program_2 results
			Prog2_OG_compare = prog2_dict[Prog2_OG]
			#use the extracted OG ID to query the Program_2 OG dictionary, to get the list of proteins in that OG
			sm=difflib.SequenceMatcher(None,Prog3_OG_compare,Prog2_OG_compare)
			#compare the similarity of the two protein lists
			#and compute a numerical ratio of that similarity
			Prog2_vs_Prog3 = sm.ratio()
			#append the similarity ratio to the list associated with the 'Prog3_vs_Prog2' key in the comparison dictionary
			comparison_dict[comparison_4_name].append(Prog2_vs_Prog3)
		if filt_prot_dict[key][1] != "-" and filt_prot_dict[key][3] != "-":
			#comparing OGs where a protein query ID is found in both Program_2 and USEARCH
			Prog4_OG = filt_prot_dict[key][3]
			#extract the OG that the protein query belongs to within the Program_4 results
			Prog4_OG_compare = prog4_dict[Prog4_OG]
			#use the extracted OG ID to query the Program_4 OG dictionary, to get the list of proteins in that OG
			Prog2_OG = filt_prot_dict[key][1]
			#extract the OG that the protein query belongs to within the Program_2 results
			Prog2_OG_compare = prog2_dict[Prog2_OG]
			#use the extracted OG ID to query the Program_2 OG dictionary, to get the list of proteins in that OG
			sm=difflib.SequenceMatcher(None,Prog4_OG_compare,Prog2_OG_compare)
			#compare the similarity of the two protein lists
			#and compute a numerical ratio of that similarity
			Prog2_vs_Prog4 = sm.ratio()
			#append the similarity ratio to the list associated with the 'Prog4_vs_Prog2' key in the comparison dictionary
			comparison_dict[comparison_5_name].append(Prog2_vs_Prog4)
		if filt_prot_dict[key][2] != "-" and filt_prot_dict[key][3] != "-":
			#comparing OGs where a protein query ID is found in both Program_3 and USEARCH
			Prog3_OG = filt_prot_dict[key][2]
			#extract the OG that the protein query belongs to within the Program_3 results
			Prog3_OG_compare = prog3_dict[Prog3_OG]
			#use the extracted OG ID to query the Program_1 OG dictionary, to get the list of proteins in that OG
			Prog4_OG = filt_prot_dict[key][3]
			#extract the OG that the protein query belongs to within the Program_4 results
			Prog4_OG_compare = prog4_dict[Prog4_OG]
			#use the extracted OG ID to query the Program_4 OG dictionary, to get the list of proteins in that OG
			sm=difflib.SequenceMatcher(None,Prog3_OG_compare,Prog4_OG_compare)
			#compare the similarity of the two protein lists
			#and compute a numerical ratio of that similarity
			Prog3_vs_Prog4 = sm.ratio()
			#append the similarity ratio to the list associated with the 'Prog3_vs_Prog2' key in the comparison dictionary
			comparison_dict[comparison_6_name].append(Prog3_vs_Prog4)

	'''
	Some references for the list comparisons:

	Using difflib:
	https://docs.python.org/3/library/difflib.html
	https://stackoverflow.com/questions/6709693/calculating-the-similarity-of-two-lists

	Using cosine similarity:
	https://stackoverflow.com/questions/28819272/python-how-to-calculate-the-cosine-similarity-of-two-word-lists
	https://stackoverflow.com/questions/14720324/compute-the-similarity-between-two-lists
	https://en.wikipedia.org/wiki/Cosine_similarity

	Both of these methods yeild similar results, within 0.02 (compared two lists with different similarities).
	I chose to use difflib because of its far simpler implementation.

	'''

	'''
	A note on the scoring mechanism used above:

	The way the scoring is done, if clusters are particularly similar between two programs, with the same
	proteins appearing in the OGs of both, the OG's will in some sense be scored multiple times.

	I justify the choice to allow this because giving more weight to programs that are providing more
	similar clusters is useful when trying to quantify the quality of the orthologous clusters these
	programs produce. A cluster that is identified by multiple programs is more likely to be reliable; and
	programs that are identifying similar clusters are likely more adept at identifying OGs within
	these particularly divergent, unique organisms.

	'''

	#Checkpoint 4 - let the user know program progress
	print("4th Checkpoint: OG scoring comparison dictionary has been successfully created. Printing dictionary to file.")

	# create the output JSON file name
	output_json_name = 'compare_OG_dict_' + run_identifier + '.json'
	#write out the filtered protein query database
	with open(output_json_name, 'w') as temp_file:
		#open the JSON outfile for writing
		#and write out the contents of the filt_prot_dict dictionary
		json.dump(comparison_dict, temp_file)


	#define objects to return
	return comparison_dict


# function to average the scores in the comparison dictionary
def avg_membership_scores(comparison_dict):
	'''Calculate the mean average the scores in the comparison dictionary.'''
	# The scores inside of the comparison dictionary are averaged. Checkpoint 5 is
	# reached at the conclusion of this step, when this smaller dictionary is exported in JSON format.
	#create a new empty dictionary to hold the average scores
	og_score_dict = {}

	for key in comparison_dict.keys():
		#iterate over the comparison score dictionary keys
		og_score_avg = statistics.mean(comparison_dict[key])
		#compute the mean/average of the scores in each list in the comparison dictionary
		#and save the average score per commparison to a new dictionary, using the same keys
		og_score_dict[key] = og_score_avg


	#Checkpoint 5 - let the user know program progress
	print("5th Checkpoint: OG comparison scores have been successfully created. Printing dictionary to file.")

	# create the output JSON file name
	output_json_name = 'og_score_dict_' + run_identifier + '.json'
	#write out the filtered protein query database
	with open(output_json_name, 'w') as temp_file:
		#open the JSON outfile for writing
		#and write out the contents of the filt_prot_dict dictionary
		json.dump(og_score_dict, temp_file)


	#define objects to return
	return og_score_dict


# function to test which program overlaps meet the testing threshold value
def threshold_test(og_score_dict):
	'''Test which program overlaps meet the testing threshold percent value.'''
	# The threshold membership percentage value is used to filter the programs with
	# the most similar clusters, and a new dictionary is created to containing only
	# this data. Checkpoint 6 is reached at the conclusion of this step.

	#create new dictionary for OG average scores that meet the desired threshold value
	threshold_dict = {}

	#convert membership percentage to a decimal
	membership_decimal = float(args.membership_percent)/100

	for key in og_score_dict.keys():
		#iterate over the average scores dictionary's keys
		if og_score_dict[key] >= membership_decimal:
			#filter the comparisons that are similar enough to pass the given threshold value
			#those comparisons that pass, as well as the associated score average, should be copied to the threshold dictionary
			threshold_dict[key] = og_score_dict[key]


	#Checkpoint 6 - let the user know program progress
	print("6th Checkpoint: Orthologous clustering program evaluation based on user-supplied threshold of " +
		  str(args.membership_percent) + " has been completed. Printing results to output file.")

	#define objects to return
	return threshold_dict


# Part 3: Parse command-line arguments & execute program


#define the final output file with a pre-determined prefix & suffix, separated by the membership percent
membership_results = args.out_name + "__" + str(args.membership_percent) + ".txt"


# Part 3A: Complete execusion

if args.run_all:
	# if executing the entire program
	print("Running entire program, not from checkpoints.")
	
	# save the input file names to a list
	db_list = args.input_files
	
	#import the parsed clustering program results
	prog1_input = db_list[0]
	prog2_input = db_list[1]
	prog3_input = db_list[2]
	prog4_input = db_list[3]
	
	#now, use appropriate functions - in this case, all
	prog1_df, prog1_dict, prog2_df, prog2_dict, prog3_df, prog3_dict, prog4_df, prog4_dict = data_2_pandas(prog1_input, prog2_input, prog3_input, prog4_input)
	prot_dict = create_prot_dict(prog1_df, prog2_df, prog3_df, prog4_df)
	filt_prot_dict = filter_prot_dict(prot_dict)
	comparison_dict = membership_test(filt_prot_dict, prog1_dict, prog2_dict, prog3_dict, prog4_dict)
	og_score_dict = avg_membership_scores(comparison_dict)
	threshold_dict = threshold_test(og_score_dict)


# Part 3B: Checkpoint-based execution

if args.checkpoint_num:
	# if executing from a checkpoint
	# base program execution on provided checkpoint number
	if args.checkpoint_num == 2:
		# if executing from checkpoint 2
		print("Running program from Checkpoint 2.")

		# save the input file names to a list
		db_list = args.input_files
		
		#import the parsed clustering program results
		prog1_input = db_list[0]
		prog2_input = db_list[1]
		prog3_input = db_list[2]
		prog4_input = db_list[3]

		#open the primary JSON input file
		with open(args.input_json.name) as json_file:
			#open the JSON file containing the filt_prot_dict data
			#and load it as a dictionary
			prot_dict = json.load(json_file)
		#open the clustering program dictionaries
		with open(prog1_input) as prog1_in:
			#open the JSON file containing the filt_prot_dict data
			#and load it as a dictionary
			prog1_dict = json.load(prog1_in)
		with open(prog2_input) as prog2_in:
			#open the JSON file containing the prog2_dict data
			#and load it as a dictionary
			prog2_dict = json.load(prog2_in)
		with open(prog3_input) as prog3_in:
			#open the JSON file containing the prog3_dict data
			#and load it as a dictionary
			prog3_dict = json.load(prog3_in)
		with open(prog4_input) as prog4_in:
			#open the JSON file containing the prog4_dict data
			#and load it as a dictionary
			prog4_dict = json.load(prog4_in)

		#now, use appropriate functions - in this case, from filtration on
		filt_prot_dict = filter_prot_dict(prot_dict)
		comparison_dict = membership_test(filt_prot_dict, prog1_dict, prog2_dict, prog3_dict, prog4_dict)
		og_score_dict = avg_membership_scores(comparison_dict)
		threshold_dict = threshold_test(og_score_dict)

	if args.checkpoint_num == 3:
		# if executing from checkpoint 3
		print("Running program from Checkpoint 3.")

		# save the input file names to a list
		db_list = args.input_files
		
		#import the parsed clustering program results
		prog1_input = db_list[0]
		prog2_input = db_list[1]
		prog3_input = db_list[2]
		prog4_input = db_list[3]

		#open the primary JSON input file
		with open(args.input_json.name) as json_file:
			#open the JSON file containing the filt_prot_dict data
			#and load it as a dictionary
			filt_prot_dict = json.load(json_file)
		#open the clustering program dictionaries
		with open(prog1_input) as prog1_in:
			#open the JSON file containing the filt_prot_dict data
			#and load it as a dictionary
			prog1_dict = json.load(prog1_in)
		with open(prog2_input) as prog2_in:
			#open the JSON file containing the prog2_dict data
			#and load it as a dictionary
			prog2_dict = json.load(prog2_in)
		with open(prog3_input) as prog3_in:
			#open the JSON file containing the prog3_dict data
			#and load it as a dictionary
			prog3_dict = json.load(prog3_in)
		with open(prog4_input) as prog4_in:
			#open the JSON file containing the prog4_dict data
			#and load it as a dictionary
			prog4_dict = json.load(prog4_in)
	
		#now, use approtpriate functions - in this case, from membership test on
		comparison_dict = membership_test(filt_prot_dict, prog1_dict, prog2_dict, prog3_dict, prog4_dict)
		og_score_dict = avg_membership_scores(comparison_dict)
		threshold_dict = threshold_test(og_score_dict)

	if args.checkpoint_num == 4:
		# if executing from checkpoint 4
		print("Running program from Checkpoint 4.")
		
		with open(args.input_json.name) as json_file:
			#open the JSON file containing the filt_prot_dict data
			#and load it as a dictionary
			comparison_dict = json.load(json_file)
	
		#now, use appropriate functions - in this case, from averaging the membership scores on
		og_score_dict = avg_membership_scores(comparison_dict)
		threshold_dict = threshold_test(og_score_dict)

	if args.checkpoint_num == 5:
		# if executing from checkpoint 5
		print("Running program from Checkpoint 5.")

		with open(args.input_json.name) as json_file:
			#open the JSON file containing the filt_prot_dict data
			#and load it as a dictionary
			og_score_dict = json.load(json_file)

		#now, use appropriate functions - in this case, only the threshold dictionary creation
		threshold_dict = threshold_test(og_score_dict)


# Part 4: Writing of final outfile
# The contents of the dictionary created in the final step (ie. the final,
# membership threshold-filtered data) is written out to a text file.

print("Writing final output file.")

with open(membership_results, "w") as outfile:
	#open the results file for writing
	if bool(threshold_dict) == False:
		#test if the dictionary exists - high threshold values may yield an empty threshold_dict
		outfile.write("The given threshold value of " + str(args.membership_percent) + "% is too high. No OG comparisons met this criteria.")
	else: 
		#otherwise write an introductory line to the file
		outfile.write("The orthologous clustering similarity comparisons that met the desired threshold value of " + str(args.membership_percent) +
				   "% are listed below:" + "\n\n")
		for key in threshold_dict.keys():
			#iterate through the threshold dictionary by its keys
			key_clean = key.replace("_", " ")
			#create a clean version of the key with spaces instead of underscores
			#and write out to the results file the comparisons that met the required thresshold value
			outfile.write("For the " + key_clean + " comparison, the average score value is: " + str(threshold_dict[key]) + "\n")
