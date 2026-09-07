#!/usr/bin/env python3
"""
plot_stress.py

Produces plots labeled with chi and anisotropy-angle values for that run.

Usage:
  
    python3 plot_stress.py --stressfile STRESS.txt --displacementfile displacement.txt --chi CHI --angle ANGLE --component COMP [--outdir DIR] [--show]
 
Example:
    python3 plot_stress.py --stressfile stress.txt --displacementfile displacement.txt --chi 2.5 --angle 0 --component 11
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

def parse_args():
    parser = argparse.ArgumentParser(description="Plot stress data from .dat or .vtk files.")
    # New: allow plotting stress vs displacement from two boxaverage output files
    parser.add_argument("--stressfile", default=None,
                        help="Path to a stress boxaverage output (text) file to use for stress values")
    parser.add_argument("--displacementfile", default=None,
                        help="Path to a displacement boxaverage output (text) file; uses last column named 'absolute_averageaverage_of_cells' or the last numeric column")
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

def read_last_column(txt_file_path):
    """
    Read a whitespace-delimited text file (boxaverage output) and return the last numeric column
    as a 1D numpy array. Lines starting with '#' are skipped.
    """
    try:
        data = np.loadtxt(txt_file_path, comments='#')
        if data.ndim == 1:
            data = data.reshape(1, -1)
        return data[:, -1]
    except Exception as e:
        print(f"Error reading last column from {txt_file_path}: {e}", file=sys.stderr)
        return None


def plot_stress_vs_displacement_files(stress_path, disp_path, outdir, chi, angle, component=None):
    """
    Read stress and displacement values from two boxaverage text files and plot stress vs displacement.
    Saves a PNG in `outdir` named with chi, angle and component when available.
    """
    stress_vals = read_last_column(stress_path)
    disp_vals = read_last_column(disp_path)
    if stress_vals is None or disp_vals is None:
        print("Error: could not read input files for stress-displacement plotting", file=sys.stderr)
        return False

    n = min(len(stress_vals), len(disp_vals))
    stress_vals = stress_vals[:n]
    disp_vals = disp_vals[:n]

    chi_str = format_value(chi)
    angle_str = format_value(angle)

    outdir = Path(outdir) if outdir else Path(stress_path).parent
    outdir.mkdir(parents=True, exist_ok=True)

    comp_tag = f"stress{component}" if component else "stress"
    out_name = f"{comp_tag}_vs_disp_chi_{chi_str}_angle_{angle_str}.png"
    out_path = outdir / out_name

    plt.figure()
    plt.plot(disp_vals, stress_vals, marker='o', linestyle='-')
    plt.xlabel('Displacement (boxaverage last column)')
    plt.ylabel('Stress')
    title_comp = f" {comp_tag}" if component else ""
    plt.title(f"Stress vs Displacement{title_comp} — chi={chi_str}, angle={angle_str}")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(str(out_path), dpi=150)
    plt.close()
    print(f"Saved stress vs displacement plot: {out_path}")
    return True

def main():
    args = parse_args()

    # If the user provided stressfile + displacementfile, produce a stress-vs-displacement plot
    if args.stressfile and args.displacementfile:
        ok = plot_stress_vs_displacement_files(args.stressfile, args.displacementfile, args.outdir, args.chi, args.angle, args.component)
        if not ok:
            sys.exit(1)
        if args.show:
            plt.show()
        sys.exit(0)

    infile = Path(args.infile)
    if not infile.is_file():
        print(f"Error: input file not found: {infile}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

