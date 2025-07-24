# OrthoBenchmark

![OrthoBenchmark logo](./img/Logo__OrthoBenchmark.png)

Author: Vi Varga

Last Update Date: 23.07.2025


## Description

A Python- and R-based toolbox for benchmarking orthologous clustering programs.


## Usage Instructions

The OrthoBenchmark toolbox should be utilized from the command line, ideally in a terminal with either the `conda` or `mamba` package manager installed. The scripts provided in the toolbox should be used in the following manner:

1. Run orthologous clustering using desired settings of four programs of interest.
2. Create a `conda`/`mamba` environment from the `env-orthobenchmark.yml` file located in the `Environment/` directory. All R and Python modules necessary to run the scripts included in this toolbox are included in the file.
3. Parse orthologous clustering results with a modified version of the `ortho_results_parser.py` script. As it stands, this script can be used to parse the results of CD-Hit, Diamond, MMseqs2 or USEARCH. The user should adapt it as needed to the format of the orthologous clustering results output by their programs of interest. Modifications to this file will not be tracked by git, but modifications to the identical `ortho_results_parser__EXAMPLE.py` script will.
4. Create an orthology database with the `create_ortho_db.py` script, which consolidates the data from the parsed orthologous clustering results into one large database.
5. Gather summary statistics from the clustering database with the `og_stats_benchmark.py` and `og_clust_counts.py` scripts.
6. Visualize descriptive statistics with the `visualize_desc_stats.R` script.
7. Test the significance of cluster size differences using the Anderson-Darling test with the `clust_size_signif.R` script.
8. Perform the cluster membership overlap testing with the `og_membership_test.py` script.
9. Visualize the results of the cluster membership overlap testing with the `visualize_cluster_overlap.R` script.

All of the above mentioned scripts are located in the `Scripts/` directory. An example workflow is provided below, but please see the scripts themselves for more specific input and usage instructions.

```bash
# parsing program results
python ../ortho_results_parser.py -i Concat_Pseudomonas_aeruginosa_CopyN_edit_90_200k.clstr -c -o CD-HIT_Pa_90_200k
python ../ortho_results_parser.py -i PA_diamond_clust_90_200k.txt -d -o Diamond_Pa_90_200k
python ../ortho_results_parser.py -i Pa_DB_90_200k_clu.tsv -m -o MMseqs2_Pa_90_200k
python ../ortho_results_parser.py -i Pa_CopyN_edit__clusters_90_200k.uc -u -o USEARCH_Pa_90_200k
# database creation
python ../create_ortho_db.py CD-HIT_Pa_90_200k_parsed_pivot.txt Diamond_Pa_90_200k_parsed_pivot.txt MMseqs2_Pa_90_200k_parsed_pivot.txt USEARCH_Pa_90_200k_parsed_pivot.txt
cp Orthology_Comparison_DB__24-07-2025--013753.txt Orthology_Comparison_DB_200k__24-07-2025--013753.txt
# statistics collection
python ../og_stats_benchmark.py CD-HIT_Pa_90_200k_parsed.json Diamond_Pa_90_200k_parsed.json MMseqs2_Pa_90_200k_parsed.json USEARCH_Pa_90_200k_parsed.json -NAME Size_200k
# boxplot data gathering by dataset size
python ../og_clust_counts.py Orthology_Comparison_DB_200k__24-07-2025--013753.txt
# created files Ortho_Comparison_Counts__24-07-2025--014037.txt & Ortho_Comparison_CountsClean__24-07-2025--014037.txt
cp Ortho_Comparison_Counts__24-07-2025--014037.txt Ortho_Comparison_Counts_200k__24-07-2025--014037.txt
cp Ortho_Comparison_CountsClean__24-07-2025--014037.txt Ortho_Comparison_CountsClean_200k__24-07-2025--014037.txt
# clustering overlap
python ../og_membership_test.py -a -i 90 -p 45 -o Pa_90_200k -d CD-HIT_Pa_90_200k_parsed.json,Diamond_Pa_90_200k_parsed.json,MMseqs2_Pa_90_200k_parsed.json,USEARCH_Pa_90_200k_parsed.json -n CDHIT,Diamond,MMseqs2,USEARCH
# visualizing descriptive statistics
Rscript ../../Scripts/visualize_desc_stats.R Size_200k__og_stats.txt Ortho_Comparison_CountsClean_200k__19-02-2025--142210.txt
# visualizing cluster membership overlap
Rscript ../../Scripts/visualize_cluster_overlap.R /mnt/c/Users/viragv/Documents/ChalmersG/Clustering/OrthoBenchmark/Manuscript/ParsedResults/ClusterOverlap/Size_200k/Percent_90/og_score_dict.json Comparison_200k_90
# Anderson-Darling
Rscript ../../Scripts/clust_size_signif.R Ortho_Comparison_CountsClean_200k__19-02-2025--142210.txt 90

```


## Publication & Citation

This GitHub repository is associated with an upcoming manuscript. Citation to be added upon publication.

Note that scripts in the `PublicationSupplement/` directory are the scripts used to parse data and create figures for the manuscript.
