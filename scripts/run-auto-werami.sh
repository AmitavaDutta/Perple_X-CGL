#!/bin/bash

# Prompt for project name
echo "Files in this directory:"
ls
read -p "Enter the project name (the name assigned in BUILD {PROJECT_NAME}.dat): " project_name
echo "Your entered project name is: $project_name"

# Check if the project file exists
if [ ! -f "${project_name}.dat" ]; then
    echo "Project file ${project_name}.dat not found. Exiting."
    exit 1
fi

# Prompt for the thermodynamic data file name
echo "Files in this directory:"
ls hp*.dat
read -p "Enter the thermodynamic data file name: " thermo_datafile

# Extract the composition data (lines 29-34)
comp_data=$(sed -n '29,34p' "${project_name}.dat" | awk '{print $1, $3}')

# Extract T and P ranges (lines 65-66)
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

# Create the input file for werami
input_file="input.txt"	    # For all the input and their functions check https://www.perplex.ethz.ch/perplex_66_seismic_velocity.html#top
{
    echo "$project_name"    # Project name
    echo "2"                # Operational mode: properties on a 2d grid
    echo "38"               # Select a property: multiple property output
    echo "1"                # Properties of the system
    echo "n"                # Include fluid in computation of aggregate (or modal) properties (y/n)? N for Dry
    echo "2"                # Property: Density (kg/m3)
    echo "13"               # Property: P-wave velocity (Vp, km/s)
    echo "14"               # Property: S-wave velocity (Vs, km/s)
    echo "3"                # Property: Specific heat capacity (J/K/m3)
    echo "19"               # Property: Heat Capacity (J/K/kg)
    echo "27"               # Property: P-wave velocity T derivative (km/s/K)
    echo "28"               # Property: S-wave velocity T derivative (km/s/K)
    echo "32"               # Property: P-wave velocity P derivative (km/s/bar)
    echo "33"               # Property: S-wave velocity P derivative (km/s/bar)
    echo "0"                # End property selection
    echo "n"                # Change default variable range: No
    echo "4"                # Grid resolution: 313 x 313 nodes
    echo "y"                # Continue with operation
    echo "0"                # End werami
} > "$input_file"

# Run WERAMI with the input file
werami < "$input_file"

# Final output file with the composition name
output_file="${project_name}-${composition_name}.tab"

# Add metadata information with extracted information to the output file
{
    echo "# File generated on: $current_date"
    echo "# Thermodynamic data file: $thermo_datafile"
    echo "# Project name: $project_name"
    echo "# Composition name: $composition_name"
    echo "# Composition elements: $comp_elements"
    echo "# Composition proportions:  $comp_amounts"
    echo "# T(K) range: $T_min $T_max"
    echo "# P(bar) range: $P_min $P_max"
} > "$output_file"

# Append the WERAMI output to the final file
cat "${project_name}_1.tab" >> "$output_file"

# Comment lines 9 to 21 in the final output file
sed -i '9,21s/^/# /' "$output_file"

# Clean up: remove the original WERAMI output file and input file
rm "${project_name}_1.tab" "$input_file"

echo "Output has been written to the file: ${output_file}"

