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
                        Vs = float(parts[6])
                        data.append((T, P, Vs))
                    except ValueError:
                        continue  # Skip lines with invalid data
    return np.array(data)

def plot(T, P, Vs, title, filename, cmap):
    # Reshape or ensure that T, P, and Vs are in a grid format before flattening
    T_flat = T.flatten()
    P_flat = P.flatten()
    Vs_flat = Vs.flatten()

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
    plt.savefig(filename, format='png')  # Change to .ps to save as .ps file

# Define color maps for each plot
cmap_cuc = 'inferno'
cmap_ouc = 'magma'
cmap_diff = 'viridis'

# Read data from files
data_ouc = data('HP-OUC.tab')
data_cuc = data('HP-CUC.tab')

# Extract columns
T_ouc, P_ouc, Vs_ouc = data_ouc[:, 0], data_ouc[:, 1], data_ouc[:, 2]
T_cuc, P_cuc, Vs_cuc = data_cuc[:, 0], data_cuc[:, 1], data_cuc[:, 2]

# Reshape your data into 2D grids if required (This assumes you know the shape)
# For demonstration purposes, let's assume the data has 100x100 grid points
n_points = int(np.sqrt(T_ouc.size))  # Assuming square grid for simplicity
T_ouc = T_ouc.reshape((n_points, n_points))
P_ouc = P_ouc.reshape((n_points, n_points))
Vs_ouc = Vs_ouc.reshape((n_points, n_points))

T_cuc = T_cuc.reshape((n_points, n_points))
P_cuc = P_cuc.reshape((n_points, n_points))
Vs_cuc = Vs_cuc.reshape((n_points, n_points))

# Plot Vs for CUC with 'inferno' colormap
plot(T_cuc, P_cuc, Vs_cuc, 'Vs_CUC', 'Vs_CUC.png', cmap_cuc)

# Plot Vs for OUC with 'magma' colormap
plot(T_ouc, P_ouc, Vs_ouc, 'Vs_OUC', 'Vs_OUC.png', cmap_ouc)

# Calculate difference and plot with 'viridis' colormap
# Create a dictionary for quick lookup
ouc_dict = {(t, p): vs for t, p, vs in zip(T_ouc.flatten(), P_ouc.flatten(), Vs_ouc.flatten())}
common_keys = {(t, p) for t, p in zip(T_cuc.flatten(), P_cuc.flatten())}
Vs_diff = []

for t, p, vs_cuc in zip(T_cuc.flatten(), P_cuc.flatten(), Vs_cuc.flatten()):
    if (t, p) in ouc_dict:
        vs_ouc = ouc_dict[(t, p)]
        Vs_diff.append((t, p, abs(vs_ouc - vs_cuc)))

# Convert difference data to numpy array
T_diff, P_diff, Vs_diff = np.array(Vs_diff).T

# Reshape difference data back to a grid
T_diff = T_diff.reshape((n_points, n_points))
P_diff = P_diff.reshape((n_points, n_points))
Vs_diff = Vs_diff.reshape((n_points, n_points))

# Plot difference with 'viridis' colormap
plot(T_diff, P_diff, Vs_diff, 'VP_relative', 'VP_relative.png', cmap_diff)

# Show all plots together
plt.show()
