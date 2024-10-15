#!/bin/bash

# Define input and output files
input_file="Test_Vs.txt"
output_file="Test_Vs_cleaned.txt"

# Use awk to filter out rows where the third column is 'nan' and adjust the columns
awk '$3 != "nan" {print 1*$1, 1*$1, (-1)*$2, 1*$3}' "$input_file" > "$output_file"*

echo "Rows with 'nan' in column 3 have been removed and columns adjusted. Cleaned data saved in $output_file."

