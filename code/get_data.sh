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
#   - plot_driving_force_polar.py in the same directory as this script
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
PLOT_DISP_SCRIPT="$SCRIPT_DIR/plot_stress_vs_displacement.py"
PLOT_DRIVING_SCRIPT="$SCRIPT_DIR/plot_driving_force_polar.py"

if [[ ! -f "$PLOT_SCRIPT" ]]; then
    echo "Error: plot_stress.py not found at $PLOT_SCRIPT"
    exit 1
fi


if [[ ! -f "$PLOT_DISP_SCRIPT" ]]; then
    echo "Error: plot_stress_vs_displacement.py not found at $PLOT_DISP_SCRIPT"
    exit 1
fi

if [[ ! -f "$PLOT_DRIVING_SCRIPT" ]]; then
    echo "Error: plot_driving_force_polar.py not found at $PLOT_DRIVING_SCRIPT"
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
DOMAIN_END_X=100
DOMAIN_END_Y=100

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
    
    # Create domain cut + boxaverage for displacement (Uy)
    DISP_SRC="$folder/${FOLDER_NAME}.SolidMechanics_Uy.p3s"
    DISP_CUT="$WORK_DIR/${FOLDER_NAME}_Uy_cut.p3s"
    DISP_BOXAVG="$WORK_DIR/${FOLDER_NAME}_Uy_boxavg.txt"

    if [[ -f "$DISP_SRC" ]]; then
        echo "  Creating domain cut for displacement (Uy)..."
        if domaincut "$DISP_SRC" "$DISP_CUT" -x "$DOMAIN_OFFSET_X" -X "$DOMAIN_END_X" -y "$DOMAIN_OFFSET_Y" -Y "$DOMAIN_END_Y" -f 2>/dev/null; then
            echo "    Displacement domain cut created: $DISP_CUT"
            echo "  Running boxaveragecells for displacement..."
            if boxaveragecells "$DISP_CUT" -b ""[0,0,0],[0,100,0]"> "$DISP_BOXAVG" 2>/dev/null; then
                echo "    Displacement boxaverage saved: $DISP_BOXAVG"
            else
                echo "    WARNING: boxaveragecells failed for displacement"
            fi
        else
            echo "    WARNING: domaincut failed for displacement"
        fi
    else
        echo "    WARNING: Displacement source file not found: $DISP_SRC"
    fi
    
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

        # Run boxaverage on the stress domain-cut file to produce a txt summary
        STRESS_BOXAVG="$WORK_DIR/${FOLDER_NAME}_stress${COMPONENT}_boxavg.txt"
        echo "    Running boxaveragecells for stress${COMPONENT}..."
        if boxaveragecells "$DOMAIN_CUT_FILE" -b "[0,0,0],[0,100,0]" > "$STRESS_BOXAVG" 2>/dev/null; then
            echo "      Stress boxaverage saved: $STRESS_BOXAVG"
        else
            echo "      WARNING: boxaveragecells failed for stress${COMPONENT}"
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
            "$VTK_BASE" 2>/dev/null ; then
            echo "      VTK files created: ${VTK_BASE}*.vtk"
        else
            echo "      WARNING: data2vtk failed for stress${COMPONENT}"
            continue
        fi
        
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
            --stressfile "$STRESS_BOXAVG" \
            --displacementfile "$DISP_BOXAVG" \
            --chi "$CHI" \
            --angle "$ANGLE" \
            --component "$COMPONENT" \
            --outdir "$OUTDIR" 2>/dev/null; then
            echo "        1D plot generated successfully"
        else
            echo "        WARNING: 1D plot generation failed for stress${COMPONENT}"
        fi
    done

    # Process the saved crack driving-force field. The exact capitalization of
    # this output name varies between PACE3D versions, so discover it by field name.
    DRIVING_SRC=$(find "$folder" -maxdepth 1 -type f -iname "${FOLDER_NAME}*driving*force*.p3s" -print -quit)
    if [[ -z "$DRIVING_SRC" ]]; then
        echo "  WARNING: No driving-force .p3s file found in $FOLDER_NAME"
        continue
    fi

    DRIVING_CUT="$WORK_DIR/${FOLDER_NAME}_driving_force_cut.p3s"
    DRIVING_SIMGEO="$WORK_DIR/${FOLDER_NAME}_driving_force_cut.p3simgeo"
    DRIVING_BASE="$WORK_DIR/${FOLDER_NAME}_driving_force_vtk"
    echo "  Creating domain cut for driving force from $(basename "$DRIVING_SRC")..."
    if ! domaincut "$DRIVING_SRC" "$DRIVING_CUT" \
        -x "$DOMAIN_OFFSET_X" -X "$DOMAIN_END_X" \
        -y "$DOMAIN_OFFSET_Y" -Y "$DOMAIN_END_Y" \
        -f 2>/dev/null; then
        echo "  WARNING: domaincut failed for driving force"
        continue
    fi

    if [[ ! -f "$DRIVING_SIMGEO" ]]; then
        echo "  WARNING: driving-force domain cut did not create $DRIVING_SIMGEO"
        continue
    fi

    echo "  Converting driving force to VTK format..."
    if ! data2vtk "$DRIVING_SIMGEO" -d "$DRIVING_CUT" -a "$DRIVING_BASE" 2>/dev/null; then
        echo "  WARNING: data2vtk failed for driving force"
        continue
    fi

    mapfile -t DRIVING_VTK_FILES < <(find "$WORK_DIR" -maxdepth 1 -type f \
        -name "${FOLDER_NAME}_driving_force_vtk-*.vtk" | sort -V)
    if [[ ${#DRIVING_VTK_FILES[@]} -lt 3 ]]; then
        echo "  WARNING: Need at least 3 driving-force VTK frames, found ${#DRIVING_VTK_FILES[@]}"
        continue
    fi

    THIRD_LAST_INDEX=$((${#DRIVING_VTK_FILES[@]} - 3))
    DRIVING_VTK_FILE="${DRIVING_VTK_FILES[$THIRD_LAST_INDEX]}"
    echo "  Using third-last driving-force frame: $(basename "$DRIVING_VTK_FILE")"
    if python3 "$PLOT_DRIVING_SCRIPT" \
        --infile "$DRIVING_VTK_FILE" \
        --chi "$CHI" \
        --angle "$ANGLE" \
        --outdir "$OUTDIR" 2>/dev/null; then
        echo "  Driving-force polar plot generated successfully"
    else
        echo "  WARNING: Driving-force polar plot generation failed"
    fi
done

echo "==============================================="
echo "Processing complete!"
echo "Processed folders: $FOLDER_COUNT"
echo "Plots saved to: $OUTDIR"
echo "==============================================="
