# Enhancement Summary: get_data.sh and plot_stress.py

## Overview
Both scripts have been significantly enhanced to process simulation output folders, extract stress data via domain cuts, convert to VTK format, and generate publication-quality stress plots.

---

## get_data.sh - Complete Rewrite

### Purpose
Automated batch processing of simulation folders with the following workflow:
1. Discover all simulation folders matching the naming pattern
2. Extract chi and angle parameters from folder names
3. Create domain cuts using `domaincut` command (x-50 to x50, y-50 to y50)
4. Convert domain cuts to VTK format using `data2vtk`
5. Generate stress plots for each component (stress11, stress22, stress21)
6. Save plots with descriptive filenames

### Key Features

**Flexible Input/Output**
- Accepts parent directory as first argument
- Optional `--outdir` flag to specify output directory (defaults to `./plots`)
- Preserves folder structure in working directories

**Automatic Parameter Extraction**
- Extracts `chi` and `angle` values from folder names using regex:
  - Pattern: `transversely_iso_no_crack_chi_<CHI>_angle_<ANGLE>_<DATE>_<TIME>`
  - Example: `chi_2.5` and `angle_0` from folder name

**Stress Component Processing**
- Processes all three stress components: 11, 22, 21
- Creates separate domain cuts for each component
- Generates individual VTK files per component
- Produces one plot file per component

**Domain Cut Configuration**
- X offset: -50, X end: 50
- Y offset: -50, Y end: 50
- Uses `-f` flag to force overwrite of existing files

**Logging & Error Handling**
- Timestamps for each operation
- Warning messages for missing files
- Graceful handling of failed operations (continues to next component)
- Summary report at completion

### Usage

```bash
# Basic usage (saves plots to ./plots)
bash get_data.sh /path/to/simulation/results

# With custom output directory
bash get_data.sh /path/to/simulation/results --outdir /path/to/output/plots

# Example with actual paths
bash get_data.sh /mnt/data/results --outdir /mnt/data/results/stress_plots
```

### Requirements
- `domaincut` command (pace2D utility)
- `data2vtk` command (pace2D utility)
- Python 3 with numpy and matplotlib
- `plot_stress.py` in the same directory

---

## plot_stress.py - Major Enhancement

### Purpose
Read stress data from VTK or DAT files and produce publication-quality plots with chi and angle labels.

### Major Changes

**Dual Format Support**
- **Primary format**: VTK files (from data2vtk output)
- **Legacy format**: .dat files (two-column: index, value)
- Auto-detects format based on file extension

**VTK Data Extraction**
- New `read_vtk_scalar_data()` function:
  - Reads unstructured grid VTK files
  - Extracts scalar stress arrays
  - Handles component filtering
  - Converts to numpy arrays
  - Sorts data by X coordinate for proper plotting
  - Robust error handling

**DAT File Support**
- New `read_dat_data()` function:
  - Reads legacy two-column format
  - Validates column count
  - Returns numpy arrays

**Enhanced Command-line Interface**
```bash
# For VTK files
python3 plot_stress.py --infile stress11_cut.vtk --chi 2.5 --angle 0 --component 11 --outdir ./plots

# For legacy .dat files
python3 plot_stress.py --infile stress11_frame3.dat --chi 2.5 --angle 45 --outdir ./plots
```

**New Arguments**
- `--component`: Stress component ID (11, 22, 21) - auto-detected from filename if not provided
- `--infile`: Path to input file (VTK or DAT)
- `--chi`: Chi parameter value (required)
- `--angle`: Anisotropy angle in degrees (required)
- `--outdir`: Output directory (default: same as input file)
- `--show`: Display plot interactively (optional)

**Improved Plot Quality**
- Larger figure size (10x6 inches vs 8x5)
- Bold, larger title font
- Legend showing stress component
- Larger axis labels (12pt) and title (14pt bold)
- Marker size 3pt, line width 1.5pt
- 150 DPI output

**Smart Filename Extraction**
- Automatically detects stress component from filename if `--component` not provided
- Pattern matching for: stress11, stress22, stress21
- Fallback to user-provided component argument

**Output Naming Convention**
- Format: `stress{COMPONENT}_chi_{CHI}_angle_{ANGLE}.png`
- Examples:
  - `stress11_chi_2.5_angle_0.png`
  - `stress22_chi_2.5_angle_45.png`
  - `stress21_chi_1.5_angle_90.png`

### Dependencies
- numpy: Data handling
- matplotlib: Plotting
- vtk (optional): VTK file support
  - If not installed, falls back to .dat format only
  - Install with: `pip install vtk`

---

## Integration with get_data.sh

The bash script automatically calls `plot_stress.py` for each stress component:

```bash
python3 "$PLOT_SCRIPT" \
    --infile "$VTK_FILE" \
    --chi "$CHI" \
    --angle "$ANGLE" \
    --component "$COMPONENT" \
    --outdir "$OUTDIR"
```

This ensures:
- Consistent plot naming across all outputs
- Proper chi/angle values passed automatically
- Component correctly identified
- All plots saved to central output directory

---

## Example Workflow

Given a folder structure like:
```
/simulations/
├── transversely_iso_no_crack_chi_2.5_angle_0_01-Sep-2026_13:43/
│   ├── *.p3simgeo
│   ├── *.SolidMechanics_stress11.p3s
│   ├── *.SolidMechanics_stress22.p3s
│   └── *.SolidMechanics_stress21.p3s
├── transversely_iso_no_crack_chi_2.5_angle_45_01-Sep-2026_14:00/
│   └── ... (similar files)
└── transversely_iso_no_crack_chi_1.5_angle_90_01-Sep-2026_14:30/
    └── ... (similar files)
```

Running:
```bash
bash get_data.sh /simulations --outdir /simulations/stress_plots
```

Will produce:
```
/simulations/stress_plots/
├── stress11_chi_2.5_angle_0.png
├── stress22_chi_2.5_angle_0.png
├── stress21_chi_2.5_angle_0.png
├── stress11_chi_2.5_angle_45.png
├── stress22_chi_2.5_angle_45.png
├── stress21_chi_2.5_angle_45.png
├── stress11_chi_1.5_angle_90.png
├── stress22_chi_1.5_angle_90.png
└── stress21_chi_1.5_angle_90.png
```

Each folder also gets a `domain_cut_analysis/` working directory with:
- Domain cut files (stress{component}_cut.p3s)
- VTK files (stress{component}_vtk-*.vtk)

---

## Error Handling & Robustness

**get_data.sh**
- Validates parent directory exists
- Checks for required SimGeo files before processing
- Warns on missing stress files
- Continues processing if individual components fail
- Reports final summary with folder count

**plot_stress.py**
- Validates input file exists
- Checks data dimensions and validity
- Gracefully handles missing VTK arrays
- Falls back to filename metadata if component not provided
- Proper error messages to stderr
- Exit codes indicate success/failure

---

## Performance Notes

- Processing speed depends on:
  - Number of simulation folders
  - Size of stress files
  - VTK conversion performance
  - Python plot generation time
  
- For batch runs with many folders:
  - Create `--outdir` on fast storage (SSD preferred)
  - Intermediate VTK files are temporary and can be cleaned up
  - Consider running in background with `nohup` or `screen`

---

## Future Enhancements (Optional)

Potential improvements for future versions:
1. Parallel processing of multiple folders
2. Animated plots showing stress evolution
3. Multi-panel plots for all components
4. Statistical analysis (min, max, mean stress)
5. Heatmap generation from VTK data
6. Export to different formats (PDF, EPS)
7. Configuration file support for domain cut parameters
