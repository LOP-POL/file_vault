#!/usr/bin/env python3
"""Create polar visualizations of a scalar driving-force VTK frame."""

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def read_structured_points(path):
    """Read the ASCII STRUCTURED_POINTS subset emitted by data2vtk."""
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    dimensions = None
    spacing = None
    origin = None
    data_start = None

    for index, line in enumerate(lines):
        fields = line.split()
        if not fields:
            continue
        if fields[0] == "DIMENSIONS":
            dimensions = tuple(int(value) for value in fields[1:4])
        elif fields[0] == "SPACING":
            spacing = tuple(float(value) for value in fields[1:4])
        elif fields[0] == "ORIGIN":
            origin = tuple(float(value) for value in fields[1:4])
        elif fields[0] in {"LOOKUP_TABLE", "COLOR_SCALARS"}:
            data_start = index + 1
            break

    if dimensions is None or data_start is None:
        raise ValueError(f"Unsupported or incomplete VTK file: {path}")

    values = np.fromstring(" ".join(lines[data_start:]), sep=" ")
    expected = dimensions[0] * dimensions[1] * dimensions[2]
    if values.size < expected:
        raise ValueError(f"VTK file contains {values.size} values, expected {expected}")
    values = values[:expected].reshape((dimensions[1], dimensions[0]))
    spacing = spacing or (1.0, 1.0, 1.0)
    origin = origin or (0.0, 0.0, 0.0)
    return values, spacing, origin


def format_value(value):
    return str(int(value)) if float(value).is_integer() else str(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--infile", required=True, type=Path)
    parser.add_argument("--chi", required=True, type=float)
    parser.add_argument("--angle", required=True, type=float)
    parser.add_argument("--outdir", type=Path, default=None)
    args = parser.parse_args()

    values, spacing, origin = read_structured_points(args.infile)
    height, width = values.shape
    x = origin[0] + np.arange(width) * spacing[0]
    y = origin[1] + np.arange(height) * spacing[1]
    xx, yy = np.meshgrid(x, y)
    center_x = (x[0] + x[-1]) / 2.0
    center_y = (y[0] + y[-1]) / 2.0
    radius = np.hypot(xx - center_x, yy - center_y)
    theta = np.mod(np.arctan2(yy - center_y, xx - center_x), 2.0 * np.pi)

    outdir = args.outdir or args.infile.parent
    outdir.mkdir(parents=True, exist_ok=True)
    stem = f"driving_force_polar_chi_{format_value(args.chi)}_angle_{format_value(args.angle)}"

    figure = plt.figure(figsize=(9, 7), constrained_layout=True)
    axis = figure.add_subplot(111, projection="polar")
    image = axis.scatter(theta.ravel(), radius.ravel(), c=values.ravel(), s=8,
                         cmap="viridis", linewidths=0)
    axis.set_title(f"Crack driving force, chi={format_value(args.chi)}, "
                   f"angle={format_value(args.angle)} deg")
    figure.colorbar(image, ax=[axis], pad=0.1, label="Driving force")
    figure.savefig(outdir / f"{stem}.png", dpi=200)
    plt.close(figure)

    bins = np.linspace(0.0, 2.0 * np.pi, 181)
    bin_indices = np.digitize(theta.ravel(), bins) - 1
    angular_mean = np.array([
        values.ravel()[bin_indices == index].mean()
        if np.any(bin_indices == index) else np.nan
        for index in range(len(bins) - 1)
    ])
    angular_figure = plt.figure(figsize=(8, 5), constrained_layout=True)
    angular_axis = angular_figure.add_subplot(111, projection="polar")
    centers = (bins[:-1] + bins[1:]) / 2.0
    angular_axis.plot(np.r_[centers, centers[0]],
                      np.r_[angular_mean, angular_mean[0]], linewidth=1.5)
    angular_axis.set_title(f"Angular mean driving force, chi={format_value(args.chi)}, "
                           f"angle={format_value(args.angle)} deg")
    angular_figure.savefig(outdir / f"{stem}_angular_mean.png", dpi=200)
    plt.close(angular_figure)


if __name__ == "__main__":
    main()