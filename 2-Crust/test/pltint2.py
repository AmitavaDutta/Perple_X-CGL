import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

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
                    rho = float(parts[1])       # Density (kg/m^3)
                    Vs = abs(float(parts[3]))   # Shear wave velocity (Vs in km/s)
                    T = float(parts[4])         # Temperature (°C)
                    P = float(parts[5])         # Pressure (Pa)
                    if Vs > 0:
                        data.append((T, P, Vs, Z))
                except ValueError:
                    continue
    return np.array(data)

# Bilinear interpolation function
def bilinear_interpolate(T1, P1, Vs1, T2, P2):
    points = np.array([T1.flatten(), P1.flatten()]).T  # Temperature and Pressure grid points
    values = Vs1.flatten()  # Corresponding Vs values
    
    # Interpolate Vs at the T2, P2 points from LitMod
    Vs_interpolated = griddata(points, values, (T2, P2), method='linear')
    
    return Vs_interpolated

# Function to write the output data to a .dat file
def write_output_dat(T, P, Z, Vs_litmod, Vs_interpolated, filename):
    with open(filename, 'w') as f:
        f.write("# T(°C)    P(GPa)    Z(km)    Vs_LitMod(Km/s)    Vs_Interpolated(Km/s)    Vs_Difference(%)\n")
        for t, p, z, vs_litmod, vs_interp in zip(T, P, Z, Vs_litmod, Vs_interpolated):
            vs_diff = 100 * (vs_interp - vs_litmod) / vs_litmod
            f.write(f"{t:.6f}    {p:.6f}    {z:.6f}    {vs_litmod:.6f}    {vs_interp:.6f}    {vs_diff:.6f}\n")

# Plot all three Vs values
def plot_vs_comparison(T2, P2, Vs_litmod, Vs_interpolated, Z2, title, filename, cmap):
    # Create the plot
    fig, ax1 = plt.subplots(figsize=(10, 8))

    # Plot the original Vs data from LitMod
    sc1 = ax1.scatter(T2, P2, c=Vs_litmod, cmap='Reds', edgecolors='k', s=50, label='LitMod Vs (Km/s)', alpha=0.8)
    
    # Plot the interpolated Vs data
    sc2 = ax1.scatter(T2, P2, c=Vs_interpolated, cmap=cmap, edgecolors='k', s=50, label='Interpolated Vs (Km/s)', alpha=0.5)
    
    # Add color bar for the LitMod Vs
    cbar1 = plt.colorbar(sc1, ax=ax1, label='LitMod Vs (Km/s)', pad=0.1)

    # Add color bar for the interpolated Vs
    cbar2 = plt.colorbar(sc2, ax=ax1, label='Interpolated Vs (Km/s)', pad=0.1)

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

# Function to perform interpolation and plotting for a given data file
def process_data(data_file, output_file, plot_file):
    # Load Perple_X data (Data 1)
    data_perplex_cuc = data_perplex(data_file)
    T_perplex, P_perplex, rho_perplex, Vs_perplex = data_perplex_cuc[:, 0], data_perplex_cuc[:, 1], data_perplex_cuc[:, 2], data_perplex_cuc[:, 3]

    # Load LitMod data (Data 2)
    data_litmod2d = data_litmod('LitMod2D_2.0_Ref_Model_for_Syn_tomo.dat')
    T_litmod, P_litmod, Vs_litmod, Z_litmod = data_litmod2d[:, 0], data_litmod2d[:, 1], data_litmod2d[:, 2], data_litmod2d[:, 3]

    # Convert pressure from Pa to GPa for LitMod and Perple_X
    P_perplex_GPa = P_perplex * 1e-4  # Convert bar to GPa for Perple_X
    P_litmod_GPa = P_litmod * 1e-9    # Convert Pa to GPa for LitMod

    # Convert Perple_X temperature from K to °C
    T_perplex_C = T_perplex - 273.15

    # Perform bilinear interpolation of Vs at the LitMod (T, P) points
    Vs_interpolated = bilinear_interpolate(T_perplex_C, P_perplex_GPa, Vs_perplex, T_litmod, P_litmod_GPa)

    # Write the output to a .dat file including Vs from LitMod and difference
    write_output_dat(T_litmod, P_litmod_GPa, Z_litmod, Vs_litmod, Vs_interpolated, output_file)

    # Plot all three Vs data
    plot_vs_comparison(T_litmod, P_litmod_GPa, Vs_litmod, Vs_interpolated, Z_litmod, f'Vs Comparison: {data_file} vs LitMod', plot_file, cmap_interpolated)

# Process Data 1a (HP-sat-melt-CUC.tab)
process_data('HP-sat-melt-CUC.tab', 'Interpolated_Vs_HP_sat_melt.dat', 'Vs_HP_sat_melt_Comparison.png')

# Process Data 1b (HP-dry-CUC.tab)
process_data('HP-dry-CUC.tab', 'Interpolated_Vs_HP_dry.dat', 'Vs_HP_dry_Comparison.png')
