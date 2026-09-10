#!/usr/bin/env python3
"""
stress_by_angle.py

Plot stress (single-value per run from boxaverage) vs angle for a given chi.

Usage:
    python3 stress_by_angle.py --parent_dir /path/to/results --chi 0.5 --outdir /path/to/plots

The script looks for folders named like:
  transversely_iso_no_crack_chi_<CHI>_angle_<ANGLE>_... 
and expects the get_data.sh script to have produced:
  <folder>/domain_cut_analysis/<FOLDER_NAME>_stress22_boxavg.txt
  <folder>/domain_cut_analysis/<FOLDER_NAME>_stress11_boxavg.txt

It reads the last numeric column from each boxavg file and takes the final value as the representative stress.
"""

import re
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def read_last_column(txt_file_path):
    try:
        data = np.loadtxt(txt_file_path, comments='#')
        if data.ndim == 1:
            data = data.reshape(1, -1)
        return data[:, -1]
    except Exception as e:
        print(f"Error reading {txt_file_path}: {e}", file=sys.stderr)
        return None


def find_folders(parent_dir, chi):
    p = Path(parent_dir)
    pattern = re.compile(r"chi_([0-9.]+)_angle_([0-9.]+)")
    folders = []
    for f in p.iterdir():
        if not f.is_dir():
            continue
        m = pattern.search(f.name)
        if m and float(m.group(1)) == float(chi):
            angle = float(m.group(2))
            folders.append((angle, f))
    folders.sort(key=lambda x: x[0])
    return folders


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Plot stress vs angle for a given chi")
    parser.add_argument("--parent_dir", required=True)
    parser.add_argument("--chi", required=True)
    parser.add_argument("--outdir", default=None)
    args = parser.parse_args()

    folders = find_folders(args.parent_dir, args.chi)
    if not folders:
        print(f"No folders found for chi {args.chi} in {args.parent_dir}", file=sys.stderr)
        sys.exit(1)

    angles = []
    angles11 = []
    stresses = []

    stresses11 = []
    for angle, folder in folders:
        work = folder / 'domain_cut_analysis'
        # boxavg filename pattern
        fname = f"{folder.name}_stress22_boxavg.txt"
        fpath = work / fname
        if not fpath.exists():
            print(f"Warning: missing {fpath}, skipping", file=sys.stderr)
            continue
        arr = read_last_column(str(fpath))
        if arr is None or len(arr) == 0:
            print(f"Warning: empty data in {fpath}", file=sys.stderr)
            continue
        val = float(arr[-1])
        angles.append(angle)
        stresses.append(val)

    for angle, folder in folders:
        work = folder / 'domain_cut_analysis'
        # boxavg filename pattern
        fname11 = f"{folder.name}_stress11_boxavg.txt"
        fpath11 = work / fname11
        if not fpath11.exists():
            print(f"Warning: missing {fpath11}, skipping", file=sys.stderr)
            continue
        arr = read_last_column(str(fpath11))
        if arr is None or len(arr) == 0:
            print(f"Warning: empty data in {fpath11}", file=sys.stderr)
            continue
        val = float(arr[-1])
        angles11.append(angle)
        stresses11.append(val)

    if not angles:
        print("No valid stress data found.", file=sys.stderr)
        sys.exit(1)

    outdir = Path(args.outdir) if args.outdir else Path(args.parent_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    plt.figure()
    plt.plot(angles, stresses, marker='o', linestyle='-',)
    for xi, yi in zip(angles, stresses):
        plt.text(xi, yi, str(yi), ha='center', va='bottom')
    plt.xlabel('angle')
    plt.ylabel('Stress22 (final boxaverage value)')
    plt.title(f"Stress22 vs angle — chi={args.chi}")
    plt.grid(True)
    fname = outdir / f"stress22_vs_angle_chi_{args.chi}.png"
    plt.tight_layout()
    plt.savefig(str(fname), dpi=150)
    print(f"Saved: {fname}")

    plt.figure()
    plt.plot(angles11, stresses11, marker='o', linestyle='-')
    for xi, yi in zip(angles11, stresses11):
        plt.text(xi, yi, str(yi), ha='center', va='bottom')
    plt.xlabel('angle')
    plt.ylabel('Stress11 (final boxaverage value)')
    plt.title(f"Stress11 vs angle — chi={args.chi}")
    plt.grid(True)
    fname11 = outdir / f"stress11_vs_angle_chi_{args.chi}.png"
    plt.tight_layout()
    plt.savefig(str(fname11), dpi=150)
    print(f"Saved: {fname11}")


if __name__ == '__main__':
    main()
