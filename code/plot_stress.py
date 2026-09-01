#!/usr/bin/env python3
"""
plot_stress.py

Reads a pace2D stress output .dat file (two whitespace-separated columns:
grid index, stress value) and produces a plot labeled with the chi and
anisotropy-angle values for that run.

Usage:
    python3 plot_stress.py --infile PATH --chi CHI --angle ANGLE [--outdir DIR] [--show]

Example:
    python3 plot_stress.py --infile stress11_frame3of3_X-50-102.dat --chi 2.5 --angle 45
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
    parser = argparse.ArgumentParser(description="Plot a pace2D stress .dat file.")
    parser.add_argument("--infile", required=True, help="Path to the stress .dat file")
    parser.add_argument("--chi", required=True, type=float, help="chi value for this run")
    parser.add_argument("--angle", required=True, type=float, help="Anisotropy angle (degrees) for this run")
    parser.add_argument("--outdir", default=None,
                         help="Directory to save the plot in (default: same directory as --infile)")
    parser.add_argument("--show", action="store_true", help="Also display the plot interactively")
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


def main():
    args = parse_args()

    infile = Path(args.infile)
    if not infile.is_file():
        print(f"Error: input file not found: {infile}", file=sys.stderr)
        sys.exit(1)

    data = np.loadtxt(infile)
    if data.ndim != 2 or data.shape[1] < 2:
        print(f"Error: expected two columns (index, value) in {infile}, got shape {data.shape}",
              file=sys.stderr)
        sys.exit(1)

    index_col, value_col = data[:, 0], data[:, 1]

    component, frame, x_range = parse_filename_metadata(infile.name)
    stress_label = f"$\\sigma_{{{component}}}$" if component else "Stress"

    # Prefer plotting against the physical X range encoded in the filename,
    # if it's there and matches the number of data points; otherwise fall
    # back to the raw index column from the file.
    if x_range is not None:
        x_values = np.linspace(x_range[0], x_range[1], len(index_col))
        x_label = "Position, X"
    else:
        x_values = index_col
        x_label = "Grid index"

    chi_str = format_value(args.chi)
    angle_str = format_value(args.angle)

    title = f"{stress_label} vs {x_label} — chi = {chi_str}, angle = {angle_str}°"
    if frame is not None:
        title += f" (frame {frame[0]} of {frame[1]})"

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x_values, value_col, marker="o", markersize=3, linewidth=1)
    ax.set_xlabel(x_label)
    ax.set_ylabel(stress_label)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()

    outdir = Path(args.outdir) if args.outdir else infile.parent
    outdir.mkdir(parents=True, exist_ok=True)

    comp_tag = f"stress{component}" if component else "stress"
    out_name = f"{comp_tag}_chi_{chi_str}_angle_{angle_str}.png"
    out_path = outdir / out_name
    fig.savefig(out_path, dpi=150)
    print(f"Saved plot to: {out_path}")

    if args.show:
        plt.show()


if __name__ == "__main__":
    main()
