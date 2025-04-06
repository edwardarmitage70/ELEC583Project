from netpyne import specs, sim
from neuron import h
import os
import numpy as np

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
    "gnabar": 0.12,
    "gkbar": 0.036,
    "gl": 0.0003,
    "el": -54.3
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

netParams.popParams['E'] = {
    "cellType": "pyr",
    "numCells": 40,
}

netParams.synMechParams['exc'] = {
    "mod": "Exp2Syn",
    "tau1": 0.1,
    "tau2": 1.0,
    "e": 0
}

netParams.connParams['E->E'] = {
    "preConds": {"pop": "E"},
    "postConds": {"pop": "E"},
    "weight": 0.005,
    "probability": 0.1,
    "delay": 5.0,
    "synMech": "exc",
    "sec": "dend",
    "loc": 1.0,
}

netParams.stimSourceParams['IClamp1'] = {
    "type": "IClamp",
    "dur": 5,
    "del": 20,
    "amp": 0.1,
}

netParams.stimTargetParams['IClamp1->cell0'] = {
    "source": "IClamp1",
    "conds": {"cellList": [0]},
    "sec": "dend",
    "loc": 1.0,
}

# Simulation configuration
simConfig.filename = "netpyne_tut1"
simConfig.duration = 200.0
simConfig.dt = 0.1

# Recording configuration
simConfig.recordCells = [0]       # Record from cell 0
simConfig.recordStep = 0.1        # Record every 0.1ms
simConfig.recordStim = True       # Record stimulation
simConfig.recordV = True          # Record voltage
simConfig.recordTime = True       # Record time
simConfig.saveMat = True         # Save to .mat file

# Record specific traces
simConfig.recordTraces = {
    "V_soma": {
        "sec": "soma",
        "loc": 0.5,
        "var": "v"
    },
    "V_dend": {
        "sec": "dend",
        "loc": 1.0,
        "var": "v"
    }
}

print("\nDebug - Recording configuration:")
print(f"Recording from cells: {simConfig.recordCells}")
print(f"Recording step: {simConfig.recordStep}")
print("Recording traces:")
for trace_name, trace_config in simConfig.recordTraces.items():
    print(f"- {trace_name}: {trace_config}")

# Create output directory if it doesn't exist
figures_dir = os.path.abspath('./figures')
if not os.path.exists(figures_dir):
    os.makedirs(figures_dir)
print(f"\nSaving plots to: {figures_dir}")

# First run simulation
sim.createSimulateAnalyze(netParams=netParams, simConfig=simConfig)

# Verify simulation data
print("\nVerifying simulation data...")
if hasattr(sim, 'allSimData'):
    print("Available data keys:", list(sim.allSimData.keys()))
    for key in ['V_soma', 'V_dend']:
        if key in sim.allSimData:
            data = sim.allSimData[key]
            print(f"\n{key} data:")
            print(f"Type: {type(data)}")
            print(f"Shape: {np.shape(data)}")
            if len(data) > 0:
                print(f"First few values: {data[0][:5]}")
        else:
            print(f"\nWarning: {key} not found in recorded data")
else:
    print("No simulation data found in sim.allSimData!")

# Now generate and save plots
try:
    import matplotlib.pyplot as plt
    
    print("\nGenerating plots...")
    
    # Network plot
    fig1 = plt.figure(figsize=(8, 8))
    sim.analysis.plot2Dnet(showFig=False)
    plt.savefig(os.path.join(figures_dir, 'network_2d.png'))
    plt.close(fig1)
    print("Network plot saved")
    
    # Basic connectivity plot
    fig2 = plt.figure(figsize=(8, 8))
    sim.analysis.plotConn(showFig=False)
    plt.savefig(os.path.join(figures_dir, 'connectivity.png'))
    plt.close(fig2)
    print("Connectivity plot saved")
    
    # Weight connectivity plot
    fig3 = plt.figure(figsize=(8, 8))
    sim.analysis.plotConn(feature='weight', groupBy='cell', showFig=False)
    plt.savefig(os.path.join(figures_dir, 'connectivity_weights.png'))
    plt.close(fig3)
    print("Weight connectivity plot saved")
    
    # Plot voltage traces
    print("\nPlotting voltage traces...")
    fig4 = plt.figure(figsize=(10, 6))
    
    # Get time vector
    time = np.arange(0, simConfig.duration + simConfig.dt, simConfig.dt)
    
    # Plot soma voltage
    plt.subplot(2, 1, 1)
    if 'V_soma' in sim.allSimData:
        soma_v = sim.allSimData['V_soma'][0]  # Get data for cell 0
        plt.plot(time[:len(soma_v)], soma_v, 'b-', label='Soma')
        plt.title('Membrane Potential - Cell 0')
        plt.ylabel('Voltage (mV)')
        plt.legend()
        plt.grid(True)
    else:
        print("Warning: No soma voltage data found")
    
    # Plot dendrite voltage
    plt.subplot(2, 1, 2)
    if 'V_dend' in sim.allSimData:
        dend_v = sim.allSimData['V_dend'][0]  # Get data for cell 0
        plt.plot(time[:len(dend_v)], dend_v, 'r-', label='Dendrite')
        plt.xlabel('Time (ms)')
        plt.ylabel('Voltage (mV)')
        plt.legend()
        plt.grid(True)
    else:
        print("Warning: No dendrite voltage data found")
    
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, 'voltage_traces.png'))
    plt.close(fig4)
    print("Voltage traces saved")
    
    # Print some statistics
    if 'V_soma' in sim.allSimData:
        print("\nVoltage Statistics (Cell 0):")
        print(f"Soma - Mean: {np.mean(sim.allSimData['V_soma'][0]):.2f} mV")
        print(f"Soma - Max: {np.max(sim.allSimData['V_soma'][0]):.2f} mV")
        print(f"Soma - Min: {np.min(sim.allSimData['V_soma'][0]):.2f} mV")
    
    if 'V_dend' in sim.allSimData:
        print(f"Dendrite - Mean: {np.mean(sim.allSimData['V_dend'][0]):.2f} mV")
        print(f"Dendrite - Max: {np.max(sim.allSimData['V_dend'][0]):.2f} mV")
        print(f"Dendrite - Min: {np.min(sim.allSimData['V_dend'][0]):.2f} mV")
    
    # Verify files were created
    expected_files = ['network_2d.png', 'connectivity.png', 'connectivity_weights.png', 'voltage_traces.png']
    for file in expected_files:
        path = os.path.join(figures_dir, file)
        if os.path.exists(path):
            print(f"Verified: {file} exists")
        else:
            print(f"Warning: {file} was not created")
            
except Exception as e:
    print(f"\nError during plotting: {str(e)}")
    print("Debug information:")
    print(f"Working directory: {os.getcwd()}")
    print(f"Figures directory: {figures_dir}")
    if hasattr(sim, 'net'):
        print(f"Network exists with {len(sim.net.cells)} cells")
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
