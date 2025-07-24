#!/usr/bin/env Rscript

###
# 
# Title: visualize_cluster_overlap.R
# Date: 2025.03.10
# Author: Vi Varga
# 
# Description:
#   This program plots a heatmap showing the average degree of overlap in 
#     protein cluster membership between programs. 
#   This script is part of the OrthoBenchmark toolbox, and is written to 
#     visualize the data stored in the og_score_dict_[IDENTIFIER].json file 
#     produced by the og_membership_test.py script.
# 
# List of functions:
#   No functions are defined in this script.
# 
# List of standard and non-standard libraries used:
#   tidyverse
#   ggplot2
#   scales
#   svglite
#   shadowtext
#   viridis
#   jsonlite
# 
# Procedure:
#   1. Load necessary libraries & assign command-line arguments
#   2. Read data into R
#   3. Restructure dataframe
#   4. Plot the heatmap data
#   5. Print results to file
# 
# Known bugs and limitations:
#   - There is no quality-checking integrated into the code.
#   - The output file basename is user-defined, with no default.
#   - This script must be run from within the directory that the input JSON file is located in, 
#     or the absolute path to the input file must be provided.
# 
# Usage: 
#   Run this script from the command line in the directory containing the input files, 
#     like so: 
#       Rscript visualize_cluster_overlap.R infile_json out_base
#
#       Where: 
#         infile_json is the og_score_dict.json file produced by the og_membership_test.py script
#         and
#         out_base is the intended basename for the output file heatmap plot files
# 
# This script was written for R version 4.4.1 (2024-06-14 ucrt), in RStudio RStudio 2024.12.0+467 
#   "Kousa Dogwood".
# 
###


# Part 1: Load necessary libraries & assign command-line arguments

# setting up the workspace
# clear the environment
rm(list = ls())

# load libraries
library(tidyverse)
library(ggplot2)
library(scales)
library(svglite)
library(viridis)
library(jsonlite)
library(shadowtext)


# Parse command line arguments
# enable command line input
# ref: https://www.r-bloggers.com/2015/09/passing-arguments-to-an-r-script-from-command-lines/
args <- commandArgs(trailingOnly = TRUE)

# get the input file name
infile_json <- args[1]
# set the basename of the output file
out_base <- args[2]


# set the working directory to where the input file is located
setwd(dirname(infile_json))

# determine the output file name based on the user-provided basename
outfile_basename <- paste(out_base, "Visualized", sep = "__")


# Part 2: Read data into R

# open the JSON file
# ref: https://stackoverflow.com/questions/41000112/reading-a-json-file-in-r-lexical-error-invalid-char-in-json-text
comparison_dict <- fromJSON(readLines(infile_json, warn = F))
# import the comparison data into a dataframe
# ref: https://www.geeksforgeeks.org/convert-json-data-to-dataframe-in-r/
comparison_df <- as.data.frame(comparison_dict)


# Part 3: Restructure dataframe

# transpose the dataframe
# ref: https://stackoverflow.com/questions/28680994/converting-rows-into-columns-and-columns-into-rows-using-r
comparison_df <- t(comparison_df)
# move the comparisons out into the 1st column
# ref: https://stackoverflow.com/questions/36396911/r-move-index-column-to-first-column
comparison_df <- cbind(newColName = rownames(comparison_df), comparison_df)
rownames(comparison_df) <- 1:nrow(comparison_df)
# rename columns
# ref: https://www.datanovia.com/en/lessons/rename-data-frame-columns-in-r/
# ref: https://stackoverflow.com/questions/2288485/how-to-convert-a-data-frame-column-to-numeric-type
# ref: https://stackoverflow.com/questions/7145826/how-to-format-a-number-as-percentage-in-r
comparison_df <- comparison_df %>% 
  as_tibble() %>% 
  # begin with existing column renaming
  rename(
    Comparison_ID = newColName,
    Overlap = V2
  ) %>% 
  # ensure Overlap column is numeric
  transform(Overlap = as.numeric(Overlap)) %>% 
  # calculate percent from decimal values
  mutate(Percent = label_percent()(Overlap))


# add new columns for comparison info
comparison_df$Prog_1 <- ""
comparison_df$Prog_2 <- ""

# fill column contents by iterating over rows
# ref: https://stackoverflow.com/questions/1699046/for-each-row-in-an-r-dataframe
# ref: https://stackoverflow.com/questions/66534128/extracting-a-string-from-one-column-into-another-in-r
# ref: https://stackoverflow.com/questions/38291794/extract-string-before
for(i in 1:nrow(comparison_df)) {
  row <- comparison_df[i,]
  # save the row contents to a variable for easier manipulation
  program_1 <- strsplit(row$Comparison_ID, "[_]")[[1]][1]
  # get the first program in the row
  comparison_df[i,4] <- program_1
  # fill the program ID into the dataframe
  program_2 <- strsplit(row$Comparison_ID, "[_]")[[1]][3]
  # get the second program in the row
  # and fill the program into the dataframe
  comparison_df[i,5] <- program_2
}


# Part 4: Plot the heatmap data

# plot the heatmap
# ref: https://stackoverflow.com/questions/51697101/how-to-do-a-triangle-heatmap-in-r-using-ggplot2-reshape2-and-hmisc
# ref: https://cran.r-project.org/web/packages/viridis/vignettes/intro-to-viridis.html
# ref: https://r-charts.com/correlation/heat-map-ggplot2/
# ref: https://stackoverflow.com/questions/10686054/outlined-text-with-ggplot2
plot_heatmap <- ggplot(comparison_df, aes(x = Prog_1, y = Prog_2, fill = Overlap)) +
  geom_raster() +
  labs(title = "Cluster Membership Overlap",
       subtitle = "Average percent of overlapping protein members of orthologous clusters predicted by different programs",
       y = NULL, x = NULL) +
  scale_fill_viridis() +
  geom_shadowtext(aes(label = Percent)) +
  guides(fill = guide_colourbar(title = "Degree of \nOverlap")) + 
  theme(panel.grid = element_blank())


# Part 5: Print results to file

# Print results to files
# print plot to PDF file
pdf(paste(outfile_basename, "pdf", sep = "."))
plot_heatmap
dev.off()

# print plot to SVG file
svglite(paste(outfile_basename, "svg", sep = "."), width = 10, height = 8)
plot_heatmap
dev.off()
