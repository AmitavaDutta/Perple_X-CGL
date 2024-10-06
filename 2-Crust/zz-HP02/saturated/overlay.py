import numpy as np
import matplotlib.pyplot as plt
from matplotlib.tri import Triangulation

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

# Plot both datasets (Perple_X and LitMod) on the same Vs(T, P) space with depth
def plot_overlay_with_depth(T1, P1, Vs1, T2, P2, Vs2, Z2, title, filename, cmap1, cmap2):
    # Flatten arrays
    T1_flat = T1.flatten()  # Perple_X temperature (K)
    P1_flat = P1.flatten()  # Perple_X pressure (Pa)
    Vs1_flat = Vs1.flatten()

    T2_flat = T2.flatten()  # LitMod temperature (°C)
    P2_flat = P2.flatten()  # LitMod pressure (Pa -> GPa)
    Vs2_flat = Vs2.flatten()
    Z2_flat = Z2.flatten()  # Depth (km)

    # Convert pressure from Pa to GPa for LitMod and Perple_X
    P1_flat_GPa = P1_flat * 1e-4  # Convert bar to GPa for Perple_X
    P2_flat_GPa = P2_flat * 1e-9  # Convert Pa to GPa for LitMod

    # Convert Perple_X temperature from K to °C
    T1_flat_C = T1_flat - 273.15

    # Remove non-finite values
    mask1 = np.isfinite(T1_flat_C) & np.isfinite(P1_flat_GPa) & np.isfinite(Vs1_flat)
    mask2 = np.isfinite(T2_flat) & np.isfinite(P2_flat_GPa) & np.isfinite(Vs2_flat) & np.isfinite(Z2_flat)

    T1_flat_C = T1_flat_C[mask1]
    P1_flat_GPa = P1_flat_GPa[mask1]
    Vs1_flat = Vs1_flat[mask1]

    T2_flat = T2_flat[mask2]
    P2_flat_GPa = P2_flat_GPa[mask2]
    Vs2_flat = Vs2_flat[mask2]
    Z2_flat = Z2_flat[mask2]

    # Debugging output
    print(f"Filtered data points (Perple_X): {T1_flat_C.size}")
    print(f"Filtered data points (LitMod): {T2_flat.size}")
    
    if T1_flat_C.size < 3 or T2_flat.size < 3:
        raise ValueError("Not enough valid data points for triangulation.")

    # Create the triangulation for Perple_X data (background)
    triang1 = Triangulation(T1_flat_C, P1_flat_GPa)

    # Plot Perple_X data (as a background contour)
    fig, ax1 = plt.subplots(figsize=(10, 8))
    contour1 = ax1.tricontourf(triang1, Vs1_flat, cmap=cmap1, alpha=0.6)
    cbar1 = plt.colorbar(contour1, ax=ax1, label='Vs (Km/s) - Perple_X', pad=0.01)  # Adjust padding here

    # Plot LitMod data as overlay points
    sc = ax1.scatter(T2_flat, P2_flat_GPa, c=Vs2_flat, cmap=cmap2, edgecolors='k', s=50, label='LitMod Vs (Km/s)', alpha=0.8)
    cbar2 = plt.colorbar(sc, ax=ax1, label='Vs (Km/s) - LitMod', pad=0.1)  # Adjust padding here

    # Add labels and title
    ax1.set_title(title)
    ax1.set_xlabel('T (°C)')
    ax1.set_ylabel('P (GPa)')
    ax1.invert_yaxis()  # Invert y-axis for pressure

    # Create secondary y-axis for depth (LitMod data)
    ax2 = ax1.twinx()
    ax2.set_ylabel('Depth (km)', color='k')
    ax2.set_ylim(Z2_flat.max(), Z2_flat.min())  # Invert depth axis
    ax2.tick_params(axis='y', labelcolor='k')

    plt.tight_layout()
    plt.legend(loc='upper right')
    plt.savefig(filename, format='png')  # Save plot as PNG

# Define color maps
cmap_perplex = 'inferno'
cmap_litmod = 'cool'

# Load Perple_X data (HP-CUC.tab)
data_perplex_cuc = data_perplex('HP-CUC.tab')
T_perplex, P_perplex, rho_perplex, Vs_perplex = data_perplex_cuc[:, 0], data_perplex_cuc[:, 1], data_perplex_cuc[:, 2], data_perplex_cuc[:, 3]

# Load LitMod data (LitMod2D_2.0_Ref_Model_for_Syn_tomo.dat)
data_litmod2d = data_litmod('LitMod2D_2.0_Ref_Model_for_Syn_tomo.dat')
T_litmod, P_litmod, Vs_litmod, Z_litmod = data_litmod2d[:, 0], data_litmod2d[:, 1], data_litmod2d[:, 2], data_litmod2d[:, 3]

# Plot overlay with depth
plot_overlay_with_depth(T_perplex, P_perplex, Vs_perplex, T_litmod, P_litmod, Vs_litmod, Z_litmod, 'CCU Perple_X vs LitMod', 'CUC-PerpleX_LitMod.png', cmap_perplex, cmap_litmod)

# Show the plot
plt.show()

