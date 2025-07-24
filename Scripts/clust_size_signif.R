#!/usr/bin/env Rscript

###
# 
# Title: clust_size_signif.R
# Date: 2025.03.28
# Author: Vi Varga
# 
# Description:
#   This program performs an Anderson-Darling all-pairs comparison test on cluster
#     size data.
# 
# List of functions:
#   No functions are defined in this script.
# 
# List of standard and non-standard libraries used:
#   tidyverse
#   nortest
#   PMCMRplus
# 
# Procedure:
#   1. Load necessary libraries
#   2. Load data file into R
#   3. Perform test & write out results
# 
# Known bugs and limitations:
#   - There is no quality-checking integrated into the code.
#   - The output file name is not entirely user-defined, but is instead based on the input
#     file name.
# 
# Usage: 
#   Run this script from the command line in the directory containing the input files, 
#     like so: 
#       Rscript clust_size_signif.R infile_counts [col_substring]
#
#       Where: 
#         infile_counts is the cleaned counts file output by the og_clust_counts.py script
#         and
#         col_substring is an optional argument specifying a substring that should be contained
#           in the column headers that the user wishes to perform the test on
# 
# This script was written for R version 4.4.3 (2025-02-28 ucrt) -- "Trophy Case", in RStudio 2024.12.0+467 
#   "Kousa Dogwood".
# 
###


# Part 1: Load necessary libraries & assign command-line arguments

# setting up the workspace
# clear the environment
rm(list = ls())

# load libraries
library(tidyverse)
library(nortest)
library(PMCMRplus)


# Parse command line arguments
# enable command line input
# ref: https://www.r-bloggers.com/2015/09/passing-arguments-to-an-r-script-from-command-lines/
args <- commandArgs(trailingOnly = TRUE)

# get the input file name
infile_counts <- args[1]

# extract the actual file name from the full name that includes the path
infile_name_counts <- basename(infile_counts)
# set the working directory to where the input file is located
setwd(dirname(infile_name_counts))

# determine the output file name based on the input file name
outfile_basename <- paste((str_split(infile_name_counts, "__")[[1]][1]), "AndersonDarling", sep = "__")


# see if there user has a subset of columns to test
col_substring <- toString(args[2])
#col_substring <- toString(90)
#col_substring <- 'NA'
# check if the user has provided an column search substring
# if not, proceed with all-against-all column comparisons
# ref: https://stackoverflow.com/questions/7355187/error-in-if-while-condition-missing-value-where-true-false-needed
if (col_substring == 'NA') {
  writeLines("No column substring provided - will proceed with all-against-all Anderson-Darling comparisons.")
} else {
  writeLines(paste("Column substring provided - will proceed with Anderson-Darling comparisons of columns which include the string '", 
              col_substring, "' in the column name.", sep=""))
  # modify the outfile basename if a search substring has been provided
  outfile_basename <- paste(outfile_basename, col_substring, sep="_")
}


# Part 2: Import data table

# load the data into dataframe in R
counts_table <- read.delim(infile_counts, header = TRUE, sep = '\t')

# fix header structures
# ref: https://stackoverflow.com/questions/16041935/remove-dots-from-column-names
names(counts_table) <- gsub(".", "-", names(counts_table), fixed=TRUE)
names(counts_table) <- gsub(" counts", "", names(counts_table), fixed=TRUE)


# Part 3: Perform test & write out results

# create list of columns to perform comparison testing on
# if a search substring was specified, subset the larger database
# ref: https://stackoverflow.com/questions/18587334/subset-data-to-contain-only-columns-whose-names-match-a-condition
if (col_substring == 'NA') {
  search_cols <- as.list(colnames(counts_table))
} else {
  counts_subset <- counts_table[ , grepl(col_substring, names(counts_table))]
  search_cols <- as.list(colnames(counts_subset))
} 


# Perform the Anderson-Darling comparison tests & write out
# ref: https://rdrr.io/cran/PMCMRplus/man/adAllPairsTest.html
# ref: https://www.r-bloggers.com/2021/11/anderson-darling-test-in-r-quick-normality-check/
# ref: https://stackoverflow.com/questions/51368682/anderson-darling-normality-test-on-all-columns-of-a-dataframe
# ref: https://forum.posit.co/t/export-r-output-to-txt-file/60732

# open output file for test results
sink(file = paste(outfile_basename, "txt", sep="."))

# perform test on specified columns
# and write out rsults
# ref: https://stackoverflow.com/questions/4071586/printing-newlines-with-print-in-r
if (col_substring == 'NA') {
  writeLines("Anderson-Darling Test Results for: All columns")
  test_results <- adAllPairsTest(counts_table)
  print(test_results)
  writeLines("Summary:")
  print(summary(test_results))
  writeLines("Group Summary:")
  print(summaryGroup(test_results))
} else {
  writeLines(paste("Anderson-Darling Test Results for: Columns with substring ", col_substring, " in header", sep = ""))
  test_results <- adAllPairsTest(counts_subset)
  print(test_results)
  writeLines("Summary:")
  print(summary(test_results))
  writeLines("Group Summary:")
  print(summaryGroup(test_results))
} 

# close file to finish writing out
sink(file = NULL)
