#!/usr/bin/env python3
"""
plot_stress_vs_disp_multiple.py

Plot stress vs displacement curves for multiple runs.

Modes:
  --mode angle --angle <ANGLE> : overlay curves for different chi values at this angle
  --mode chi   --chi <CHI>     : overlay curves for different angles at this chi

Requires `get_data.sh` to have produced boxaverage txt files under each run's `domain_cut_analysis`.

Figures are written as PDF (for LaTeX, include them WITHOUT width=...) plus a PNG preview.
Size and fonts come from thesis_style.py.
"""

import re
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import thesis_style as ts

ts.apply()


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


def overlay_curves(curves, component, out_stem, width):
    """
    curves    : list of (legend_label, run_folder)
    component : '22' or '11'
    out_stem  : output path without extension
    width     : fraction of the text width
    """
    fig, ax = plt.subplots(figsize=ts.figsize(width))
    plotted = 0
    for label, folder in curves:
        work = folder / 'domain_cut_analysis'
        stress_file = work / f"{folder.name}_stress{component}_boxavg.txt"
        disp_file = work / f"{folder.name}_Ux_boxavg.txt"
        if not stress_file.exists() or not disp_file.exists():
            print(f"Skipping {folder}: missing boxavg files", file=sys.stderr)
            continue
        s = read_last_column(str(stress_file))
        d = read_last_column(str(disp_file))
        if s is None or d is None:
            continue
        n = min(len(s), len(d))
        ax.plot(d[:n], s[:n], label=label)
        plotted += 1

    ax.set_xlabel(r"$\bar{u}$ [mm]")
    ax.set_ylabel(rf"$\sigma_{{{component}}} [GPa]$")
    if plotted:
        ax.legend()
    ts.save(fig, out_stem)
    plt.close(fig)


def plot_mode_angle(parent_dir, angle, outdir, width):
    runs = collect_runs(parent_dir)
    selected = [(chi, f) for (chi, a, f) in runs if float(a) == float(angle)]
    if not selected:
        print(f"No runs for angle {angle}", file=sys.stderr)
        return False
    selected.sort(key=lambda x: x[0])
    curves = [(rf"$\chi={chi}$ [GPa]", f) for chi, f in selected]

    outdir = Path(outdir) if outdir else Path(parent_dir)
    overlay_curves(curves, "22", outdir / f"stress22_vs_disp_angle_{angle}", width)
    overlay_curves(curves, "11", outdir / f"stress11_vs_disp_angle_{angle}", width)
    return True


def plot_mode_chi(parent_dir, chi, outdir, width):
    runs = collect_runs(parent_dir)
    selected = [(a, f) for (c, a, f) in runs if float(c) == float(chi)]
    if not selected:
        print(f"No runs for chi {chi}", file=sys.stderr)
        return False
    selected.sort(key=lambda x: float(x[0]))
    curves = [(rf"$\theta={angle}^\circ$", f) for angle, f in selected]

    outdir = Path(outdir) if outdir else Path(parent_dir)
    # NOTE: in the original script both figures were saved under the same name
    # (stress_vs_disp_chi_<chi>.png), so the sigma_11 plot overwrote the sigma_22 plot.
    overlay_curves(curves, "22", outdir / f"stress22_vs_disp_chi_{chi}", width)
    overlay_curves(curves, "11", outdir / f"stress11_vs_disp_chi_{chi}", width)
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Plot stress vs displacement for multiple runs")
    parser.add_argument("--parent_dir", required=True)
    parser.add_argument("--mode", choices=["angle", "chi"], required=True)
    parser.add_argument("--angle", default=None)
    parser.add_argument("--chi", default=None)
    parser.add_argument("--outdir", default=None)
    parser.add_argument("--width", type=float, default=0.8,
                        help="figure width as a fraction of the LaTeX text width "
                             "(1.0 = full width, 0.48 = two side by side). Default 0.8")
    args = parser.parse_args()

    if args.mode == 'angle':
        if args.angle is None:
            print("--angle required for mode=angle", file=sys.stderr)
            sys.exit(1)
        plot_mode_angle(args.parent_dir, args.angle, args.outdir, args.width)
    else:
        if args.chi is None:
            print("--chi required for mode=chi", file=sys.stderr)
            sys.exit(1)
        plot_mode_chi(args.parent_dir, args.chi, args.outdir, args.width)


if __name__ == '__main__':
    main()
