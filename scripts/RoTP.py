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
                        Ro = float(parts[2])
                        data.append((T, P, Ro))
                    except ValueError:
                        continue  # Skip lines with invalid data
    return np.array(data)

def plot(T, P, Ro, title, filename, cmap):
    plt.figure(figsize=(7, 6))
    scatter = plt.scatter(T, P, c=Ro, cmap=cmap)
    plt.colorbar(scatter, label='Ro (Km/s)')
    plt.title(title)
    plt.xlabel('T (K)')
    plt.ylabel('P (bar)')
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
T_dmm, P_dmm, Ro_dmm = data_dmm[:, 0], data_dmm[:, 1], data_dmm[:, 2]
T_pum, P_pum, Ro_pum = data_pum[:, 0], data_pum[:, 1], data_pum[:, 2]

# Plot Ro for PUM with 'plasma' colormap
plot(T_pum, P_pum, Ro_pum, 'Ro_PUM', 'Ro_PUM.png', cmap_pum)

# Plot Ro for DMM with 'inferno' colormap
plot(T_dmm, P_dmm, Ro_dmm, 'Ro_DMM', 'Ro_DMM.png', cmap_dmm)

# Calculate difference and plot with 'magma' colormap
# Create a dictionary for quick lookup
dmm_dict = {(t, p): Ro for t, p, Ro in zip(T_dmm, P_dmm, Ro_dmm)}
common_keys = {(t, p) for t, p in zip(T_pum, P_pum)}
Ro_diff = []

for t, p, Ro_pum in zip(T_pum, P_pum, Ro_pum):
    if (t, p) in dmm_dict:
        Ro_dmm = dmm_dict[(t, p)]
        Ro_diff.append((t, p, abs(Ro_dmm - Ro_pum)))

# Convert difference data to numpy array
T_diff, P_diff, Ro_diff = np.array(Ro_diff).T

# Plot difference with 'magma' colormap
plot(T_diff, P_diff, Ro_diff, 'Ro_relative', 'Ro_relative.png', cmap_diff)

# Show all plots together
plt.show()
