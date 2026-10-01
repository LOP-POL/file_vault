import argparse
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

import re
import sys
from scipy.interpolate import griddata


try:
    import vtk
    from vtkmodules.vtkIOLegacy import vtkDataSetReader, vtkStructuredPointsReader
    from vtkmodules.util import numpy_support
    HAS_VTK = True
except ImportError:
    HAS_VTK = False

def fix_vtk_scalars_header(vtk_file_path):
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
                    scalar_name = "driving_force"
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
    fix_vtk_scalars_header(vtk_file_path)
    
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

def parse_args():
    parser = argparse.ArgumentParser(description="Plot stress data from .dat or .vtk files.")
    parser.add_argument("--infile", required=True, 
                        help="Path to the stress file (.dat or .vtk)")
    parser.add_argument("--chi", default=None,
                        help="chi value for this run")
    parser.add_argument("--angle", default=None,
                        help="anisotropy angle for this run")
    parser.add_argument("--outdir", default=None,
                        help="Directory to save the plot in (default: same directory as --infile)")
    return parser.parse_args()

def manual_extraction(vtk_file_path):
    """
    Read scalar force data and mesh information from a VTK file.

    Returns:
        nx, ny: mesh dimensions
        force: 2D force magnitude array, shape (ny, nx)
        origin: (x0, y0, z0)
        spacing: (dx, dy, dz)
    """
    if not HAS_VTK:
        print(
            "Error: VTK support not available. "
            "Install python package: vtk",
            file=sys.stderr
        )
        return None

    fix_vtk_scalars_header(vtk_file_path)

    try:
        reader = vtkStructuredPointsReader()
        reader.SetFileName(str(vtk_file_path))
        reader.ReadAllVectorsOn()
        reader.ReadAllScalarsOn()
        reader.Update()

        output = reader.GetOutput()

        if (
            output.GetNumberOfCells() == 0
            and output.GetNumberOfPoints() == 0
        ):
            print(
                f"Error: VTK file is empty: {vtk_file_path}",
                file=sys.stderr
            )
            return None

        scalars = output.GetPointData().GetScalars()

        if scalars is None:
            print("Error: No scalar data found in VTK file.",
                  file=sys.stderr)
            return None

        force = numpy_support.vtk_to_numpy(scalars)

        # VTK dimensions: nx, ny, nz
        nx, ny, nz = output.GetDimensions()

        # Mesh information
        spacing = output.GetSpacing()
        origin = output.GetOrigin()

        # Reshape VTK's flat array into a 2D field
        force = force.reshape((ny, nx))

        return nx, ny, force, origin, spacing

    except Exception as e:
        print(
            f"Error reading VTK file: {e}",
            file=sys.stderr
        )
        return None

def plot_polar_contours(force, nx, ny, origin, spacing, outfile, chi, angle):

    x0, y0, _ = origin
    dx, dy, _ = spacing

    # ---------------------------------------------------------
    # Original Cartesian mesh
    # ---------------------------------------------------------

    x = x0 + np.arange(nx) * dx
    y = y0 + np.arange(ny) * dy

    X, Y = np.meshgrid(x, y)

    # ---------------------------------------------------------
    # Convert Cartesian coordinates to polar
    # ---------------------------------------------------------

    X_relative = X
    Y_relative = Y

    theta = np.arctan2(Y_relative, X_relative)
    radius = np.sqrt(X_relative**2 + Y_relative**2)

    # ---------------------------------------------------------
    # Create regular polar grid
    # ---------------------------------------------------------

    n_theta = 360
    n_radius = 150

    theta_new = np.linspace(-np.pi, np.pi, n_theta)
    radius_new = np.linspace(
        0,
        radius.max(),
        n_radius
    )

    THETA, R = np.meshgrid(
        theta_new,
        radius_new
    )

    # Convert polar grid back to Cartesian
    X_new = R * np.cos(THETA)
    Y_new = R * np.sin(THETA)

    # ---------------------------------------------------------
    # Interpolate force onto polar grid
    # ---------------------------------------------------------

    points = np.column_stack(
        (X.ravel(), Y.ravel())
    )

    force_polar = griddata(
        points,
        force.ravel(),
        (X_new, Y_new),
        method="linear"
    )

    # ---------------------------------------------------------
    # Plot contours
    # ---------------------------------------------------------

    fig, ax = plt.subplots(
        figsize=(8, 8),
        subplot_kw={"projection": "polar"}
    )

    levels = 15

    contour = ax.contour(
        THETA,
        R,
        force_polar,
        levels=levels,
        colors="black",
        linewidths=0.8
    )

    # Label the contour lines
    ax.clabel(
        contour,
        inline=True,
        fontsize=8,
        fmt="%.2f"
    )

    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)

    ax.set_thetamin(0)
    ax.set_thetamax(90)
    


    title = "Driving Force Contours"
    if chi is not None and angle is not None:
        title += f" - chi={chi}, angle={angle}"
    ax.set_title(title)

    plt.savefig(
        outfile,
        dpi=150,
        bbox_inches="tight"
    )

   

def main():
    args = parse_args()

    infile = Path(args.infile)

    if not infile.is_file():
        print(
            f"Error: input file not found: {infile}",
            file=sys.stderr
        )
        sys.exit(1)

    extraction = manual_extraction(infile)

    if extraction is None:
        sys.exit(1)

    nx, ny, force, origin, spacing = extraction

   

    # ---------------------------------------------------------
    # Construct the Cartesian mesh
    # ---------------------------------------------------------

    x0, y0, _ = origin
    dx, dy, _ = spacing

    x = x0 + np.arange(nx) * dx
    y = y0 + np.arange(ny) * dy

    X, Y = np.meshgrid(x, y)

    # ---------------------------------------------------------
    # Convert Cartesian coordinates -> polar coordinates
    # ---------------------------------------------------------

    theta = np.arctan2(Y, X)
    radius = np.sqrt(X**2 + Y**2)

    # ---------------------------------------------------------
    # Flatten the arrays
    # ---------------------------------------------------------

    theta_flat = theta.ravel()
    radius_flat = radius.ravel()
    force_flat = force.ravel()

    # ---------------------------------------------------------
    # Polar plot
    # ---------------------------------------------------------

    fig, ax = plt.subplots(
        figsize=(8, 8),
        subplot_kw={"projection": "polar"}
    )

    scatter = ax.scatter(
        theta_flat,
        radius_flat,
        c=force_flat,
        cmap="viridis",
        s=15
    )

    # Color bar = force magnitude
    cbar = fig.colorbar(
        scatter,
        ax=ax,
        pad=0.1
    )

    cbar.set_label("Force magnitude")

    title = "Driving Force"
    if args.chi is not None and args.angle is not None:
        title += f" - chi={args.chi}, angle={args.angle}"
    ax.set_title(title)

    # Put 0 degrees at the top
    #ax.set_theta_zero_location("N")

    # Make angle increase clockwise
    #ax.set_theta_direction(-1)

    ax.set_thetamin(0)
    ax.set_thetamax(90)
    # ax.set_rlim(0, 1.0)


    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    outdir = Path(args.outdir) if args.outdir else infile.parent
    outdir.mkdir(parents=True, exist_ok=True)

    outfile = outdir / f"{infile.stem}_polar.png"
    outfile_cont = outdir / f"{infile.stem}_con_polar.png"
    

    plt.savefig(
        outfile,
        dpi=150,
        bbox_inches="tight"
    )

    print(f"Saved plot to: {outfile}")
    plot_polar_contours(
        force, nx, ny, origin, spacing, outfile_cont, args.chi, args.angle
    )
if __name__ == "__main__":
    main()