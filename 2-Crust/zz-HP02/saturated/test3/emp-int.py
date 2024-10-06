import numpy as np
import matplotlib.pyplot as plt

# Function to read data from the Perple_X data file (HP-CUC.tab)
def data_perplex(file_path):
    data = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines[21:]:
            if not line.startswith('#'):
                parts = line.split()
                if len(parts) >= 7:
                    try:
                        T = float(parts[0])
                        P = float(parts[1])
                        rho = float(parts[2])
                        Vs = abs(float(parts[6]))
                        if Vs > 0:
                            data.append((T, P, rho, Vs))
                    except ValueError:
                        continue
    return np.array(data)

# Function to read data from the LitMod2D_2.0_Ref_Model_for_Syn_tomo.dat file
def data_litmod(file_path):
    data = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            parts = line.split()
            if len(parts) >= 8:
                try:
                    Z = float(parts[0])         # Depth (km)
                    rho = float(parts[1])       # Density (km/m^3)
                    Vs = abs(float(parts[3]))   # Shear wave velocity (Vs in km/s)
                    T = float(parts[4])         # Temperature (°C)
                    P = float(parts[5])         # Pressure (Pa)
                    if Vs > 0:
                        data.append((T, P, Vs, Z))
                except ValueError:
                    continue
    return np.array(data)

# Function for empirical bilinear interpolation
def empirical_bilinear_interpolate(T1, P1, Vs_grid, T2, P2):
    Vs_interpolated = np.full(T2.shape, np.nan)  # Prepare an array filled with NaN for the interpolated Vs values
    
    for i in range(len(T2)):
        t = T2[i]
        p = P2[i]

        # Find indices for the nearest surrounding points
        t_indices = np.searchsorted(T1, t)
        p_indices = np.searchsorted(P1, p)
        
        # Check if indices are valid and within bounds
        if t_indices == 0 or t_indices == len(T1) or p_indices == 0 or p_indices == len(P1):
            print(f"Warning: (T, P) = ({t}, {p}) is out of bounds for interpolation.")
            continue
        
        # Identify the four surrounding points
        T1_point = T1[t_indices - 1]
        T2_point = T1[t_indices]
        P1_point = P1[p_indices - 1]
        P2_point = P1[p_indices]

        Vs11 = Vs_grid[t_indices - 1, p_indices - 1]
        Vs12 = Vs_grid[t_indices - 1, p_indices]
        Vs21 = Vs_grid[t_indices, p_indices - 1]
        Vs22 = Vs_grid[t_indices, p_indices]

        # Calculate normalized distances
        x = (t - T1_point) / (T2_point - T1_point)
        y = (p - P1_point) / (P2_point - P1_point)

        # Bilinear interpolation formula
        Vs_interpolated[i] = (1 - x) * (1 - y) * Vs11 + \
                              x * (1 - y) * Vs21 + \
                              (1 - x) * y * Vs12 + \
                              x * y * Vs22

    return Vs_interpolated

# Function to write the output data to a .dat file
def write_output_dat(T, P, Z, Vs, filename):
    with open(filename, 'w') as f:
        f.write("# T(°C)    P(GPa)    Z(km)    Vs(Km/s)\n")
        for t, p, z, vs in zip(T, P, Z, Vs):
            if not np.isnan(vs):  # Only write valid Vs values
                f.write(f"{t:.6f}    {p:.6f}    {z:.6f}    {vs:.6f}\n")

# Plot interpolated Vs values from data 1 based on (T, P) from data 2
def plot_interpolated_vs(T2, P2, Vs_interpolated, Z2, title, filename, cmap):
    # Create the plot
    fig, ax1 = plt.subplots(figsize=(10, 8))

    # Plot the interpolated Vs data from Perple_X corresponding to LitMod (T, P)
    sc = ax1.scatter(T2, P2, c=Vs_interpolated, cmap=cmap, edgecolors='k', s=50, label='Interpolated Vs (Km/s)', alpha=0.8)
    cbar = plt.colorbar(sc, ax=ax1, label='Vs (Km/s)', pad=0.1)

    # Add labels and title
    ax1.set_title(title)
    ax1.set_xlabel('T (°C)')
    ax1.set_ylabel('P (GPa)')
    ax1.invert_yaxis()  # Invert y-axis for pressure

    # Create secondary y-axis for depth (LitMod data)
    ax2 = ax1.twinx()
    ax2.set_ylabel('Depth (km)', color='k')
    ax2.set_ylim(Z2.max(), Z2.min())  # Invert depth axis
    ax2.tick_params(axis='y', labelcolor='k')

    plt.tight_layout()
    plt.legend(loc='upper right')
    plt.savefig(filename, format='png')  # Save plot as PNG
    plt.show()

# Define color map
cmap_interpolated = 'cool'

# Load Perple_X data (HP-CUC.tab)
data_perplex_cuc = data_perplex('HP-CUC.tab')
T_perplex, P_perplex, rho_perplex, Vs_perplex = data_perplex_cuc[:, 0], data_perplex_cuc[:, 1], data_perplex_cuc[:, 2], data_perplex_cuc[:, 3]

# Create a grid for Vs values based on unique T and P
unique_T = np.unique(T_perplex)
unique_P = np.unique(P_perplex)
Vs_grid = np.full((len(unique_T), len(unique_P)), np.nan)  # Initialize with NaN

# Fill the grid with Vs values, only if they exist
for i, T in enumerate(unique_T):
    for j, P in enumerate(unique_P):
        matching_vs = Vs_perplex[(T_perplex == T) & (P_perplex == P)]
        if matching_vs.size > 0:
            Vs_grid[i, j] = matching_vs[0]  # Assign the first matching Vs value
        else:
            print(f"Warning: No Vs value found for T = {T:.2f} and P = {P:.2f}")

# Load LitMod data (LitMod2D_2.0_Ref_Model_for_Syn_tomo.dat)
data_litmod2d = data_litmod('LitMod2D_2.0_Ref_Model_for_Syn_tomo.dat')
T_litmod, P_litmod, Vs_litmod, Z_litmod = data_litmod2d[:, 0], data_litmod2d[:, 1], data_litmod2d[:, 2], data_litmod2d[:, 3]

# Convert pressure from Pa to GPa for LitMod and Perple_X
P_perplex_GPa = P_perplex * 1e-4  # Convert bar to GPa for Perple_X
P_litmod_GPa = P_litmod * 1e-9    # Convert Pa to GPa for LitMod

# Convert Perple_X temperature from K to °C
T_perplex_C = T_perplex - 273.15

# Perform empirical bilinear interpolation of Vs at the LitMod (T, P) points
Vs_interpolated = empirical_bilinear_interpolate(T_perplex_C, P_perplex_GPa, Vs_grid, T_litmod, P_litmod_GPa)

# Write the output to a .dat file
write_output_dat(T_litmod, P_litmod_GPa, Z_litmod, Vs_interpolated, 'Interpolated_Vs_LitMod.dat')

# Plot interpolated Vs data
plot_interpolated_vs(T_litmod, P_litmod_GPa, Vs_interpolated, Z_litmod, 'Interpolated Vs from Perple_X onto LitMod (T, P)', 'Interpolated_Vs_LitMod.png', cmap_interpolated)
