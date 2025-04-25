from netpyne import specs, sim
from neuron import h, load_mechanisms
import os
import numpy as np

# Path to the directory containing mod files
mod_dir = os.path.join(os.path.dirname(__file__), 'required_files', 'neuronal_model', 'modfiles')
if os.path.exists(mod_dir):
    try:
        load_mechanisms(mod_dir)
        print(f"Successfully loaded mechanisms from {mod_dir}")
    except Exception as e:
        print(f"Failed to load mechanisms: {e}")
else:
    print(f"MOD files directory not found: {mod_dir}")
# Basic setup
netParams = specs.NetParams()
simConfig = specs.SimConfig()

netParams.cellParams['pyr'] = {}
netParams.cellParams['pyr']['secs'] = {}

netParams.cellParams['pyr']['secs']['soma'] = {}

netParams.cellParams['pyr']['secs']['soma']['geom'] = {
    "diam": 12,
    "L": 12,
    "Ra": 100.0,
    "cm": 1
    }

netParams.cellParams['pyr']['secs']['soma']['mechs'] = {"hh": {
    "gnabar": 0.15,
    "gkbar": 0.05,
    "gl": 0.0003,
    "el": -65
    }}

dend = {}
dend['geom'] = {"diam": 1.0,
                "L": 200.0,
                "Ra": 100.0,
                "cm": 1,
               }
dend['mechs'] = {"pas": 
                    {"g": 0.001,
                     "e": -70}
                }
dend['topol'] = {"parentSec": "soma",
                 "parentX": 1.0,
                 "childX": 0,
                }

netParams.cellParams['pyr']['secs']['dend'] = dend

'''
netParams.cellParams['pyr']['secs']['soma']['mechs']['extracellular'] = {}
netParams.cellParams['pyr']['secs']['dend']['mechs']['extracellular'] = {}
netParams.cellParams['pyr']['secs']['soma']['mechs']['efield'] = {}
netParams.cellParams['pyr']['secs']['dend']['mechs']['efield'] = {}
'''

# Replace the pointps section with this:
for sec in ['soma', 'dend']:
    # Add the extracellular field mechanism as a density mechanism
    netParams.cellParams['pyr']['secs'][sec]['mechs']['extracellular_field'] = {
        'amp': 1e-5,    
        'freq': 140,        # 140 Hz
        'phase': 0,         # 0 degrees
        'offset': 0         # No DC offset
    }

netParams.cellParams['pyr']['secs']['soma']['mechs']['km'] = {
    "gbar": 0.01,  # Conductance density
    "vhalfn": -10  # Half-activation voltage
}

# Excitatory pyramidal cell population
netParams.popParams['E'] = {
    "cellType": "pyr",
    "numCells": 20,
}

# Inhibitory parvalbumin cell population
netParams.cellParams['pv'] = {}
netParams.cellParams['pv']['secs'] = {}

# PV cell soma
netParams.cellParams['pv']['secs']['soma'] = {}
netParams.cellParams['pv']['secs']['soma']['geom'] = {
    "diam": 10,  # Smaller diameter than pyramidal cells
    "L": 10,    # Shorter length
    "Ra": 100.0,
    "cm": 1.0
}

# PV cells have different channel properties - faster-spiking
netParams.cellParams['pv']['secs']['soma']['mechs'] = {"hh": {
    "gnabar": 0.2,    # Higher sodium conductance for faster spikes
    "gkbar": 0.06,   # Higher potassium conductance
    "gl": 0.0003,
    "el": -70       # More hyperpolarized resting potential
}}

# PV cells have less spike frequency adaptation
netParams.cellParams['pv']['secs']['soma']['mechs']['km'] = {
    "gbar": 0.002,  # Lower adaptation conductance
    "vhalfn": -10
}

# PV cell dendrite (simpler than pyramidal cells)
pv_dend = {}
pv_dend['geom'] = {"diam": 0.8,
                "L": 100.0,  # Shorter dendrites
                "Ra": 100.0,
                "cm": 1
               }
pv_dend['mechs'] = {"pas": 
                    {"g": 0.001,
                     "e": -70}
                }

# Add extracellular field to PV cells too
for sec in ['soma', 'dend']:
    if sec == 'dend':
        netParams.cellParams['pv']['secs'][sec] = pv_dend
    netParams.cellParams['pv']['secs'][sec]['mechs']['extracellular_field'] = {
        'amp': 1e-5,        # Same as pyramidal cells
        'freq': 140,        # 140 Hz
        'phase': 0,
        'offset': 0
    }

# Add PV population
netParams.popParams['I'] = {
    "cellType": "pv",
    "numCells": 20,
}

# Excitatory synapse mechanism
netParams.synMechParams['exc'] = {
    "mod": "Exp2Syn",
    "tau1": 0.1,
    "tau2": 1.0,
    "e": 0  # Reversal potential for excitatory synapses
}

# Inhibitory synapse mechanism
netParams.synMechParams['inh'] = {
    "mod": "Exp2Syn",
    "tau1": 0.5,  # Faster rise for inhibitory synapses
    "tau2": 5.0,  # Longer decay for inhibitory synapses
    "e": -80    # Negative reversal potential for inhibitory synapses
}

# E->E: Pyramidal to pyramidal connections
netParams.connParams['E->E'] = {
    "preConds": {"pop": "E"},
    "postConds": {"pop": "E"},
    "weight": 0.01,
    "probability": 0.2,
    "delay": 5.0,
    "synMech": "exc",
    "sec": "dend",
    "loc": 1.0,
}

# E->I: Pyramidal to PV connections
netParams.connParams['E->I'] = {
    "preConds": {"pop": "E"},
    "postConds": {"pop": "I"},
    "weight": 0.01,  
    "probability": 0.2,  
    "delay": 2.0,  # Faster transmission
    "synMech": "exc",
    "sec": "dend",
    "loc": 0.5,
}

# I->E: PV to pyramidal connections (inhibitory)
netParams.connParams['I->E'] = {
    "preConds": {"pop": "I"},
    "postConds": {"pop": "E"},
    "weight": 0.016,
    "probability": 0.2,
    "delay": 2.0,
    "synMech": "inh",  
    "sec": "soma",  
    "loc": 0.5,
}

# I->I: PV to PV connections (inhibitory)
netParams.connParams['I->I'] = {
    "preConds": {"pop": "I"},
    "postConds": {"pop": "I"},
    "weight": 0.01,
    "probability": 0.2,
    "delay": 2.0,
    "synMech": "inh",
    "sec": "soma",
    "loc": 0.5,
}


netParams.stimSourceParams['IClamp1'] = {
    "type": "IClamp",
    "dur": 2000,
    "del": 20,
    "amp": 0.2,  #nA
}

netParams.stimSourceParams['IClamp1PV'] = {
    "type": "IClamp",
    "dur": 2000,
    "del": 20,
    "amp": 0.2,  #nA
}

# Apply IClamp to 5 pyramidal cells
netParams.stimTargetParams['IClamp1->E_subset'] = {
    "source": "IClamp1",
    "conds": {"pop": "E", "cellList": [0, 5, 10, 15, 19]},  # Target 5 pyramidal cells
    "sec": "soma",
    "loc": 0.5,
}

# Apply IClamp to 5 PV cells as well
netParams.stimTargetParams['IClamp1PV->I_subset'] = {
    "source": "IClamp1PV",
    "conds": {"pop": "I", "cellList": [0, 5, 10, 15, 19]},  # Target 5 PV cells
    "sec": "soma",
    "loc": 0.5,
}


# Add small background noise to pyramidal cells
for i in range(20):
    netParams.stimSourceParams[f'Noise_E_{i}'] = {
        "type": "IClamp",
        "delay": 0,
        "dur": 2000,
        "amp": 'uniform(0.1,0.15)'  # Reduced background noise
    }
    netParams.stimTargetParams[f'Noise_E_{i}->cell{i}'] = {
        "source": f'Noise_E_{i}',
        "conds": {"pop": "E", "cellList": [i]},
        "sec": "soma",
        "loc": 0.5
    }


# Add noise current to PV cells (higher amplitude for faster firing)
for i in range(20):
    netParams.stimSourceParams[f'Noise_I_{i}'] = {
        "type": "IClamp",
        "delay": 0,
        "dur": 2000,
        "amp": 'uniform(0.1,0.2)'  # Slightly higher current for PV cells
    }
    netParams.stimTargetParams[f'Noise_I_{i}->cell{i}'] = {
        "source": f'Noise_I_{i}',
        "conds": {"pop": "I", "cellList": [i]},
        "sec": "soma",
        "loc": 0.5
    }


# Simulation configuration
simConfig.filename = "netpyne_tut1"
simConfig.duration = 2000
simConfig.dt = .1

# Set up recording - note the use of soma_0 for proper recording as per memory
simConfig.recordCells = list(range(40))  # Record from all 40 cells (20 pyr + 20 PV)
simConfig.recordStep = 0.1  # Record at 0.1 ms intervals
simConfig.recordTraces = {
    'V_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'v'},  # Using soma_0 as noted in memory
    'V_dend': {'sec': 'dend', 'loc': 1.0, 'var': 'v'}
}
simConfig.recordStim = True  # Added as per memory
simConfig.recordSpikes = True

# First run simulation
sim.createSimulateAnalyze(netParams=netParams, simConfig=simConfig)

# Add this after your simulation ends
def analyze_spike_field_entrainment(sim_data, field_freq, cell_type=None, plot=True, save=True):
    """
    Analyze spike-field entrainment and create polar plots
    
    Parameters:
    -----------
    sim_data : dict
        The simulation data dictionary (sim.allSimData)
    field_freq : float
        Frequency of the field in Hz
    cell_type : str or None
        If 'pyr', analyze only pyramidal cells (0-39)
        If 'pv', analyze only PV cells (40-79)
        If None, analyze all cells
    plot : bool
        Whether to display the plot
    save : bool
        Whether to save the plot
    """
    """
    Analyze spike-field entrainment and create polar plots
    
    Parameters:
    -----------
    sim_data : dict
        The simulation data dictionary (sim.allSimData)
    field_freq : float
        Frequency of the field in Hz
    plot : bool
        Whether to display the plot
    save : bool
        Whether to save the plot
    """
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec
    import os
    
    # Check for spike data in NetPyNE's typical format (spkt/spkid)
    if 'spkt' in sim_data and 'spkid' in sim_data:
        # Extract spike times and cell IDs from the spkt/spkid format
        spk_times = np.array(sim_data['spkt'])
        spk_cells = np.array(sim_data['spkid'])
        
        # Filter by cell type if specified
        if cell_type == 'pyr':
            # Pyramidal cells are 0-19
            mask = spk_cells < 20
            spk_times = spk_times[mask]
            spk_cells = spk_cells[mask]
            cell_type_str = "Pyramidal Cells"
        elif cell_type == 'pv':
            # PV cells are 20-39
            mask = spk_cells >= 20
            spk_times = spk_times[mask]
            spk_cells = spk_cells[mask]
            cell_type_str = "Parvalbumin Cells"
        else:
            cell_type_str = "All Cells"
            
        print(f"Found {len(spk_times)} spikes in {cell_type_str}")
    else:
        print("No spike data found in simulation results")
        return
    
    if len(spk_times) == 0:
        print("No spikes detected in the simulation")
        return
    
    # Calculate field period in ms
    field_period = 1000/field_freq
    
    # For each spike, calculate its phase in the oscillation cycle (0-360 degrees)
    spike_phases = np.mod(spk_times, field_period) / field_period * 360
    
    # Convert to radians for polar plotting
    spike_phases_rad = spike_phases * np.pi / 180
    
    # Calculate mean resultant vector (measure of phase concentration)
    # This is done by converting phases to unit vectors and taking the mean
    mean_vec_x = np.mean(np.cos(spike_phases_rad))
    mean_vec_y = np.mean(np.sin(spike_phases_rad))
    
    # Phase locking value (PLV) - magnitude of the mean vector (0-1)
    plv = np.sqrt(mean_vec_x**2 + mean_vec_y**2)
    
    # Mean phase angle
    mean_phase = np.arctan2(mean_vec_y, mean_vec_x) * 180 / np.pi
    if mean_phase < 0:
        mean_phase += 360
    
    # Create figure for plotting
    fig = plt.figure(figsize=(12, 10))
    gs = GridSpec(2, 2, height_ratios=[1, 1])
    
    # Polar histogram
    ax1 = fig.add_subplot(gs[0, 0], projection='polar')
    bins = np.linspace(0, 2*np.pi, 37)  # 36 bins (10 degrees each)
    counts, edges = np.histogram(spike_phases_rad, bins=bins)
    centers = (edges[:-1] + edges[1:]) / 2
    
    # Normalize by max count for better visualization
    counts = counts / counts.max() if counts.max() > 0 else counts
    
    bars = ax1.bar(centers, counts, width=bins[1]-bins[0], bottom=0.0, alpha=0.8)
    
    # Add a vector showing the mean direction and magnitude
    ax1.annotate("", xytext=(0, 0), xy=(mean_phase*np.pi/180, plv), 
                arrowprops=dict(facecolor='red', width=2, alpha=0.8))
    
    ax1.set_title(f'Spike Phase Distribution (N={len(spike_phases)})\nPLV={plv:.3f}, Mean Phase={mean_phase:.1f}°')
    
    # Linear histogram
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.hist(spike_phases, bins=36, alpha=0.7, color='skyblue', edgecolor='black')
    ax2.set_xlabel('Phase (degrees)')
    ax2.set_ylabel('Spike Count')
    ax2.set_title('Linear Phase Histogram')
    ax2.set_xlim(0, 360)
    
    # Spike phase by time
    ax3 = fig.add_subplot(gs[1, 0])
    sc = ax3.scatter(spk_times, spike_phases, s=20, alpha=0.5, c=spk_cells, cmap='viridis')
    ax3.set_xlabel('Time (ms)')
    ax3.set_ylabel('Phase (degrees)')
    ax3.set_title('Spike Phases Over Time')
    ax3.set_ylim(0, 360)
    plt.colorbar(sc, ax=ax3, label='Cell ID')
    
    # Spike raster with phase coding
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.scatter(spk_times, spk_cells, c=spike_phases, s=20, alpha=0.8, cmap='hsv')
    ax4.set_xlabel('Time (ms)')
    ax4.set_ylabel('Cell ID')
    ax4.set_title('Spike Raster (color=phase)')
    
    plt.tight_layout()
    
    if save:
        # Create directory if it doesn't exist
        save_dir = 'figures'
        os.makedirs(save_dir, exist_ok=True)
        
        # Use different filenames based on cell type
        if cell_type == 'pyr':
            filename = 'pyr_spike_field_entrainment.png'
        elif cell_type == 'pv':
            filename = 'pv_spike_field_entrainment.png'
        else:
            filename = 'all_spike_field_entrainment.png'
            
        plt.savefig(os.path.join(save_dir, filename), dpi=300)
    
    if plot:
        plt.show()
    
    return {
        'spike_phases': spike_phases,
        'plv': plv,
        'mean_phase': mean_phase,
        'n_spikes': len(spike_phases)
    }

# Create output directory if it doesn't exist
figures_dir = os.path.abspath('./figures')
if not os.path.exists(figures_dir):
    os.makedirs(figures_dir)
print(f"\nSaving plots to: {figures_dir}")

try:
    import matplotlib.pyplot as plt
    
    print("\nGenerating plots...")
    
    # First verify we have simulation data
    #if not hasattr(sim, 'allSimData'):
        #print("Error: No simulation data available!")
        #return
    
    # Verify we have the required data
    print("\nAvailable data keys:", list(sim.allSimData.keys()))
    print(f"V_soma data exists: {'V_soma' in sim.allSimData}")
    print(f"V_dend data exists: {'V_dend' in sim.allSimData}")
    
    # Get time vector
    time = np.arange(0, simConfig.duration + simConfig.dt, simConfig.dt)
    print(f"\nTime array shape: {np.shape(time)}")
    
    # Plot voltage traces for each cell
    print("\nPlotting voltage traces for each cell...")
    
    for cell_idx in range(40):
        print(f"\nProcessing cell {cell_idx}...")
        
        # Create a new figure for this cell
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
        
        # Plot soma voltage
        if 'V_soma' in sim.allSimData:
            soma_data = sim.allSimData['V_soma']
            if isinstance(soma_data, dict):
                # Try different key formats
                possible_keys = [f'cell_{cell_idx}', str(cell_idx)]
                found_soma = False
                for key in possible_keys:
                    if key in soma_data:
                        soma_v = soma_data[key]
                        if len(soma_v) > 0:
                            ax1.plot(time[:len(soma_v)], soma_v, 'b-', label='Soma')
                            ax1.set_ylabel('Voltage (mV)')
                            ax1.set_title(f'Cell {cell_idx} - Soma Voltage')
                            ax1.grid(True)
                            ax1.legend()
                            found_soma = True
                            break
                if not found_soma:
                    print(f"Warning: No soma data found for cell {cell_idx}")
            else:
                print(f"Warning: V_soma data is not a dict: {type(soma_data)}")
        
        # Plot dendrite voltage
        if 'V_dend' in sim.allSimData:
            dend_data = sim.allSimData['V_dend']
            if isinstance(dend_data, dict):
                # Try different key formats
                possible_keys = [f'cell_{cell_idx}', str(cell_idx)]
                found_dend = False
                for key in possible_keys:
                    if key in dend_data:
                        dend_v = dend_data[key]
                        if len(dend_v) > 0:
                            ax2.plot(time[:len(dend_v)], dend_v, 'r-', label='Dendrite')
                            ax2.set_xlabel('Time (ms)')
                            ax2.set_ylabel('Voltage (mV)')
                            ax2.set_title(f'Cell {cell_idx} - Dendrite Voltage')
                            ax2.grid(True)
                            ax2.legend()
                            found_dend = True
                            break
                if not found_dend:
                    print(f"Warning: No dendrite data found for cell {cell_idx}")
            else:
                print(f"Warning: V_dend data is not a dict: {type(dend_data)}")
        
        # Add overall title
        fig.suptitle(f'Cell {cell_idx} Voltage Traces')
        
        # Save the plot
        try:
            filename = os.path.join(figures_dir, f'cell_{cell_idx}_voltage_traces.png')
            plt.savefig(filename, dpi=300)
            print(f"Saved plot for cell {cell_idx} to: {filename}")
            
            # Verify file exists
            if os.path.exists(filename):
                print(f"File size: {os.path.getsize(filename)} bytes")
            else:
                print(f"Error: File not created: {filename}")
        except Exception as e:
            print(f"Error saving plot for cell {cell_idx}: {str(e)}")
        
        # Close the figure to free memory
        plt.close(fig)
    
    print("\nAll individual cell plots have been generated!")
    print(f"Check the {figures_dir} directory for the PNG files.")
    
except Exception as e:
    print(f"\nError during plotting: {str(e)}")
    print("Debug information:")
    print(f"Working directory: {os.getcwd()}")
    print(f"Figures directory: {figures_dir}")
    if hasattr(sim, 'allSimData'):
        print(f"Available data keys: {list(sim.allSimData.keys())}")
    raise

simConfig.analysis = {
    "plotTraces": {
        "include": [0],
        "saveFig": True,
        "showFig": True,
        "figSize": (8, 6),
        "saveFolder": "figures"
    }
}

# Function to visualize network connectivity
def visualize_network(sim, save=True):
    """
    Create a 2D visualization of the network with neurons as dots and connections as lines
    Color-coded by cell type: pyramidal (blue) and parvalbumin (red)
    """
    import matplotlib.pyplot as plt
    import numpy as np
    import os
    
    # Create figure
    plt.figure(figsize=(10, 10))
    
    # Get cell positions (we'll create them in a circle pattern since they're not defined spatially)
    num_cells = len(sim.net.allCells)
    radius = 200  # arbitrary radius for visualization
    
    # Create positions in two concentric circles - pyramidal cells outer, PV cells inner
    positions = {}
    
    # Pyramidal cells (0-19) in outer circle
    for i in range(20):
        angle = 2 * np.pi * i / 20
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        positions[i] = (x, y)
    
    # PV cells (20-39) in inner circle
    inner_radius = radius * 0.6
    for i in range(20, 40):
        angle = 2 * np.pi * (i-20) / 20
        x = inner_radius * np.cos(angle)
        y = inner_radius * np.sin(angle)
        positions[i] = (x, y)
    
    # Generate connections based on connection parameters
    # We'll create synthetic connections based on our connection rules
    connections = []
    
    # E->E connections (probability 0.1)
    for pre in range(20):
        for post in range(20):
            if pre != post and np.random.random() < 0.1:  # 10% probability
                connections.append((pre, post, 'E->E'))
    
    # E->I connections (probability 0.2)
    for pre in range(20):
        for post in range(20, 40):
            if np.random.random() < 0.2:  # 20% probability
                connections.append((pre, post, 'E->I'))
    
    # I->E connections (probability 0.2)
    for pre in range(20, 40):
        for post in range(20):
            if np.random.random() < 0.2:  # 20% probability
                connections.append((pre, post, 'I->E'))
    
    # I->I connections (probability 0.1)
    for pre in range(20, 40):
        for post in range(20, 40):
            if pre != post and np.random.random() < 0.1:  # 10% probability
                connections.append((pre, post, 'I->I'))
    
    # Plot connections
    for pre_id, post_id, conn_type in connections:
        pre_pos = positions[pre_id]
        post_pos = positions[post_id]
        
        # Determine connection type for color
        if conn_type == 'E->E':
            color = 'blue'
            alpha = 0.1
        elif conn_type == 'E->I':
            color = 'purple'
            alpha = 0.2
        elif conn_type == 'I->E':
            color = 'red'
            alpha = 0.2
        else:  # I->I
            color = 'darkred'
            alpha = 0.1
        
        plt.plot([pre_pos[0], post_pos[0]], [pre_pos[1], post_pos[1]], 
                 color=color, alpha=alpha, linewidth=0.5)
    
    # Plot cells
    for gid, pos in positions.items():
        if gid < 20:  # Pyramidal cells
            plt.scatter(pos[0], pos[1], s=80, color='blue', edgecolor='black', zorder=10)
        else:  # PV cells
            plt.scatter(pos[0], pos[1], s=60, color='red', edgecolor='black', zorder=10)
    
    # Add legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=10, label='Pyramidal'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=10, label='Parvalbumin'),
        Line2D([0], [0], color='blue', label='E→E'),
        Line2D([0], [0], color='purple', label='E→I'),
        Line2D([0], [0], color='red', label='I→E'),
        Line2D([0], [0], color='darkred', label='I→I')
    ]
    plt.legend(handles=legend_elements, loc='upper right')
    
    # Add title and labels
    plt.title('Network Connectivity: Pyramidal (blue) and Parvalbumin (red) Cells')
    plt.xlabel('X position (μm)')
    plt.ylabel('Y position (μm)')
    plt.axis('equal')
    
    # Save figure
    if save:
        save_dir = 'figures'
        os.makedirs(save_dir, exist_ok=True)
        plt.savefig(os.path.join(save_dir, 'network_visualization.png'), dpi=300)
        print(f"Network visualization saved to {os.path.join(save_dir, 'network_visualization.png')}")
    
    plt.show()
    return

# Add this after sim.analyze()
print("Analyzing spike-field entrainment...")

# Analyze all cells together
print("\nAnalyzing ALL cells:")
entrainment_results_all = analyze_spike_field_entrainment(sim.allSimData, field_freq=140)

# Analyze pyramidal cells only
print("\nAnalyzing PYRAMIDAL cells only:")
entrainment_results_pyr = analyze_spike_field_entrainment(sim.allSimData, field_freq=140, cell_type='pyr')

# Analyze PV cells only
print("\nAnalyzing PARVALBUMIN cells only:")
entrainment_results_pv = analyze_spike_field_entrainment(sim.allSimData, field_freq=140, cell_type='pv')

# Print results for each cell type
if entrainment_results_all:
    print(f"ALL cells: PLV={entrainment_results_all['plv']:.3f}, Mean Phase={entrainment_results_all['mean_phase']:.1f}°, N={entrainment_results_all['n_spikes']} spikes")

if entrainment_results_pyr:
    print(f"PYRAMIDAL cells: PLV={entrainment_results_pyr['plv']:.3f}, Mean Phase={entrainment_results_pyr['mean_phase']:.1f}°, N={entrainment_results_pyr['n_spikes']} spikes")

if entrainment_results_pv:
    print(f"PARVALBUMIN cells: PLV={entrainment_results_pv['plv']:.3f}, Mean Phase={entrainment_results_pv['mean_phase']:.1f}°, N={entrainment_results_pv['n_spikes']} spikes")

# Visualize the network
print("\nCreating network visualization...")
visualize_network(sim)

sim.analysis.plot2Dnet(
    saveFig=os.path.join('figures', 'network_2d_plot.png'),
    showConns=True,
    figSize=(10, 10)
)

# Create a 3D visualization of the network with detailed neuron morphologies
def visualize_network_3d(sim, save=True):
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    import numpy as np
    import os
    from matplotlib.patches import Circle, PathPatch
    from matplotlib.transforms import Affine2D
    import mpl_toolkits.mplot3d.art3d as art3d
    
    # Create figure
    fig = plt.figure(figsize=(14, 12))
    ax = fig.add_subplot(111, projection='3d')
    
    # Get cell positions
    positions = {}
    for cell in sim.net.cells:
        # Add some random offset to z to make visualization more interesting
        positions[cell.gid] = (cell.tags['x'], cell.tags['y'], cell.tags['z'] if 'z' in cell.tags else np.random.uniform(0, 100))
    
    # Function to draw a neuron with soma and dendrite
    def draw_neuron(ax, pos, is_pyramidal=True):
        x, y, z = pos
        
        # Draw soma as a sphere
        if is_pyramidal:
            radius = 6  # Pyramidal cells have larger soma
            color = 'royalblue'
            alpha = 0.8
        else:
            radius = 5  # PV cells have smaller soma
            color = 'crimson'
            alpha = 0.8
            
        # Create a sphere for the soma
        u = np.linspace(0, 2 * np.pi, 20)
        v = np.linspace(0, np.pi, 20)
        sx = x + radius * np.outer(np.cos(u), np.sin(v))
        sy = y + radius * np.outer(np.sin(u), np.sin(v))
        sz = z + radius * np.outer(np.ones(np.size(u)), np.cos(v))
        ax.plot_surface(sx, sy, sz, color=color, alpha=alpha, linewidth=0)
        
        # Draw dendrite
        if is_pyramidal:
            # Pyramidal cells have longer dendrites
            dend_length = 100
            # Apical dendrite points upward
            dend_x = np.linspace(x, x, 20)
            dend_y = np.linspace(y, y, 20)
            dend_z = np.linspace(z, z + dend_length, 20)
            ax.plot(dend_x, dend_y, dend_z, color=color, linewidth=2, alpha=0.7)
            
            # Add some basal dendrites (simplified)
            for angle in np.linspace(0, 2*np.pi, 4):
                basal_length = 50
                dend_x = np.linspace(x, x + basal_length * np.cos(angle), 20)
                dend_y = np.linspace(y, y + basal_length * np.sin(angle), 20)
                dend_z = np.linspace(z, z, 20)
                ax.plot(dend_x, dend_y, dend_z, color=color, linewidth=1, alpha=0.5)
        else:
            # PV cells have shorter, more radial dendrites
            for angle1 in np.linspace(0, 2*np.pi, 3):
                for angle2 in np.linspace(0, np.pi, 2):
                    dend_length = 40
                    dx = dend_length * np.sin(angle2) * np.cos(angle1)
                    dy = dend_length * np.sin(angle2) * np.sin(angle1)
                    dz = dend_length * np.cos(angle2)
                    dend_x = np.linspace(x, x + dx, 20)
                    dend_y = np.linspace(y, y + dy, 20)
                    dend_z = np.linspace(z, z + dz, 20)
                    ax.plot(dend_x, dend_y, dend_z, color=color, linewidth=1, alpha=0.6)
    
    # Create connections list
    connections = []
    
    # Use actual connections from the simulation if available
    if hasattr(sim, 'net') and hasattr(sim.net, 'connections'):
        for conn in sim.net.connections:
            pre_id = conn.preGid
            post_id = conn.postGid
            
            # Determine connection type
            if pre_id < 20 and post_id < 20:
                conn_type = 'E->E'
            elif pre_id < 20 and post_id >= 20:
                conn_type = 'E->I'
            elif pre_id >= 20 and post_id < 20:
                conn_type = 'I->E'
            else:
                conn_type = 'I->I'
                
            connections.append((pre_id, post_id, conn_type))
    else:
        # If connections not available, generate based on probabilities
        # E->E connections (probability 0.2)
        for pre in range(20):
            for post in range(20):
                if pre != post and np.random.random() < 0.2:
                    connections.append((pre, post, 'E->E'))
        
        # E->I connections (probability 0.2)
        for pre in range(20):
            for post in range(20, 40):
                if np.random.random() < 0.2:
                    connections.append((pre, post, 'E->I'))
        
        # I->E connections (probability 0.2)
        for pre in range(20, 40):
            for post in range(20):
                if np.random.random() < 0.2:
                    connections.append((pre, post, 'I->E'))
        
        # I->I connections (probability 0.2)
        for pre in range(20, 40):
            for post in range(20, 40):
                if pre != post and np.random.random() < 0.2:
                    connections.append((pre, post, 'I->I'))
    
    # Plot connections
    for pre_id, post_id, conn_type in connections:
        if pre_id in positions and post_id in positions:  # Make sure both cells exist
            pre_pos = positions[pre_id]
            post_pos = positions[post_id]
            
            # Determine connection type for color
            if conn_type == 'E->E':
                color = 'blue'
                alpha = 0.3
                linewidth = 0.7
            elif conn_type == 'E->I':
                color = 'purple'
                alpha = 0.3
                linewidth = 0.7
            elif conn_type == 'I->E':
                color = 'red'
                alpha = 0.3
                linewidth = 0.7
            else:  # I->I
                color = 'darkred'
                alpha = 0.3
                linewidth = 0.7
            
            # Draw connection as a curved line
            # Calculate midpoint with slight offset for curved appearance
            mid_x = (pre_pos[0] + post_pos[0]) / 2
            mid_y = (pre_pos[1] + post_pos[1]) / 2
            mid_z = (pre_pos[2] + post_pos[2]) / 2 + np.random.uniform(10, 30)
            
            # Create a Bezier curve
            t = np.linspace(0, 1, 20)
            x = (1-t)**2 * pre_pos[0] + 2*(1-t)*t * mid_x + t**2 * post_pos[0]
            y = (1-t)**2 * pre_pos[1] + 2*(1-t)*t * mid_y + t**2 * post_pos[1]
            z = (1-t)**2 * pre_pos[2] + 2*(1-t)*t * mid_z + t**2 * post_pos[2]
            
            ax.plot(x, y, z, color=color, alpha=alpha, linewidth=linewidth)
    
    # Draw neurons
    for gid, pos in positions.items():
        is_pyramidal = gid < 20  # First 20 cells are pyramidal
        draw_neuron(ax, pos, is_pyramidal)
    
    # Add legend with custom handles
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='royalblue', markersize=15, label='Pyramidal Neuron'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='crimson', markersize=15, label='Parvalbumin Neuron'),
        Line2D([0], [0], color='blue', label='E→E Connection'),
        Line2D([0], [0], color='purple', label='E→I Connection'),
        Line2D([0], [0], color='red', label='I→E Connection'),
        Line2D([0], [0], color='darkred', label='I→I Connection')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
    # Add title and labels
    ax.set_title('3D Network Visualization with Detailed Neuron Morphology', fontsize=14)
    ax.set_xlabel('X position (μm)', fontsize=12)
    ax.set_ylabel('Y position (μm)', fontsize=12)
    ax.set_zlabel('Z position (μm)', fontsize=12)
    
    # Calculate axis limits
    x_values = [pos[0] for pos in positions.values()]
    y_values = [pos[1] for pos in positions.values()]
    z_values = [pos[2] for pos in positions.values()]
    
    # Set equal aspect ratio
    max_range = np.array([max(x_values) - min(x_values),
                          max(y_values) - min(y_values),
                          max(z_values) - min(z_values)]).max() / 2.0
    
    mid_x = (max(x_values) + min(x_values)) * 0.5
    mid_y = (max(y_values) + min(y_values)) * 0.5
    mid_z = (max(z_values) + min(z_values)) * 0.5
    
    # Add some padding to the limits
    padding = max_range * 0.3
    ax.set_xlim(mid_x - max_range - padding, mid_x + max_range + padding)
    ax.set_ylim(mid_y - max_range - padding, mid_y + max_range + padding)
    ax.set_zlim(mid_z - max_range - padding, mid_z + max_range + padding)
    
    # Add interactivity - set initial view angle
    ax.view_init(elev=25, azim=30)
    
    # Save figure
    if save:
        save_dir = 'figures'
        os.makedirs(save_dir, exist_ok=True)
        plt.savefig(os.path.join(save_dir, 'network_3d_detailed_visualization.png'), dpi=300, bbox_inches='tight')
        print(f"3D detailed network visualization saved to {os.path.join(save_dir, 'network_3d_detailed_visualization.png')}")
    
    plt.tight_layout()
    plt.show()
    return

# Call the 3D visualization function
print("\nCreating 3D network visualization...")
visualize_network_3d(sim)