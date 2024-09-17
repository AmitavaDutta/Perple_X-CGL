import numpy as np
import matplotlib.pyplot as plt
from matplotlib.tri import Triangulation

def data(file_path):
    # Read data starting from line 23, ignoring comments
    data = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines[21:]:  # Start reading from line 23
            if not line.startswith('#'):  # Skip comment lines
                parts = line.split()
                if len(parts) >= 7:  # Ensure enough columns are present
                    try:
                        T = float(parts[0])
                        P = float(parts[1])
                        Vs = abs(float(parts[6]))  # Ensure Vs is non-negative
                        if Vs > 0:  # Filter out zero values
                            data.append((T, P, Vs))
                    except ValueError:
                        continue  # Skip lines with invalid data
    return np.array(data)

def plot(T, P, Vs, title, filename, cmap):
    # Flatten arrays
    T_flat = T.flatten()
    P_flat = P.flatten()
    Vs_flat = Vs.flatten()

    # Remove non-finite values
    mask = np.isfinite(T_flat) & np.isfinite(P_flat) & np.isfinite(Vs_flat)
    T_flat = T_flat[mask]
    P_flat = P_flat[mask]
    Vs_flat = Vs_flat[mask]

    # Debugging output to check data
    print(f"Filtered data points: {T_flat.size}")
    if T_flat.size < 3:
        raise ValueError("Not enough valid data points for triangulation.")

    # Create the triangulation for T and P
    triang = Triangulation(T_flat - 273.15, P_flat * 1e-4)  # Convert T to °C and P to GPa

    # Plot using the triangulation
    fig, ax = plt.subplots(figsize=(7, 6))
    contour = ax.tricontourf(triang, Vs_flat, cmap=cmap)
    cbar = plt.colorbar(contour, ax=ax, label='Vs (Km/s)')

    ax.set_title(title)
    ax.set_xlabel('T (°C)')
    ax.set_ylabel('P (GPa)')
    ax.set_ylim(0, 6)
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(filename, format='png')  # Save plot as PNG

# Define color map for the plot
cmap_cuc = 'inferno'

# Read data from hp_1.tab
data_cuc = data('hp_1.tab')

# Extract columns
T_cuc, P_cuc, Vs_cuc = data_cuc[:, 0], data_cuc[:, 1], data_cuc[:, 2]

# Plot Vs for CUC with 'inferno' colormap
plot(T_cuc, P_cuc, Vs_cuc, 'Vs_CUC', 'Vs_CUC.png', cmap_cuc)

# Show the plot
plt.show()
