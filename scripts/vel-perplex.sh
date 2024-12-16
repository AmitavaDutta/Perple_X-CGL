#!/bin/bash

# Directory where the data files are stored
datafiles_dir="./datafiles"
# Define the composition files directory
comp_files="./comp-input"
# Define the output files directory
output_dir="./output-files"

# Check if the datafiles directory exists
if [ ! -d "$datafiles_dir" ]; then
    echo "Error: Directory $datafiles_dir does not exist."
    exit 1
fi

# Check if the output-files directory exists, create it if not
if [ ! -d "$output_dir" ]; then
    mkdir "$output_dir"
fi
# Prompt the user for the project name
read -p "Enter a name for the project (this name shall contain short info about themodynamic datafile and the composition): " project_name
echo "Your project is ${project_name}.dat"
echo -e "\n"
# Set a default value for the thermodynamic data file if the user presses enter
echo "Default Thermodynamic data file is hp02ver.dat"
echo "Some available examples of thermodynamic data files are: " #hp02ver.dat, hp633ver.dat, stx21ver.dat and stx24ver.dat
ls datafiles/hp*
ls datafiles/stx*
read -p "Enter the thermodynamic data file name (press Enter for default): " thermo_datafile
thermo_datafile=${thermo_datafile:-hp02ver.dat}

# Check if the thermodynamic data file exists in the /datafiles directory
if [ ! -f "$datafiles_dir/$thermo_datafile" ]; then
    echo "Error: Thermodynamic data file $thermo_datafile not found in $datafiles_dir."
    exit 1
fi
echo "Thermodynamic data file is $thermo_datafile"
echo -e "\n"
# Set a default value for the computational option file if the user presses enter
echo "Default Computational option file is perplex_option.dat"
echo "Some available examples of computational option files are: " #hp02ver.dat, hp633ver.dat, stx21ver.dat and stx24ver.dat
ls datafiles/perplex_option*
read -p "Enter the Computational option file name (press Enter for default): " optn_file
optn_file=${optn_file:-perplex_option.dat}

# Check if the computational option file exists in the /datafiles directory
if [ ! -f "$datafiles_dir/$optn_file" ]; then
    echo "Error: Computational option file $optn_file not found in $datafiles_dir."
    exit 1
fi
echo "Computational option file is $optn_file"
echo -e "\n"
# Set a default value for the solution model file if the user presses enter
echo "Default Solution model file is solution_model.dat"
echo "Available Solution model files are: " #solution_model.dat, stx21_solution_model.dat and stx24_solution_model.dat
ls datafiles/*solution*
read -p "Enter the solution model file name (press Enter for default): " soln_mod
soln_mod=${soln_mod:-solution_model.dat}

# Check if the solution model file exists in the /datafiles directory
if [ ! -f "$datafiles_dir/$soln_mod" ]; then
    echo "Error: Solution model file $soln_mod not found in $datafiles_dir."
    exit 1
fi
echo "Solution Model is $soln_mod"
echo -e "\n"

# Ask the user whether they want Crust or Mantle
read -p "Do you want to calculate for Crust or Mantle? " layer_type

# Set the comp_files directory based on the user's choice
if [ "$layer_type" == "Crust" ]; then
    comp_files="comp-input/Crust"
elif [ "$layer_type" == "Mantle" ]; then
    comp_files="comp-input/Mantle"
else
    echo "Invalid choice! Please select either Crust or Mantle."
    exit 1
fi

# Extract the prefix from the thermo_datafile
#thermo_datafile="hp02ver.dat" # Example; replace with actual input
prefix=$(echo "$thermo_datafile" | sed -E 's/[0-9]+.*//')

# Now, display available compositions based on the extracted prefix and layer
echo "Currently available Compositions for the selected thermodynamics data file are:"
ls "$comp_files/$prefix"

# Ask for the composition name
read -p "Enter a name of the Composition: " composition_name

# Construct the path to the composition file
composition_file="$comp_files/$prefix/$composition_name"

# Check if the composition file exists
if [ -f "$composition_file" ]; then
    echo "Composition file found: $composition_file"
else
    echo "Composition file not found: $composition_file"
fi


# Initialize arrays for components and mass amounts
components=()
mass_amounts=""

# Check if the composition file exists
if [[ -f "$composition_file" ]]; then
    # Read the components (all lines except the last one)
    while IFS= read -r line; do
        # Add line to components array until the last line
        components+=("$line")  # Add each line to the components array
    done < <(head -n -1 "$composition_file")  # Read all but the last line

    # Read the mass amounts from the last line
    read -r mass_amounts < <(tail -n 1 "$composition_file")

    # Check if mass amounts are not empty
    if [[ -z "$mass_amounts" ]]; then
        echo "Error: No mass amounts found in $composition_file."
        exit 1
    fi
else
    echo "Error: Composition file $composition_file not found in $comp_files."
    exit 1
fi

echo "Composition is $composition_name"

# Create a directory for the project
project_dir="./${project_name}"
if [ ! -d "$project_dir" ]; then
    mkdir "$project_dir"
fi

# Create the input file for BUILD
input_file="build_input.txt"  # For all the input and their functions check https://www.perplex.ethz.ch/perplex_66_seismic_velocity.html#top

{
    echo "$project_name"                       # Project name
    echo "$datafiles_dir/$thermo_datafile"     # Thermodynamic data file
    echo "$datafiles_dir/$optn_file"           # Computational option file
    echo "n"                                   # Transform components (Y/N)
    echo "2"                                   # Computational mode (2d grid)
    echo "n"                                   # Calculations with saturated fluids (Y/N)    
    echo "n"                                   # Calculations with saturated components (Y/N)
    echo "n"                                   # Use chemical potentials, activities, fugacities (Y/N)

    # Loop through the components array and echo each component
    for component in "${components[@]}"; do
        echo "$component"                      # Thermodynamic components
    done

    echo ""                                    # End of thermodynamic components selection
    echo "n"                                   # Make P dependent on T (Y/N)
    echo "2"                                   # Select x-axis variable (2 for T(K))
    echo "273"                                 # Minimum T(K)
    echo "1873"                                # Maximum T(K)
    echo "10"                                  # Minimum P(bar)
    echo "150000"                               # Maximum P(bar)
    echo "y"                                   # Specify component amounts by mass (Y/N)
    echo "$mass_amounts"                       # Mass amounts for components
    echo "y"                                   # Output a print file (Y/N)
    echo "y"                                   # Exclude pure/endmember phases (Y/N)
    echo "n"                                   # Do you want to be prompted for phases (Y/N)? 
    echo "q"	                       	       #  Enter names, left justified, 1 per line, press <enter> to finish:    For dry          
    echo "kalGL"	                       #  Enter names, left justified, 1 per line, press <enter> to finish:    For dry and avg cont crust
    echo "h2oL"	                       	       #  Enter names, left justified, 1 per line, press <enter> to finish:    For h           
    #echo "lc"	                       	       #  Enter names, left justified, 1 per line, press <enter> to finish:    For h + (and & arch) basalt
    echo "fo8L"	                       	       #  Enter names, left justified, 1 per line, press <enter> to finish:    For DMM & PUM & cont-crust
    echo "foL"	                       	       #  Enter names, left justified, 1 per line, press <enter> to finish:    For DMM  & PUM & cont-crust
    #echo "nasGL"	                       #  Enter names, left justified, 1 per line, press <enter> to finish:    For PUM
    echo "k2o"	                       	       #  Enter names, left justified, 1 per line, press <enter> to finish:    For cont-crust
    echo ""
    echo "y"                                   # Include solution models (Y/N)
    echo "$datafiles_dir/$soln_mod"            # Solution model file
    echo "O(HP)" 			       # Solution Model Phases
    echo "Sp(HP)"  			       # Solution Model Phases
    echo "Gt(HP)"  			       # Solution Model Phases
    echo "Opx(HP)"  			       # Solution Model Phases
    echo "Cpx(HP)" 			       # Solution Model Phases
    echo "Pl(h)" 			       # Solution Model Phases
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

# Create the input file for VERTEX
input_file="vertex_input.txt" 
{
    echo "$project_name"                     # Project name
} > "$input_file"
# Run VERTEX using the generated input file
vertex < "$input_file"

# Check if VERTEX ran successfully
if [ $? -eq 0 ]; then
    echo "VERTEX ran successfully!"
else
    echo "VERTEX encountered an error."
fi

# Extract the composition data (lines may  vary check the project file)
#comp_data=$(sed -n '29,36p' "${project_name}.dat" | awk '{print $1, $3}')

# Extract T and P ranges (lines may  vary check the project file)
#t_p_range=$(sed -n '68,69p' "${project_name}.dat" | awk '{print $1, $2}')
#t_p_range=$(sed -n '63,64p' "${project_name}.dat" | awk '{print $1, $2}')

# Find the line number for "begin thermodynamic component list"
lnb=$(grep -n "begin thermodynamic component list" "${project_name}.dat" | awk -F: '{print $1}')

# Find the line number for "end thermodynamic component list"
lne=$(grep -n "end thermodynamic component list" "${project_name}.dat" | awk -F: '{print $1}')

# Extract the composition data dynamically based on lnb and lne
comp_data=$(sed -n "$((lnb + 1)),$((lne - 1))p" "${project_name}.dat" | awk '{print $1, $3}')

# Find the line number for "end solution phase list"
ln=$(grep -n "end solution phase list" "${project_name}.dat" | awk -F: '{print $1}')

# Extract T and P ranges using the calculated line numbers
t_p_range=$(sed -n "$((ln + 2)),$((ln + 3))p" "${project_name}.dat" | awk '{print $1, $2}')


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
input_file="werami_input.txt"	    # For all the input and their functions check https://www.perplex.ethz.ch/perplex_66_seismic_velocity.html#top
{
    echo "$project_name"    # Project name
    echo "2"                # Operational mode: properties on a 2d grid
    echo "38"               # Select a property: multiple property output
    echo "1"                # Properties of the system
    echo "y"                # Include fluid in computation of aggregate (or modal) properties (y/n)?
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
    echo "4"                # Grid resolution: 
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
cp "$output_file" "$output_dir"

# Move all files with the ${project_name}.* pattern to the project directory
mv "${project_name}."* "$project_dir"
mv "${project_name}_"* "$project_dir"

# Clean up: remove temporary files
#rm "${project_name}_1.tab" "$werami_input" "$input_file"
rm build_input.txt vertex_input.txt werami_input.txt


echo "Output has been written to the file: ${output_file} and copied to $output_dir"

