# ELEC 583 Project

This repository simulates single-neuron responses to electric field stimulation using NEURON and BMTK. It includes morphology preprocessing, parameter setup, simulation execution, and spike-phase analysis via rose plots to evaluate electric field entrainment.

📁 Project Structure

PvalbA_8Hz_HOF0/
│
├── 01_Set_up.py               # Prepares morphology, parameter files, and runs simulations in 16 threads
├── 02_Gather_Data.py          # Aggregates simulation outputs
├── 03_Erase_files.py          # Cleans up temporary simulation folders
├── 04_Plot_results.py         # Analyzes phase-locking and generates rose plots
├── MultiRun.bat               # Optional Windows batch script to automate runs
│
├── required_files/
│   ├── neuronal_model/        # Contains morphologies (.swc), parameters (.json), mod files
│   ├── ais_functions.py       # Axon initial segment manipulation functions
│   ├── cell_functions.py      # Utilities for neuron setup in BMTK
│   └── Simulation_(Main).py   # Copied per thread to simulate different runs
│
├── Temp/                      # Temporary thread-based folders for simulations
├── Results/                   # Output CSVs, rose plots, and result PDFs
└── Rose_plots_hof0.pdf        # Final visualization output

🚀 How to Run the Simulation

1. Set Up Your Environment

Install required packages:

pip install numpy pandas matplotlib efel neurom pycircstat morphio

NEURON and BMTK must also be installed. Follow BMTK installation instructions.

2. Run Setup and Simulations

This script rotates morphologies, processes parameters, and automatically runs 16 simulation threads:

python 01_Set_up.py <StartCurrent> <CellType>

StartCurrent: e.g., 630

CellType: e.g., pyram, pval

3. Gather Results

python 02_Gather_Data.py 630 0 pyram

4. Visualize Phase Entrainment

python Plots/04_Plot_results.py

Generates Rose_plots_hof0.pdf.

5. Cleanup

python 03_Erase_files.py

📊 Output

Rose Plots showing spike-phase histograms and vector strength

CSV Results with spike rates and entrainment metrics

PDF of Morphologies with rotation metadata

🔠 Importing a New Neuron

1. Add the Morphology

Place your new .swc file into:

./required_files/neuronal_model/

Example filename: Cell_rotated_newneuron.swc

2. Add Electrophysiological Parameters

Add .json file with cm, e_pas, and ra values:

./required_files/neuronal_model/hof_param_<timestamp>_0_newneuron.json

3. Run Setup and Simulations

python 01_Set_up.py <current> newneuron

Automatically:

Rotates .swc

Creates fixed .json

Compiles NEURON mechanisms

Creates thread folders and runs simulations

4. Gather and Plot Results

python 02_Gather_Data.py 630 0 newneuron
python Plots/04_Plot_results.py

📃 Biological Context

This simulation explores how neuron types (e.g., pyramidal, pvalb) respond to alternating electric fields. This is relevant for studying effects of techniques like transcranial electric stimulation. Outputs include spike-phase histograms and entrainment metrics based on circular statistics.

📘 References

NEURON: https://neuron.yale.edu/neuron/

BMTK: https://alleninstitute.github.io/bmtk/

eFEL: https://github.com/BlueBrain/eFEL
