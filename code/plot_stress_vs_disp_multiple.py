#!/usr/bin/env python3
"""
plot_stress_vs_disp_multiple.py

Plot stress vs displacement curves for multiple runs.

Modes:
  --mode angle --angle <ANGLE> : overlay curves for different chi values at this angle
  --mode chi   --chi <CHI>     : overlay curves for different angles at this chi

Requires `get_data.sh` to have produced boxaverage txt files under each run's `domain_cut_analysis`.
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


def collect_runs(parent_dir):
    p = Path(parent_dir)
    runs = []
    patt = re.compile(r"chi_([0-9.]+)_angle_([0-9.]+)")
    for f in p.iterdir():
        if not f.is_dir():
            continue
        m = patt.search(f.name)
        if not m:
            continue
        chi = float(m.group(1))
        angle = float(m.group(2))
        runs.append((chi, angle, f))
    return runs


def plot_mode_angle(parent_dir, angle, outdir):
    runs = collect_runs(parent_dir)
    selected = [(chi, f) for (chi, a, f) in runs if float(a) == float(angle)]
    if not selected:
        print(f"No runs for angle {angle}", file=sys.stderr)
        return False
    selected.sort(key=lambda x: x[0])

    plt.figure()
    for chi, folder in selected:
        work = folder / 'domain_cut_analysis'
        stress_file = work / f"{folder.name}_stress22_boxavg.txt"
        disp_file = work / f"{folder.name}_Uy_boxavg.txt"
        if not stress_file.exists() or not disp_file.exists():
            print(f"Skipping {folder}: missing boxavg files", file=sys.stderr)
            continue
        s = read_last_column(str(stress_file))
        d = read_last_column(str(disp_file))
        if s is None or d is None:
            continue
        n = min(len(s), len(d))
        plt.plot(d[:n], s[:n], label=f"chi={chi}")

    plt.xlabel('Displacement')
    plt.ylabel('Stress')
    plt.title(f"Stress vs Displacement — angle={angle}")
    plt.legend()
    plt.grid(True)
    outdir = Path(outdir) if outdir else Path(parent_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    fname = outdir / f"stress22_vs_disp_angle_{angle}.png"
    plt.tight_layout()
    plt.savefig(str(fname), dpi=150)
    print(f"Saved: {fname}")
   


    plt.figure()
    for chi, folder in selected:
        work = folder / 'domain_cut_analysis'
        stress_file = work / f"{folder.name}_stress11_boxavg.txt"
        disp_file = work / f"{folder.name}_Uy_boxavg.txt"
        if not stress_file.exists() or not disp_file.exists():
            print(f"Skipping {folder}: missing boxavg files", file=sys.stderr)
            continue
        s11 = read_last_column(str(stress_file))
        d11 = read_last_column(str(disp_file))
        if s11 is None or d11 is None:
            continue
        n = min(len(s11), len(d11))
        plt.plot(d11[:n], s11[:n], label=f"chi={chi}")

    plt.xlabel('Displacement')
    plt.ylabel('Stress')
    plt.title(f"Stress vs Displacement — angle={angle}")
    plt.legend()
    plt.grid(True)
    outdir = Path(outdir) if outdir else Path(parent_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    fname = outdir / f"stress11_vs_disp_angle_{angle}.png"
    plt.tight_layout()
    plt.savefig(str(fname), dpi=150)
    print(f"Saved: {fname}")
    return True

def plot_mode_chi(parent_dir, chi, outdir):
    runs = collect_runs(parent_dir)
    selected = [(a, f) for (c, a, f) in runs if float(c) == float(chi)]
    if not selected:
        print(f"No runs for chi {chi}", file=sys.stderr)
        return False
    selected.sort(key=lambda x: float(x[0]))

    plt.figure()
    for angle, folder in selected:
        work = folder / 'domain_cut_analysis'
        stress_file = work / f"{folder.name}_stress22_boxavg.txt"
        disp_file = work / f"{folder.name}_Uy_boxavg.txt"
        if not stress_file.exists() or not disp_file.exists():
            print(f"Skipping {folder}: missing boxavg files", file=sys.stderr)
            continue
        s = read_last_column(str(stress_file))
        d = read_last_column(str(disp_file))
        if s is None or d is None:
            continue
        n = min(len(s), len(d))
        plt.plot(d[:n], s[:n], label=f"angle={angle}")

    plt.xlabel('Displacement')
    plt.ylabel('Stress')
    plt.title(f"Stress vs Displacement — chi={chi}")
    plt.legend()
    plt.grid(True)
    outdir = Path(outdir) if outdir else Path(parent_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    fname = outdir / f"stress_vs_disp_chi_{chi}.png"
    plt.tight_layout()
    plt.savefig(str(fname), dpi=150)
    print(f"Saved: {fname}")
  

    plt.figure()
    for angle, folder in selected:
        work = folder / 'domain_cut_analysis'
        stress_file = work / f"{folder.name}_stress11_boxavg.txt"
        disp_file = work / f"{folder.name}_Uy_boxavg.txt"
        if not stress_file.exists() or not disp_file.exists():
            print(f"Skipping {folder}: missing boxavg files", file=sys.stderr)
            continue
        s11 = read_last_column(str(stress_file))
        d11 = read_last_column(str(disp_file))
        if s11 is None or d11 is None:
            continue
        n = min(len(s11), len(d11))
        plt.plot(d11[:n], s11[:n], label=f"angle={angle}")
    
    plt.xlabel('Displacement')
    plt.ylabel('Stress')
    plt.title(f"Stress vs Displacement — chi={chi}")
    plt.legend()
    plt.grid(True)
    outdir = Path(outdir) if outdir else Path(parent_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    fname = outdir / f"stress_vs_disp_chi_{chi}.png"
    plt.tight_layout()
    plt.savefig(str(fname), dpi=150)
    print(f"Saved: {fname}")
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Plot stress vs displacement for multiple runs")
    parser.add_argument("--parent_dir", required=True)
    parser.add_argument("--mode", choices=["angle", "chi"], required=True)
    parser.add_argument("--angle", default=None)
    parser.add_argument("--chi", default=None)
    parser.add_argument("--outdir", default=None)
    args = parser.parse_args()

    if args.mode == 'angle':
        if args.angle is None:
            print("--angle required for mode=angle", file=sys.stderr)
            sys.exit(1)
        plot_mode_angle(args.parent_dir, args.angle, args.outdir)
    else:
        if args.chi is None:
            print("--chi required for mode=chi", file=sys.stderr)
            sys.exit(1)
        plot_mode_chi(args.parent_dir, args.chi, args.outdir)


if __name__ == '__main__':
    main()
