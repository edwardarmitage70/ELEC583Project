# ELEC 583 Project

This repository simulates single-neuron responses to electric field stimulation using NEURON and BMTK. It includes morphology preprocessing, parameter setup, simulation execution, and spike-phase analysis via rose plots to evaluate electric field entrainment.

---

## 📁 Project Structure

```
PvalbA_8Hz_HOF0/
│
├── 01_Set_up.py               # Prepares morphology, parameter files, and directories
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
```

---

## 🚀 How to Run the Simulation

### 1. **Set Up Your Environment**
Install required packages:
```bash
pip install numpy pandas matplotlib efel neurom pycircstat morphio
```
NEURON and BMTK must also be installed. Follow [BMTK installation instructions](https://github.com/AllenInstitute/bmtk).

### 2. **Run Setup**
```bash
python 01_Set_up.py <StartCurrent> <CellType>
```
- `StartCurrent`: e.g., `630`
- `CellType`: e.g., `pyram`, `pval`

### 3. **Run Simulations**
This creates and runs 16 threads of electric stimulation:
```bash
python 01_Set_up.py 630 pyram
```

### 4. **Gather Results**
```bash
python 02_Gather_Data.py 630 0 pyram
```

### 5. **Visualize Phase Entrainment**
```bash
python Plots/04_Plot_results.py
```
Generates `Rose_plots_hof0.pdf`.

### 6. **Cleanup**
```bash
python 03_Erase_files.py
```

---

## 📊 Output

- **Rose Plots** showing spike-phase histograms and vector strength
- **CSV Results** with spike rates and entrainment metrics
- **PDF of Morphologies** with rotation metadata

---

## 🔠 Importing a New Neuron

### 1. **Add the Morphology**
Place your new `.swc` file into:
```
./required_files/neuronal_model/
```
Example filename: `Cell_rotated_newneuron.swc`

### 2. **Add Electrophysiological Parameters**
Add `.json` file with `cm`, `e_pas`, and `ra` values:
```
./required_files/neuronal_model/hof_param_<timestamp>_0_newneuron.json
```

### 3. **Run `01_Set_up.py`**
```bash
python 01_Set_up.py <current> newneuron
```
Automatically:
- Rotates `.swc`
- Creates fixed `.json`
- Compiles NEURON mechanisms
- Creates thread folders

### 4. **Verify Simulation Configuration**
- Check that `Simulation_(Main).py` is configured with your new files (automatic)

### 5. **Run the Simulations**
```bash
python ./Temp/Threads2/Thread0/Simulation_(Main).py 1
```

### 6. **Gather and Plot Results**
```bash
python 02_Gather_Data.py 630 0 newneuron
python Plots/04_Plot_results.py
```

## 📘 References

- NEURON: https://neuron.yale.edu/neuron/
- BMTK: https://alleninstitute.github.io/bmtk/
- eFEL: https://github.com/BlueBrain/eFEL

