#!/bin/bash

# File name
file="HP-CUC.tab"

# Check if the file exists
if [ ! -f "$file" ]; then
  echo "File $file not found!"
  exit 1
fi

# Find the highest and lowest values in column 6, ignoring the first 21 lines (comments)
highest_value=$(awk 'NR>21 {print $7}' "$file" | sort -n | tail -1)
lowest_value=$(awk 'NR>21 {print $7}' "$file" | sort -n | head -1)

# Find the highest and lowest values in column 5, ignoring the first 21 lines (comments)
highest_value2=$(awk 'NR>21 {print $6}' "$file" | sort -n | tail -1)
lowest_value2=$(awk 'NR>21 {print $6}' "$file" | sort -n | head -1)

# Output the highest and lowest values
echo "The highest value in column 6 is: $highest_value"
echo "The lowest value in column 6 is: $lowest_value"

echo "The highest value in column 5 is: $highest_value2"
echo "The lowest value in column 5 is: $lowest_value2"

