#!/usr/bin/env python3
"""
stress22_by_chi.py

Plot stress22 (single-value per run from boxaverage) vs chi for a given angle.

Usage:
  python3 stress22_by_chi.py --parent_dir /path/to/results --angle 0 --outdir /path/to/plots

The script looks for folders named like:
  transversely_iso_no_crack_chi_<CHI>_angle_<ANGLE>_... 
and expects the get_data.sh script to have produced:
  <folder>/domain_cut_analysis/<FOLDER_NAME>_stress22_boxavg.txt

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


def find_folders(parent_dir, angle):
    p = Path(parent_dir)
    pattern = re.compile(rf"chi_([0-9.]+)_angle_{re.escape(str(angle))}")
    folders = []
    for f in p.iterdir():
        if not f.is_dir():
            continue
        m = pattern.search(f.name)
        if m:
            chi = float(m.group(1))
            folders.append((chi, f))
    folders.sort(key=lambda x: x[0])
    return folders


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Plot stress22 vs chi for a given angle")
    parser.add_argument("--parent_dir", required=True)
    parser.add_argument("--angle", required=True)
    parser.add_argument("--outdir", default=None)
    args = parser.parse_args()

    folders = find_folders(args.parent_dir, args.angle)
    if not folders:
        print(f"No folders found for angle {args.angle} in {args.parent_dir}", file=sys.stderr)
        sys.exit(1)

    chis = []
    stresses = []
    for chi, folder in folders:
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
        chis.append(chi)
        stresses.append(val)

    if not chis:
        print("No valid stress data found.", file=sys.stderr)
        sys.exit(1)

    outdir = Path(args.outdir) if args.outdir else Path(args.parent_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    plt.figure()
    plt.plot(chis, stresses, marker='o', linestyle='-')
    plt.xlabel('chi')
    plt.ylabel('Stress22 (final boxaverage value)')
    plt.title(f"Stress22 vs chi — angle={args.angle}")
    plt.grid(True)
    fname = outdir / f"stress22_vs_chi_angle_{args.angle}.png"
    plt.tight_layout()
    plt.savefig(str(fname), dpi=150)
    print(f"Saved: {fname}")


if __name__ == '__main__':
    main()
