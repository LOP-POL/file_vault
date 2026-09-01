#!/usr/bin/env python3
"""
plot_stress.py

Reads stress data from either:
  1. VTK files (from data2vtk output) - primary input format
  2. pace2D stress output .dat files (legacy format)

Produces plots labeled with chi and anisotropy-angle values for that run.

Usage:
    # VTK input (preferred):
    python3 plot_stress.py --infile STRESS.vtk --chi CHI --angle ANGLE --component COMP [--outdir DIR] [--show]
    
    # DAT input (legacy):
    python3 plot_stress.py --infile STRESS.dat --chi CHI --angle ANGLE [--outdir DIR] [--show]

Example:
    python3 plot_stress.py --infile stress11_chi_2.5_angle_0_cut.vtk --chi 2.5 --angle 0 --component 11
    python3 plot_stress.py --infile stress11_frame3of3.dat --chi 2.5 --angle 45
"""

import argparse
import re
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")  # safe default for headless/batch runs; --show still works
import matplotlib.pyplot as plt

# Optional VTK support
try:
    import vtk
    from vtkmodules.vtkIOLegacy import vtkDataSetReader, vtkStructuredPointsReader
    from vtkmodules.util import numpy_support
    HAS_VTK = True
except ImportError:
    HAS_VTK = False


def parse_args():
    parser = argparse.ArgumentParser(description="Plot stress data from .dat or .vtk files.")
    parser.add_argument("--infile", required=True, 
                        help="Path to the stress file (.dat or .vtk)")
    parser.add_argument("--chi", required=True, type=float, 
                        help="chi value for this run")
    parser.add_argument("--angle", required=True, type=float, 
                        help="Anisotropy angle (degrees) for this run")
    parser.add_argument("--component", default=None, 
                        help="Stress component identifier (e.g., '11', '22', '21') - auto-detected if not provided")
    parser.add_argument("--outdir", default=None,
                        help="Directory to save the plot in (default: same directory as --infile)")
    parser.add_argument("--show", action="store_true", 
                        help="Also display the plot interactively")
    return parser.parse_args()


def parse_filename_metadata(filename):
    """
    Pull whatever hints are available out of the filename, e.g.
    'stress11_frame3of3_X-50-102.dat' ->
        component = '11', frame = (3, 3), x_range = (-50.0, 102.0)
    Any piece that isn't found is returned as None, and the caller falls
    back to sensible defaults.
    """
    component = None
    m = re.search(r'stress(\d+)', filename, re.IGNORECASE)
    if m:
        component = m.group(1)

    frame = None
    m = re.search(r'frame(\d+)of(\d+)', filename, re.IGNORECASE)
    if m:
        frame = (int(m.group(1)), int(m.group(2)))

    x_range = None
    m = re.search(r'X(-?\d+(?:\.\d+)?)-(-?\d+(?:\.\d+)?)', filename)
    if m:
        x_range = (float(m.group(1)), float(m.group(2)))

    return component, frame, x_range


def format_value(value):
    """Format a chi/angle value without a trailing '.0' for whole numbers."""
    if float(value).is_integer():
        return str(int(value))
    return str(value)


def read_vtk_scalar_data(vtk_file_path, component=None):
    """
    Read scalar data from a VTK file.
    
    Args:
        vtk_file_path: Path to the VTK file
        component: Optional component name to filter (e.g., 'stress11')
    
    Returns:
        Tuple of (x_values, stress_values) as numpy arrays
        or None if data cannot be extracted
    """
    if not HAS_VTK:
        print("Error: VTK support not available. Install python package: vtk", file=sys.stderr)
        return None
    
    try:
        reader = vtkStructuredPointsReader()
        reader.SetFileName(str(vtk_file_path))
        reader.ReadAllVectorsOn()
        reader.ReadAllScalarsOn()
        reader.Update()
        
        output = reader.GetOutput()
        if output.GetNumberOfCells() == 0 and output.GetNumberOfPoints() == 0:
            print(f"Error: VTK file is empty: {vtk_file_path}", file=sys.stderr)
            return None
        
        # Try to find the stress array
        point_data = output.GetPointData()
        if point_data.GetNumberOfArrays() == 0:
            print(f"Warning: No arrays found in VTK file: {vtk_file_path}", file=sys.stderr)
            return None
        
        # Look for array matching the component
        stress_array = None
        if component:
            # Try to find array with component in name
            for i in range(point_data.GetNumberOfArrays()):
                arr = point_data.GetArray(i)
                name = arr.GetName() if arr.GetName() else f"Array_{i}"
                if component in name.lower():
                    stress_array = arr
                    break
        
        # Fallback: use first scalar array
        if stress_array is None:
            stress_array = point_data.GetArray(0)
        
        if stress_array is None:
            print(f"Error: Could not extract stress data from {vtk_file_path}", file=sys.stderr)
            return None
        
        # Convert to numpy array
        stress_data = numpy_support.vtk_to_numpy(stress_array)
        
        # Extract point coordinates
        points = output.GetPoints()
        coords = numpy_support.vtk_to_numpy(points.GetData())
        
        # Use first spatial dimension (X) as x-axis
        x_values = coords[:, 0] if coords.shape[1] > 0 else np.arange(len(stress_data))
        stress_values = stress_data if stress_data.ndim == 1 else stress_data[:, 0]
        
        # Sort by x coordinate
        sort_idx = np.argsort(x_values)
        x_values = x_values[sort_idx]
        stress_values = stress_values[sort_idx]
        
        return x_values, stress_values
        
    except Exception as e:
        print(f"Error reading VTK file: {e}", file=sys.stderr)
        return None


def read_dat_data(dat_file_path):
    """
    Read data from a .dat file (two whitespace-separated columns: index, value).
    
    Args:
        dat_file_path: Path to the .dat file
    
    Returns:
        Tuple of (x_values, stress_values) as numpy arrays
    """
    try:
        data = np.loadtxt(dat_file_path)
        if data.ndim != 2 or data.shape[1] < 2:
            print(f"Error: expected two columns (index, value) in {dat_file_path}, got shape {data.shape}",
                  file=sys.stderr)
            return None
        
        index_col, value_col = data[:, 0], data[:, 1]
        return index_col, value_col
    except Exception as e:
        print(f"Error reading .dat file: {e}", file=sys.stderr)
        return None


def main():
    args = parse_args()

    infile = Path(args.infile)
    if not infile.is_file():
        print(f"Error: input file not found: {infile}", file=sys.stderr)
        sys.exit(1)

    # Determine file type and read data
    if infile.suffix.lower() == '.vtk':
        result = read_vtk_scalar_data(infile, args.component)
        if result is None:
            sys.exit(1)
        x_values, value_col = result
        x_label = "Position, X"
    else:
        # Assume .dat format
        result = read_dat_data(infile)
        if result is None:
            sys.exit(1)
        index_col, value_col = result
        
        # Try to extract component and range from filename
        component, frame, x_range = parse_filename_metadata(infile.name)
        
        # Use physical X range if available
        if x_range is not None:
            x_values = np.linspace(x_range[0], x_range[1], len(index_col))
            x_label = "Position, X"
        else:
            x_values = index_col
            x_label = "Grid index"
    
    # Use provided component or try to extract from filename
    component = args.component if args.component else parse_filename_metadata(infile.name)[0]
    stress_label = f"$\\sigma_{{{component}}}$" if component else "Stress"

    chi_str = format_value(args.chi)
    angle_str = format_value(args.angle)

    title = f"{stress_label} vs {x_label} — chi = {chi_str}, angle = {angle_str}°"

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(x_values, value_col, marker="o", markersize=3, linewidth=1.5, label=f"stress{component}")
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(stress_label, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()

    outdir = Path(args.outdir) if args.outdir else infile.parent
    outdir.mkdir(parents=True, exist_ok=True)

    comp_tag = f"stress{component}" if component else "stress"
    out_name = f"{comp_tag}_chi_{chi_str}_angle_{angle_str}.png"
    out_path = outdir / out_name
    fig.savefig(str(out_path), dpi=150)
    print(f"Saved plot to: {out_path}")

    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
