#!/bin/bash

################################################################################
# get_data.sh
#
# Processes simulation output folders to extract stress data via domain cuts,
# convert to VTK format, and generate stress plots.
#
# Usage:
#     bash get_data.sh <parent_dir> [--outdir OUTPUT_DIR]
#
# Example:
#     bash get_data.sh /path/to/results --outdir /path/to/plots
#
# Requirements:
#   - domaincut command available (for cutting domains)
#   - data2vtk command available (for VTK conversion)
#   - Python 3 with numpy and matplotlib
#   - plot_stress.py in the same directory as this script
#
################################################################################

set -e

# Default values
PARENT_DIR="${1:-.}"
OUTDIR=""

# Parse arguments
while [[ $# -gt 1 ]]; do
    case "$2" in
        --outdir)
            OUTDIR="$3"
            shift 2
            ;;
        *)
            echo "Unknown option: $2"
            exit 1
            ;;
    esac
done

# Validate parent directory
if [[ ! -d "$PARENT_DIR" ]]; then
    echo "Error: Parent directory not found: $PARENT_DIR"
    exit 1
fi

# Set output directory
if [[ -z "$OUTDIR" ]]; then
    OUTDIR="$PARENT_DIR/plots"
fi
mkdir -p "$OUTDIR"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLOT_SCRIPT="$SCRIPT_DIR/plot_stress.py"
PLOT_VTK_SCRIPT="$SCRIPT_DIR/plot_vtk_stress.py"

if [[ ! -f "$PLOT_SCRIPT" ]]; then
    echo "Error: plot_stress.py not found at $PLOT_SCRIPT"
    exit 1
fi

if [[ ! -f "$PLOT_VTK_SCRIPT" ]]; then
    echo "Error: plot_vtk_stress.py not found at $PLOT_VTK_SCRIPT"
    exit 1
fi

echo "Processing simulation folders in: $PARENT_DIR"
echo "Output directory: $OUTDIR"
echo "Plot script: $PLOT_SCRIPT"
echo ""

# Define stress components to process
STRESS_COMPONENTS=("11" "22" "21")
DOMAIN_OFFSET_X=0
DOMAIN_OFFSET_Y=0
DOMAIN_END_X=50
DOMAIN_END_Y=50

# Counter for processed folders
FOLDER_COUNT=0

# Process each folder matching the simulation naming pattern
for folder in "$PARENT_DIR"/transversely_iso_no_crack_chi_*_angle_*; do
    [[ -d "$folder" ]] || continue
    
    FOLDER_COUNT=$((FOLDER_COUNT + 1))
    FOLDER_NAME=$(basename "$folder")
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Processing folder: $FOLDER_NAME"
    
    # Extract chi and angle from folder name
    # Pattern: transversely_iso_no_crack_chi_<CHI>_angle_<ANGLE>_<DATE>_<TIME>
    if [[ $FOLDER_NAME =~ chi_([0-9.]+)_angle_([0-9.]+) ]]; then
        CHI="${BASH_REMATCH[1]}"
        ANGLE="${BASH_REMATCH[2]}"
        echo "  Extracted: chi=$CHI, angle=$ANGLE"
    else
        echo "  WARNING: Could not extract chi and angle from folder name, skipping"
        continue
    fi
    
    # Create temporary working directory for domain cuts and VTK files
    WORK_DIR="$folder/domain_cut_analysis"
    mkdir -p "$WORK_DIR"
    
    echo "  Creating domain cuts and VTK files..."
    
    # Process each stress component
    for COMPONENT in "${STRESS_COMPONENTS[@]}"; do
        STRESS_FILE="$folder/${FOLDER_NAME}.SolidMechanics_stress${COMPONENT}.p3s"
        
        if [[ ! -f "$STRESS_FILE" ]]; then
            echo "    WARNING: Stress file not found: $STRESS_FILE"
            continue
        fi
        
        # Create domain cut file
        DOMAIN_CUT_FILE="$WORK_DIR/${FOLDER_NAME}_stress${COMPONENT}_cut.p3s"
        SIMGEO_FILE="$folder/${FOLDER_NAME}.p3simgeo"
        
        if [[ ! -f "$SIMGEO_FILE" ]]; then
            echo "    WARNING: SimGeo file not found: $SIMGEO_FILE"
            continue
        fi
        
        echo "    Creating domain cut for stress${COMPONENT}..."
        if domaincut "$STRESS_FILE" "$DOMAIN_CUT_FILE" \
            -x "$DOMAIN_OFFSET_X" -X "$DOMAIN_END_X" \
            -y "$DOMAIN_OFFSET_Y" -Y "$DOMAIN_END_Y" \
            -f 2>/dev/null; then
            echo "      Domain cut created: $DOMAIN_CUT_FILE"
        else
            echo "      WARNING: domaincut failed for stress${COMPONENT}"
            continue
        fi
        
        # Also create domain cut for the geometry file
        SIMGEO_DOM_CUT_FILE="$WORK_DIR/${FOLDER_NAME}_stress${COMPONENT}_cut.p3simgeo"
    
        # Create VTK file
        VTK_BASE="$WORK_DIR/stress${COMPONENT}_vtk"
        echo "    Converting to VTK format for stress${COMPONENT}..."
        
         # Error with folder names that had decimal places
         if [[ ! -f "$WORK_DIR/${FOLDER_NAME}_stress${COMPONENT}_cut.p3simgeo" ]]; then
            for file in "$WORK_DIR"/*.p3simgeo; do
                [[ -f "$file" ]] || continue
                mv "$file" "$WORK_DIR/${FOLDER_NAME}_stress${COMPONENT}_cut.p3simgeo"
                echo "Renamed the file"
                echo "$WORK_DIR/${FOLDER_NAME}_stress${COMPONENT}_cut.p3simgeo"
	        done	
        fi
        
        if data2vtk "$SIMGEO_DOM_CUT_FILE"\
            -d "$DOMAIN_CUT_FILE" \
            -a \
            "$VTK_BASE" 2>/dev/null       
            ;
            then
            echo "      VTK files created: ${VTK_BASE}*.vtk"
        else
            echo "      WARNING: data2vtk failed for stress${COMPONENT}"
            continue
        fi
        
        # Generate plots using both plot_stress.py and plot_vtk_stress.py
        echo "    Generating plots for stress${COMPONENT}..."
        
        # Find all VTK files for this component and use the last frame
        VTK_FILES=(${VTK_BASE}-*.vtk)
        if [[ ${#VTK_FILES[@]} -eq 0 ]]; then
            echo "      WARNING: No VTK files found matching pattern: ${VTK_BASE}-*.vtk"
            continue
        fi
        
        # Get the last VTK file (highest frame number)
        VTK_FILE="${VTK_FILES[-1]}"
        NUM_FRAMES=${#VTK_FILES[@]}
        echo "      Found $NUM_FRAMES frames, using last frame: $(basename "$VTK_FILE")"
        
        # 1. Generate 1D line plot using plot_stress.py
        echo "      Generating 1D stress profile plot..."
        if python3 "$PLOT_SCRIPT" \
            --infile "$VTK_FILE" \
            --chi "$CHI" \
            --angle "$ANGLE" \
            --component "$COMPONENT" \
            --outdir "$OUTDIR" 2>/dev/null; then
            echo "        1D plot generated successfully"
        else
            echo "        WARNING: 1D plot generation failed for stress${COMPONENT}"
        fi
    done
    
    # 2. Generate 2D field plots using plot_vtk_stress.py (all stress components at once)
    # Find any VTK file from the first component to pass to the 2D plotting script
    VTK_BASE_11="$WORK_DIR/stress11_vtk"
    VTK_FILES_11=(${VTK_BASE_11}-*.vtk)
    if [[ ${#VTK_FILES_11[@]} -gt 0 ]]; then
        VTK_FILE_FOR_2D="${VTK_FILES_11[-1]}"
        echo "    Generating 2D field plots for all stress components..."
        if python3 "$PLOT_VTK_SCRIPT" \
            --vtk "$VTK_FILE_FOR_2D" \
            --chi "$CHI" \
            --angle "$ANGLE" \
            --outdir "$OUTDIR" 2>/dev/null; then
            echo "      2D field plots generated successfully (stress11, stress22, stress12)"
        else
            echo "      WARNING: 2D field plot generation failed"
        fi
    else
        echo "    WARNING: Could not find VTK files for 2D plotting"
    fi
    
    echo "  Folder processing complete"
    echo ""
done

echo "==============================================="
echo "Processing complete!"
echo "Processed folders: $FOLDER_COUNT"
echo "Plots saved to: $OUTDIR"
echo "==============================================="
