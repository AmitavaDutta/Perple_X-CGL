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
cmap_pum = 'inferno'
cmap_dmm = 'magma'
cmap_diff = 'viridis'

# Read data from files
data_dmm = data('stx21-DMM.tab')
data_pum = data('stx21-PUM.tab')

# Extract columns
T_dmm, P_dmm, Vp_dmm = data_dmm[:, 0], data_dmm[:, 1], data_dmm[:, 2]
T_pum, P_pum, Vp_pum = data_pum[:, 0], data_pum[:, 1], data_pum[:, 2]

# Plot Vp for PUM with 'plasma' colormap
plot(T_pum, P_pum, Vp_pum, 'Vp_PUM', 'Vp_PUM.png', cmap_pum)

# Plot Vp for DMM with 'inferno' colormap
plot(T_dmm, P_dmm, Vp_dmm, 'Vp_DMM', 'Vp_DMM.png', cmap_dmm)

# Calculate difference and plot with 'magma' colormap
# Create a dictionary for quick lookup
dmm_dict = {(t, p): vp for t, p, vp in zip(T_dmm, P_dmm, Vp_dmm)}
common_keys = {(t, p) for t, p in zip(T_pum, P_pum)}
Vp_diff = []

for t, p, vp_pum in zip(T_pum, P_pum, Vp_pum):
    if (t, p) in dmm_dict:
        vp_dmm = dmm_dict[(t, p)]
        Vp_diff.append((t, p, abs(vp_dmm - vp_pum)))

# Convert difference data to numpy array
T_diff, P_diff, Vp_diff = np.array(Vp_diff).T

# Plot difference with 'magma' colormap
plot(T_diff, P_diff, Vp_diff, 'VP_relative', 'VP_relative.png', cmap_diff)

# Show all plots together
plt.show()
