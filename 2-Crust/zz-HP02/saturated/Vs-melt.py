import numpy as np
import matplotlib.pyplot as plt
from matplotlib.tri import Triangulation

def data(file_path):
    # Read the data from the new file format
    data = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            parts = line.split()
            if len(parts) >= 8:  # Ensure enough columns are present
                try:
                    Z = float(parts[0])         # Depth (km)
                    rho = float(parts[1])       # Density (km/m^3)
                    Vs = abs(float(parts[3]))   # Shear wave velocity (Vs in km/s)
                    T = float(parts[4])         # Temperature (°C)
                    P = float(parts[5])         # Pressure (Pa)
                    if Vs > 0:  # Filter out zero or negative Vs values
                        data.append((Z, rho, Vs, T, P))
                except ValueError:
                    continue  # Skip lines with invalid data
    return np.array(data)

def plot(T, P, Vs, Z, title, filename, cmap):
    # Flatten arrays
    T_flat = T.flatten()
    P_flat = P.flatten()
    Vs_flat = Vs.flatten()
    Z_flat = Z.flatten()

    # Convert pressure from Pascals to GPa
    P_flat_GPa = P_flat * 1e-9  # Convert from Pa to GPa

    # Remove non-finite values
    mask = np.isfinite(T_flat) & np.isfinite(P_flat_GPa) & np.isfinite(Vs_flat) & np.isfinite(Z_flat)
    T_flat = T_flat[mask]
    P_flat_GPa = P_flat_GPa[mask]
    Vs_flat = Vs_flat[mask]
    Z_flat = Z_flat[mask]

    # Debugging output to check data
    print(f"Filtered data points: {T_flat.size}")
    if T_flat.size < 3:
        raise ValueError("Not enough valid data points for triangulation.")

    # Create the triangulation for T and P (in GPa)
    triang = Triangulation(T_flat, P_flat_GPa)

    # Plot using the triangulation
    fig, ax1 = plt.subplots(figsize=(10, 8))

    # Plot Vs on primary y-axis (P in GPa)
    contour = ax1.tricontourf(triang, Vs_flat, cmap=cmap)
    cbar = plt.colorbar(contour, ax=ax1, label='Vs (Km/s)', pad=0.1)
    ax1.set_title(title)
    ax1.set_xlabel('T (°C)')
    ax1.set_ylabel('P (GPa)')
    ax1.invert_yaxis()  # Invert y-axis for pressure

    # Create secondary y-axis for depth, based on Z
    ax2 = ax1.twinx()
    ax2.set_ylim(Z_flat.min(), Z_flat.max())
    ax2.set_ylabel('Depth (km)', color='k')
    ax2.tick_params(axis='y', labelcolor='k')
    ax2.invert_yaxis()  # Invert y-axis for pressure

    plt.tight_layout()
    plt.savefig(filename, format='png')  # Save plot as PNG

# Define color map for the plot
cmap_litmod = 'inferno'

# Read data from the new file
data_litmod = data('LitMod2D_2.0_Ref_Model_for_Syn_tomo.dat')

# Extract columns
Z_litmod, rho_litmod, Vs_litmod, T_litmod, P_litmod = data_litmod[:, 0], data_litmod[:, 1], data_litmod[:, 2], data_litmod[:, 3], data_litmod[:, 4]

# Plot Vs with P (in GPa) and Depth (in km) and T (°C)
plot(T_litmod, P_litmod, Vs_litmod, Z_litmod, 'Vs_LitMod', 'Vs_LitMod.png', cmap_litmod)

# Show the plot
plt.show()

