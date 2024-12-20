#!/bin/bash

# Directory where the data files are stored
datafiles_dir="./datafiles"
# Define the output files directory
output_files="./output-files"

# Check if the datafiles directory exists
if [ ! -d "$datafiles_dir" ]; then
    echo "Error: Directory $datafiles_dir does not exist."
    exit 1
fi

# Check if the output-files directory exists, create it if not
if [ ! -d "$output_files" ]; then
    mkdir "$output_files"
fi
# Prompt the user for the project name
read -p "Enter a name for the project (this name shall contain short info about themodynamic datafile and the composition): " project_name
echo "Your project is ${project_name}.dat"
echo "\n"
# Set a default value for the thermodynamic data file if the user presses enter
echo "Default Thermodynamic data file is hp02ver.dat"
read -p "Enter the thermodynamic data file name (press Enter for default): " thermo_datafile
thermo_datafile=${thermo_datafile:-hp02ver.dat}

# Check if the thermodynamic data file exists in the /datafiles directory
if [ ! -f "$datafiles_dir/$thermo_datafile" ]; then
    echo "Error: Thermodynamic data file $thermo_datafile not found in $datafiles_dir."
    exit 1
fi
echo "Thermodynamic data file is $thermo_datafile"
echo "\n"
# Set a default value for the computational option file if the user presses enter
echo "Default Computational option file is perplex_option.dat"
read -p "Enter the Computational option file name (press Enter for default): " optn_file
optn_file=${optn_file:-perplex_option.dat}

# Check if the computational option file exists in the /datafiles directory
if [ ! -f "$datafiles_dir/$optn_file" ]; then
    echo "Error: Computational option file $optn_file not found in $datafiles_dir."
    exit 1
fi
echo "Computational option file is $optn_file"
echo "\n"
# Set a default value for the solution model file if the user presses enter
echo "Default Solution model file is solution_model.dat"
read -p "Enter the solution model file name (press Enter for default): " soln_mod
soln_mod=${soln_mod:-solution_model.dat}

# Check if the solution model file exists in the /datafiles directory
if [ ! -f "$datafiles_dir/$soln_mod" ]; then
    echo "Error: Solution model file $soln_mod not found in $datafiles_dir."
    exit 1
fi
echo "Solution Model is $soln_mod"
echo "\n"

#Composition Name
read -p "Enter a name of the Composition: " composition_name
echo "Composition is $composition_name"

# Create a directory for the project
project_dir="./${project_name}"
if [ ! -d "$project_dir" ]; then
    mkdir "$project_dir"
fi

# Create the input file for BUILD
input_file="build_input.txt"  # For all the input and their functions check https://www.perplex.ethz.ch/perplex_66_seismic_velocity.html#top

{
    echo "$project_name"                     # Project name
    echo "$datafiles_dir/$thermo_datafile"   # Thermodynamic data file
    echo "$datafiles_dir/$optn_file"         # Computational option file
    echo "n"                                   # Transform components (Y/N)
    echo "2"                                   # Computational mode (2d grid)
    echo "n"                                   # Calculations with saturated components (Y/N)
    echo "n"                                   # Use chemical potentials, activities, fugacities (Y/N)
    echo "NA2O"				     # Thermodynamic Component
    echo "MGO"				     # Thermodynamic Component
    echo "AL2O3"				     # Thermodynamic Component
    echo "SIO2"				     # Thermodynamic Component
    echo "CAO"				     # Thermodynamic Component
    echo "FEO"				     # Thermodynamic Component
    echo ""                                    # End of thermodynamic components selection
    echo "n"                                   # Make P dependent on T (Y/N)
    echo "2"                                   # Select x-axis variable (2 for T(K))
    echo "273"                                 # Minimum T(K)
    echo "2000"                                # Maximum T(K)
    echo "15"                                  # Minimum P(bar)
    echo "150000"                              # Maximum P(bar)
    echo "y"                                   # Specify component amounts by mass (Y/N)
    echo "3.21 8.73 15.48 48.3 9.52 8.87"      # Mass amounts for components
    echo "n"                                   # Output a print file (Y/N)
    echo "n"                                   # Exclude pure/endmember phases (Y/N)
    echo "y"                                   # Include solution models (Y/N)
    echo "$datafiles_dir/$soln_mod"           # Solution model file
    echo "O(HP)"                               # Solution model: O
    echo "Pl(h)"                               # Solution model: Pl
    echo "Sp(HP)"                              # Solution model: Sp
    echo "Cpx(HP)"                             # Solution model: Cpx
    echo "Opx(HP)"                             # Solution model: Opx
    echo "Gt(HP)"                              # Solution model: Gt
    echo ""                                    # End of solution model selection
    echo "${project_name}"                     # Calculation title (same as project name)
} > "$input_file"


# Run BUILD using the generated input file
build < "$input_file"

# Check if BUILD ran successfully
if [ $? -eq 0 ]; then
    echo "BUILD ran successfully!"
else
    echo "BUILD encountered an error."
fi

# Run BUILD using the generated input file
vertex < "$input_file"

# Check if BUILD ran successfully
if [ $? -eq 0 ]; then
    echo "VERTEX ran successfully!"
else
    echo "VERTEX encountered an error."
fi

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

# Create the input file for werami
input_file="input.txt"	    # For all the input and their functions check https://www.perplex.ethz.ch/perplex_66_seismic_velocity.html#top
{
    echo "$project_name"    # Project name
    echo "2"                # Operational mode: properties on a 2d grid
    echo "38"               # Select a property: multiple property output
    echo "1"                # Properties of the system
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
output_file="${project_name}.tab"

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

# Append WERAMI output to the final output file
cat "${project_name}_1.tab" >> "$output_file"

# Comment lines 9 to 21 in the final output file
sed -i '9,21s/^/# /' "$output_file"

# Copy the final output file to both the project directory and the output-files directory
cp "$output_file" "$project_dir"
cp "$output_file" "$output_files"

# Move all files with the ${project_name}.* pattern to the project directory
mv "${project_name}"* "$project_dir"

# Clean up: remove temporary files
rm "${project_name}_1.tab" "$werami_input" "$input_file"

echo "Output has been written to the file: ${output_file} and copied to $output_dir"

