#!/bin/bash

# Prompt for project name
read -p "Enter the project name (the name assigned in BUILD): " project_name

# Check if the project file exists
if [ ! -f "${project_name}.dat" ]; then
    echo "Project file ${project_name}.dat not found. Exiting."
    exit 1
fi

# Prompt for the thermodynamic data file name
read -p "Enter the thermodynamic data file name: " thermo_datafile

# Extract the composition data (lines 29-34)
comp_data=$(sed -n '29,34p' "${project_name}.dat" | awk '{print $1, $3}')

# Extract T and P ranges (lines 57 and 58)
t_p_range=$(sed -n '65,66p' "${project_name}.dat" | awk '{print $1, $2}')

# Format composition data (columns 1 and 3)
comp_elements=$(echo "$comp_data" | awk '{printf "%s\t", $1}')  # Elements separated by tab
comp_amounts=$(echo "$comp_data" | awk '{printf "%.2f\t", $2}') # Amounts with two decimal places

# Format T(K) and P(bar) range
T_min=$(echo "$t_p_range" | awk 'NR==2 {print $2}')
T_max=$(echo "$t_p_range" | awk 'NR==1 {print $2}')
P_min=$(echo "$t_p_range" | awk 'NR==2 {print $1}')
P_max=$(echo "$t_p_range" | awk 'NR==1 {print $1}')

# Get the current date
current_date=$(date)

# Prompt for composition name
read -p "Enter the composition name: " composition_name

# Prompt for the phase name
#read -p "Enter the phase name: " phase_name

# Run WERAMI 
werami

# Final output file with the composition name
output_file="${project_name}-${composition_name}.tab" 							#-${phase_name

# Add metadata information with extracted information to the output file
{
    echo "# File generated on: $current_date"
    echo "# Thermodynamic data file: $thermo_datafile"
    echo "# Project name: $project_name"
    echo "# Composition name: $composition_name"
    echo "# Phase name: $phase_name" 
    echo "# Composition elements: $comp_elements"
    echo "# Composition proportions:  $comp_amounts"
    echo "# T(K) range: $T_min $T_max"
    echo "# P(bar) range: $P_min $P_max"
} > "$output_file"

# Append the WERAMI output to the final file
cat "${project_name}_1.tab" >> "$output_file"

# Comment lines 9 to 21 in the final output file
sed -i '9,21s/^/# /' "$output_file"

# Clean up: remove the original WERAMI output file
rm "${project_name}_1.tab"

echo "Output has been written to the file: ${output_file}"

