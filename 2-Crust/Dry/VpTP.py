import numpy as np
import matplotlib.pyplot as plt

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
                        Vp = float(parts[5])
                        data.append((T, P, Vp))
                    except ValueError:
                        continue  # Skip lines with invalid data
    return np.array(data)

def plot(T, P, Vs, title, filename, cmap):
    fig, ax = plt.subplots(figsize=(7, 6))
    scatter = ax.scatter(T - 273.15, P * 1e-4, c=Vs, cmap=cmap)
    cbar = plt.colorbar(scatter, ax=ax, label='Vs (Km/s)')
    ax.set_title(title)
    ax.set_xlabel('T (°C)')
    ax.set_ylabel('P (GPa)')
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
T_ouc, P_ouc, Vp_ouc = data_ouc[:, 0], data_ouc[:, 1], data_ouc[:, 2]
T_cuc, P_cuc, Vp_cuc = data_cuc[:, 0], data_cuc[:, 1], data_cuc[:, 2]

# Plot Vp for CUC with 'plasma' colormap
plot(T_cuc, P_cuc, Vp_cuc, 'Vp_CUC', 'Vp_CUC.png', cmap_cuc)

# Plot Vp for OUC with 'inferno' colormap
plot(T_ouc, P_ouc, Vp_ouc, 'Vp_OUC', 'Vp_OUC.png', cmap_ouc)

# Calculate difference and plot with 'magma' colormap
# Create a dictionary for quick lookup
ouc_dict = {(t, p): vp for t, p, vp in zip(T_ouc, P_ouc, Vp_ouc)}
common_keys = {(t, p) for t, p in zip(T_cuc, P_cuc)}
Vp_diff = []

for t, p, vp_cuc in zip(T_cuc, P_cuc, Vp_cuc):
    if (t, p) in ouc_dict:
        vp_ouc = ouc_dict[(t, p)]
        Vp_diff.append((t, p, abs(vp_ouc - vp_cuc)))

# Convert difference data to numpy array
T_diff, P_diff, Vp_diff = np.array(Vp_diff).T

# Plot difference with 'magma' colormap
plot(T_diff, P_diff, Vp_diff, 'VP_relative', 'VP_relative.png', cmap_diff)

# Show all plots together
plt.show()
