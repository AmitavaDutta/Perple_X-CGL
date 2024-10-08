#!/bin/bash

# Prompt the user for the project name
read -p "Enter a name for the project: " project_name
read -p "Enter a name of the Composition: " composition_name

# Create the input file for BUILD
input_file="build_input.txt"  # For all the input and their functions check https://www.perplex.ethz.ch/perplex_66_seismic_velocity.html#top

{
    echo "$project_name"                    # Project name
    echo "hp633ver.dat"                      # Thermodynamic data file
    echo "perplex_option.dat"               # Computational option file
    echo "n"                                # Transform components (Y/N)
    echo "2"                                # Computational mode (2d grid)
    echo "n"                                # Calculations with saturated fluids (Y/N)
    echo "n"  				    # Calculations with saturated components (Y/N)?
    echo "n"                                # Use chemical potentials, activities, fugacities (Y/N)
    echo "Na2O"                             # Thermodynamic component 1
    echo "MgO"                              # Thermodynamic component 2
    echo "Al2O3"                            # Thermodynamic component 3
    echo "SiO2"                             # Thermodynamic component 4
    echo "CaO"                              # Thermodynamic component 5
    echo "FeO"                              # Thermodynamic component 6
    echo ""                                 # End of thermodynamic components selection
    echo "n"                                # Make P dependent on T (Y/N)
    echo "2"                                # Select x-axis variable (2 for T(K))
    echo "273"                              # Minimum T(K)
    echo "1800"                             # Maximum T(K)
    echo "15"                               # Minimum P(bar)
    echo "150000"                           # Maximum P(bar)
    echo "y"                                # Specify component amounts by mass (Y/N)
    echo "3.27 2.50 15.40 66.60 3.59 5.00" # Mass amounts for NA2O, MGO, AL2O3, SIO2, CAO, FEO, H2O, CO2
    echo "n"                                # Output a print file (Y/N)
    echo "n"                                # Exclude pure/endmember phases (Y/N)
    echo "y"                                # Include solution models (Y/N)
    echo "solution_model.dat"               # Solution model file
   # Input solution models one by one
    echo "O(HP)"                            # Solution model: O
    echo "Pl(h)"                            # Solution model: Pl
    echo "Sp(HP)"                           # Solution model: Sp
    echo "Cpx(HP)"                          # Solution model: Cpx
    echo "Opx(HP)"                          # Solution model: Opx
    echo "Gt(HP)"                           # Solution model: Gt
    echo ""                                 # End of solution model selection
    echo "${project_name}-${composition_name}"  # Calculation title (same as project name)
} > "$input_file"


# Run BUILD using the generated input file
build < "$input_file"

# Check if BUILD ran successfully
if [ $? -eq 0 ]; then
    echo "BUILD ran successfully!"
else
    echo "BUILD encountered an error."
fi
