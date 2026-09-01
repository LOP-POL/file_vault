#!/usr/bin/env python3
"""
plot_vtk_stress.py

Reads a VTK file produced by pace2D's `data2vtk` using the VTK Python bindings (containing stress11,
stress22 and stress12 fields after a domain cut) and produces one 2D field
plot per stress component: x/y are the spatial axes of the domain, colour
(the plot's "z") is the stress value.

Usage:
    python3 plot_vtk_stress.py --vtk PATH --chi CHI --angle ANGLE --outdir DIR

Example:
    python3 plot_vtk_stress.py \
        --vtk transversely_iso_no_crack_chi_2.5_angle_0_vtk-00003.vtk \
        --chi 2.5 --angle 0 --outdir ./plots
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")  # safe default for headless/batch runs; --show still works
import matplotlib.pyplot as plt

try:
    import vtk
    from vtkmodules.vtkIOLegacy import vtkDataSetReader, vtkStructuredPointsReader
    from vtkmodules.util import numpy_support
except ImportError:
    print("Error: the VTK Python bindings are required in this Python environment.",
          file=sys.stderr)
    sys.exit(1)

# Stress components to look for and plot. Values are (search_token, LaTeX label).
COMPONENTS = [
    ("stress11", r"$\sigma_{11}$"),
    ("stress22", r"$\sigma_{22}$"),
    ("stress12", r"$\sigma_{12}$"),  # covers stress21 by symmetry
]


def parse_args():
    parser = argparse.ArgumentParser(description="Plot stress fields from a data2vtk output file.")
    parser.add_argument("--vtk", required=True, help="Path to the .vtk file to read")
    parser.add_argument("--chi", required=True, type=float, help="chi value for this run")
    parser.add_argument("--angle", required=True, type=float, help="Anisotropy angle (degrees) for this run")
    parser.add_argument("--outdir", required=True, help="Directory to save the plots in")
    parser.add_argument("--show", action="store_true", help="Also display each plot interactively")
    return parser.parse_args()


def format_value(value):
    """Format a chi/angle value without a trailing '.0' for whole numbers."""
    if float(value).is_integer():
        return str(int(value))
    return str(value)


def read_vtk_file(vtk_path):
    """
    Read a legacy .vtk file using VTK.

    Returns:
        points: NumPy array of point coordinates
        point_data: dictionary mapping array names to NumPy arrays
        cell_data: dictionary mapping array names to NumPy arrays
        dataset: original VTK dataset
    """
    reader = vtkStructuredPointsReader()
    reader.SetFileName(str(vtk_path))
    reader.Update()

    dataset = reader.GetOutput()

    if dataset is None or dataset.GetNumberOfPoints() == 0:
        raise RuntimeError(f"Could not read valid VTK data from {vtk_path}")

    vtk_points = dataset.GetPoints()
    if vtk_points is None:
        raise RuntimeError(f"No point coordinates found in {vtk_path}")

    points = numpy_support.vtk_to_numpy(vtk_points.GetData())

    point_data = {}
    vtk_point_data = dataset.GetPointData()
    for i in range(vtk_point_data.GetNumberOfArrays()):
        array = vtk_point_data.GetArray(i)
        if array is not None and array.GetName():
            point_data[array.GetName()] = numpy_support.vtk_to_numpy(array)

    cell_data = {}
    vtk_cell_data = dataset.GetCellData()
    for i in range(vtk_cell_data.GetNumberOfArrays()):
        array = vtk_cell_data.GetArray(i)
        if array is not None and array.GetName():
            cell_data[array.GetName()] = numpy_support.vtk_to_numpy(array)

    return points, point_data, cell_data, dataset


def find_field(point_data, cell_data, token):
    """
    Look for a data array whose name contains `token` (case-insensitive),
    checking point data first, then cell data.

    Returns (name, array, "point" or "cell") or
    (None, None, None) if nothing matches.
    """
    for name, array in point_data.items():
        if token.lower() in name.lower():
            return name, np.asarray(array).reshape(-1), "point"

    for name, array in cell_data.items():
        if token.lower() in name.lower():
            return name, np.asarray(array).reshape(-1), "cell"

    return None, None, None

def build_grid(x, y, values):
    """
    Turn scattered/structured (x, y, value) triples into a regular 2D grid
    suitable for pcolormesh, without assuming any particular point ordering.
    """
    x_axis = np.unique(x)
    y_axis = np.unique(y)
    grid = np.full((len(y_axis), len(x_axis)), np.nan)

    x_idx = np.searchsorted(x_axis, x)
    y_idx = np.searchsorted(y_axis, y)
    grid[y_idx, x_idx] = values

    return x_axis, y_axis, grid


def main():
    args = parse_args()

    vtk_path = Path(args.vtk)
    if not vtk_path.is_file():
        print(f"Error: VTK file not found: {vtk_path}", file=sys.stderr)
        sys.exit(1)

    try:
        points, point_data, cell_data, dataset = read_vtk_file(vtk_path)
    except Exception as e:
        print(f"Error reading VTK file {vtk_path}: {e}", file=sys.stderr)
        sys.exit(1)

    x_coords, y_coords = points[:, 0], points[:, 1]

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    chi_str = format_value(args.chi)
    angle_str = format_value(args.angle)

    available_point_keys = list(point_data.keys())
    available_cell_keys = list(cell_data.keys())

    made_any_plot = False
    for token, label in COMPONENTS:
        name, values, kind = find_field(point_data, cell_data, token)
        if values is None:
            print(f"WARNING: no field matching '{token}' found in {vtk_path.name} "
                  f"(point_data keys: {available_point_keys}, cell_data keys: {available_cell_keys}) "
                  f"-- skipping this component.", file=sys.stderr)
            continue

        if kind == "cell":
            # Cell data has one value per cell, not per point. Use cell-centre
            # coordinates so the values can still be placed on a 2D grid.
            cells_x, cells_y = [], []

            for i in range(dataset.GetNumberOfCells()):
                cell = dataset.GetCell(i)
                point_ids = cell.GetPointIds()

                coords = []
                for j in range(point_ids.GetNumberOfIds()):
                    point_id = point_ids.GetId(j)
                    coords.append(points[point_id])

                coords = np.asarray(coords)
                cells_x.append(coords[:, 0].mean())
                cells_y.append(coords[:, 1].mean())

            x_use = np.asarray(cells_x)
            y_use = np.asarray(cells_y)
        else:
            x_use, y_use = x_coords, y_coords

        x_axis, y_axis, grid = build_grid(x_use, y_use, values)

        fig, ax = plt.subplots(figsize=(7, 6))
        mesh_plot = ax.pcolormesh(x_axis, y_axis, grid, shading="auto", cmap="viridis")
        cbar = fig.colorbar(mesh_plot, ax=ax)
        cbar.set_label(label)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_aspect("equal", adjustable="box")
        ax.set_title(f"{label} field — chi = {chi_str}, angle = {angle_str}°")
        fig.tight_layout()

        # token (e.g. "stress11") is used as the "dimension" tag in the filename
        out_name = f"{token}_chi_{chi_str}_angle_{angle_str}.png"
        out_path = outdir / out_name
        fig.savefig(str(out_path), dpi=150)
        plt.close(fig)
        print(f"Saved plot to: {out_path}")
        made_any_plot = True

        if args.show:
            plt.show()

    if not made_any_plot:
        print(f"Error: none of stress11/stress22/stress12 were found in {vtk_path}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
