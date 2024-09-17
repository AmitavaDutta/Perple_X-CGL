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
                        rho = float(parts[2])  # Assuming rho is in the 3rd column
                        Vs = abs(float(parts[6]))  # Ensure Vs is non-negative
                        if Vs > 0:  # Filter out zero values
                            data.append((T, P, rho, Vs))
                    except ValueError:
                        continue  # Skip lines with invalid data
    return np.array(data)

def plot(T, P, Vs, rho, title, filename, cmap):
    # Flatten arrays
    T_flat = T.flatten()
    P_flat = P.flatten()
    Vs_flat = Vs.flatten()
    rho_flat = rho.flatten()

    # Remove non-finite values
    mask = np.isfinite(T_flat) & np.isfinite(P_flat) & np.isfinite(Vs_flat) & np.isfinite(rho_flat)
    T_flat = T_flat[mask]
    P_flat = P_flat[mask]
    Vs_flat = Vs_flat[mask]
    rho_flat = rho_flat[mask]

    # Debugging output to check data
    print(f"Filtered data points: {T_flat.size}")
    if T_flat.size < 3:
        raise ValueError("Not enough valid data points for triangulation.")

    # Calculate depth inside the function
    def calculate_depth(P, rho, g=9.81):
        # Convert P from bar to Pa: 1 bar = 10^5 Pa
        P = P * 1e5  # Convert P to Pascals
        depth = np.zeros_like(P)
        for i in range(1, len(P)):
            # Calculate depth in meters, then convert to kilometers
            depth[i] = depth[i-1] + (P[i] - P[i-1]) / (rho[i] * g)
        return depth / 1000  # Convert depth to kilometers

    # Calculate depth
    depth = calculate_depth(P_flat, rho_flat)

    # Create the triangulation for T and P
    triang = Triangulation(T_flat - 273.15, P_flat * 1e-4)  # Convert T to °C and P to GPa

    # Plot using the triangulation
    fig, ax1 = plt.subplots(figsize=(10, 8))

    # Plot Vs on primary y-axis
    contour = ax1.tricontourf(triang, Vs_flat, cmap=cmap)
    cbar = plt.colorbar(contour, ax=ax1, label='Vs (Km/s)', pad=0.1)
    ax1.set_title(title)
    ax1.set_xlabel('T (°C)')
    ax1.set_ylabel('P (GPa)')
    ax1.set_ylim(0, 5)  # Setting pressure range (0-6 GPa)
    ax1.invert_yaxis()

    # Create secondary y-axis for depth, based on pressure
    ax2 = ax1.twinx()

    # Define a linear transformation from pressure to depth
    def pressure_to_depth(p, rho):
        g = 9.81  # m/s² (gravitational acceleration)
        return (p * 1e9) / (rho * g) / 1000  # Convert Pa to km

    # Apply the transformation for each pressure using the corresponding rho
    depth_limits = [pressure_to_depth(p, r) for p, r in zip(ax1.get_ylim(), [rho_flat[0], rho_flat[-1]])]

    # Set the limits for the secondary depth axis
    ax2.set_ylim(depth_limits)
    ax2.set_ylabel('Depth (km)', color='k')
    ax2.tick_params(axis='y', labelcolor='k')

    plt.tight_layout()
    plt.savefig(filename, format='png')  # Save plot as PNG

# Define color map for the plot
cmap_ouc = 'inferno'

# Read data from hp_1.tab
data_ouc = data('HP-OUC.tab')

# Extract columns
T_ouc, P_ouc, rho_ouc, Vs_ouc = data_ouc[:, 0], data_ouc[:, 1], data_ouc[:, 2], data_ouc[:, 3]

# Plot Vs for OUC with 'inferno' colormap
plot(T_ouc, P_ouc, Vs_ouc, rho_ouc, 'Vs_OUC', 'Vs_OUC.png', cmap_ouc)

# Show the plot
plt.show()
