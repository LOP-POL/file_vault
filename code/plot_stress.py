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


def fix_vtk_scalars_header(vtk_file_path, component=None):
    """
    Fix malformed VTK SCALARS declaration by adding the scalar name.
    
    Some VTK generators (e.g., data2vtk) produce incomplete SCALARS lines:
        SCALARS float 1
    
    This should be:
        SCALARS stress<component> float 1
    
    This function reads the VTK file, fixes the header, and writes it back.
    
    Args:
        vtk_file_path: Path to the VTK file
        component: Component name to add (e.g., '11', '22', '21')
    """
    try:
        with open(vtk_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # Look for malformed SCALARS line
        modified = False
        for i, line in enumerate(lines):
            # Match SCALARS declarations that are missing the name
            if line.strip().startswith('SCALARS'):
                parts = line.split()
                # Malformed: SCALARS float 1 (only 3 parts, missing scalar name)
                # Correct: SCALARS name float 1 (4 parts)
                if len(parts) >= 2 and parts[1] in ['float', 'int', 'double', 'unsigned_char', 'unsigned_int']:
                    scalar_name = f"stress{component}" if component else "stress"
                    # Reconstruct: SCALARS <name> <type> <num_components>
                    new_line = f"SCALARS {scalar_name} {' '.join(parts[1:])}\n"
                    lines[i] = new_line
                    modified = True
                    print(f"Fixed SCALARS header: added name '{scalar_name}'", file=sys.stderr)
        
        if modified:
            with open(vtk_file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
    
    except Exception as e:
        print(f"Warning: Could not fix VTK header: {e}", file=sys.stderr)


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
    
    # Fix any malformed SCALARS headers before reading
    fix_vtk_scalars_header(vtk_file_path, component)
    
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
        print("stress data to be plotted")
        print(stress_data)
        print(f"length is stress data {len(stress_data)}")
        # Compute coordinates based on grid structure
        # vtkStructuredPoints uses origin, spacing, and dimensions
        dims = output.GetDimensions()
        spacing = output.GetSpacing()
        origin = output.GetOrigin()
        
        # Generate X coordinates based on grid spacing
        # dims are (nx, ny, nz), spacing is (dx, dy, dz)
        nx = dims[0]
        dx = spacing[0]
        x0 = origin[0]
        x_values = np.array([x0 + i * dx for i in range(nx)])
        print(" \n x values")
        print(x_values)
        stress_values = stress_data if stress_data.ndim == 1 else stress_data[:, 0]
        
        # Ensure arrays have matching lengths
        if len(x_values) != len(stress_values):
            print(f"Warning: X coordinates ({len(x_values)}) don't match stress data ({len(stress_values)}). "
                  f"Using indices as X-axis.", file=sys.stderr)
            x_values = np.arange(len(stress_values))
        
        return x_values, stress_values
        
    except Exception as e:
        print(f"Error reading VTK file: {e}", file=sys.stderr)
        return None

def manual_extraction(vtk_file_path, component):

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
    
    # Fix any malformed SCALARS headers before reading
    fix_vtk_scalars_header(vtk_file_path, component)
    
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

        stress = numpy_support.vtk_to_numpy(
            output.GetPointData().GetScalars()
        )
        nx, ny, nz = output.GetDimensions()
        stress =  stress.reshape((ny,nx))
       
        return nx, ny , stress
        
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

def visulize_whole_field(outdir,infile_parent,angle_str,chi_str,stress, component):
    plt.figure()
    plt.imshow(stress, origin='lower')
    plt.colorbar(label='Stress')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.show()

    outdir = Path(outdir) if outdir else infile_parent
    outdir.mkdir(parents=True, exist_ok=True)
    
    comp_tag = f"stress{component}" if component else "stress"
    out_name = f"{comp_tag}_chi_{chi_str}_angle_{angle_str}_field.png"
    out_path = outdir / out_name
    plt.savefig(str(out_path), dpi=150)
    print(f"Saved plot to: {out_path}")

def plot_stress_vs_x_fixed_y(x,stress,y_index,infile_parent,component,chi_str,angle_str, outdir):
    plt.figure()
    plt.plot(x,stress[y_index, :])
    plt.xlabel('x')
    plt.ylabel('stress')
    plt.title(f"stress along y={y_index}")
    outdir = Path(outdir) if outdir else infile_parent
    outdir.mkdir(parents=True, exist_ok=True)
    
    comp_tag = f"stress{component}" if component else "stress"
    out_name = f"{comp_tag}_chi_{chi_str}_angle_{angle_str}_x_fixed_y{y_index}.png"
    out_path = outdir / out_name
    plt.savefig(str(out_path), dpi=150)
    print(f"Saved plot to: {out_path}")

def plot_stress_vs_y_fixed_x(y,stress,x_index,infile_parent,component,chi_str,angle_str, outdir):
    plt.figure()
    plt.plot(y,stress[: ,x_index])
    plt.xlabel('x')
    plt.ylabel('stress')
    plt.title(f"stress along y={x_index}")
    outdir = Path(outdir) if outdir else infile_parent
    outdir.mkdir(parents=True, exist_ok=True)
    
    comp_tag = f"stress{component}" if component else "stress"
    out_name = f"{comp_tag}_chi_{chi_str}_angle_{angle_str}_y_fixed_x{x_index}.png"
    out_path = outdir / out_name
    plt.savefig(str(out_path), dpi=150)
    print(f"Saved plot to: {out_path}")


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

        nx, ny, stress_man = manual_extraction(infile, args.component) # type: ignore
        y_values_man = np.arange(ny)
        x_values_man = np.arange(nx)
       

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

    outdir = Path(args.outdir) if args.outdir else infile.parent
    outdir.mkdir(parents=True, exist_ok=True)

    visulize_whole_field(args.outdir, infile.parent,angle_str,chi_str,stress_man,component)
    plot_stress_vs_x_fixed_y(x_values_man,stress_man,48,infile.parent,component,chi_str,angle_str, outdir)
    plot_stress_vs_y_fixed_x(y_values_man,stress_man,48,infile.parent,component,chi_str,angle_str, outdir)

    if args.show:
        plt.show()


if __name__ == "__main__":
    main()

