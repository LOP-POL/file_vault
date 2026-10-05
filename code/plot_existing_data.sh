#!/usr/bin/env bash

################################################################################
# Plot existing simulation outputs without running domaincut or data2vtk.
#
# Usage:
#     bash plot_existing_data.sh <parent_dir> [--outdir OUTPUT_DIR]
################################################################################

set -euo pipefail

PARENT_DIR=""
OUTDIR=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --outdir)
            if [[ $# -lt 2 ]]; then
                echo "Error: --outdir requires a directory"
                exit 1
            fi
            OUTDIR="$2"
            shift 2
            ;;
        -h|--help)
            sed -n '1,9p' "$0"
            exit 0
            ;;
        -* )
            echo "Unknown option: $1"
            exit 1
            ;;
        *)
            if [[ -n "$PARENT_DIR" ]]; then
                echo "Error: only one parent directory may be provided"
                exit 1
            fi
            PARENT_DIR="$1"
            shift
            ;;
    esac
done

PARENT_DIR="${PARENT_DIR:-.}"
if [[ ! -d "$PARENT_DIR" ]]; then
    echo "Error: Parent directory not found: $PARENT_DIR"
    exit 1
fi

OUTDIR="${OUTDIR:-$PARENT_DIR/plots}"
mkdir -p "$OUTDIR"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLOT_SCRIPT="$SCRIPT_DIR/plot_stress.py"
PLOT_DRIVING_SCRIPT="$SCRIPT_DIR/plot_polar.py"

for script in "$PLOT_SCRIPT" "$PLOT_DRIVING_SCRIPT"; do
    if [[ ! -f "$script" ]]; then
        echo "Error: plotting script not found: $script"
        exit 1
    fi
done

TEMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TEMP_DIR"' EXIT

STRESS_COMPONENTS=("11" "22" "21")
FOLDER_COUNT=0
PLOT_COUNT=0

shopt -s nullglob
FOLDERS=("$PARENT_DIR"/transversely_iso_no_crack_chi_*_angle_*)
for folder in "${FOLDERS[@]}"; do
    [[ -d "$folder" ]] || continue

    FOLDER_COUNT=$((FOLDER_COUNT + 1))
    FOLDER_NAME="$(basename "$folder")"
    WORK_DIR="$folder/domain_cut_analysis"

    if [[ ! "$FOLDER_NAME" =~ chi_([0-9.]+)_angle_([0-9.]+) ]]; then
        echo "Skipping folder with unrecognized chi/angle: $FOLDER_NAME"
        continue
    fi
    CHI="${BASH_REMATCH[1]}"
    ANGLE="${BASH_REMATCH[2]}"

    if [[ ! -d "$WORK_DIR" ]]; then
        echo "Skipping $FOLDER_NAME: no domain_cut_analysis directory"
        continue
    fi

    echo "Plotting existing outputs for $FOLDER_NAME (chi=$CHI, angle=$ANGLE)"

    for component in "${STRESS_COMPONENTS[@]}"; do
        mapfile -t VTK_FILES < <(find "$WORK_DIR" -maxdepth 1 -type f \
            -name "stress${component}_vtk-*.vtk" -print | sort -V)

        if [[ ${#VTK_FILES[@]} -eq 0 ]]; then
            echo "  No stress${component} VTK files found; skipping component"
            continue
        fi

        VTK_FILE="${VTK_FILES[-1]}"
        TEMP_VTK="$TEMP_DIR/stress${component}.vtk"
        cp "$VTK_FILE" "$TEMP_VTK"
        echo "  Plotting stress${component} from $(basename "$VTK_FILE")"

        if python3 "$PLOT_SCRIPT" \
            --infile "$TEMP_VTK" \
            --chi "$CHI" \
            --angle "$ANGLE" \
            --component "$component" \
            --outdir "$OUTDIR"; then
            PLOT_COUNT=$((PLOT_COUNT + 1))
        else
            echo "  WARNING: stress${component} VTK plotting failed"
        fi

        STRESS_BOXAVG="$WORK_DIR/${FOLDER_NAME}_stress${component}_boxavg.txt"
        DISP_BOXAVG="$WORK_DIR/${FOLDER_NAME}_Ux_boxavg.txt"
        if [[ -f "$STRESS_BOXAVG" && -f "$DISP_BOXAVG" ]]; then
            echo "  Plotting stress${component} versus displacement"
            if python3 "$PLOT_SCRIPT" \
                --infile "$TEMP_VTK" \
                --stressfile "$STRESS_BOXAVG" \
                --displacementfile "$DISP_BOXAVG" \
                --chi "$CHI" \
                --angle "$ANGLE" \
                --component "$component" \
                --outdir "$OUTDIR"; then
                PLOT_COUNT=$((PLOT_COUNT + 1))
            else
                echo "  WARNING: stress${component}-versus-displacement plotting failed"
            fi
        else
            echo "  Box-average inputs missing for stress${component}-versus-displacement; skipping"
        fi
    done

    mapfile -t DRIVING_VTK_FILES < <(find "$WORK_DIR" -maxdepth 1 -type f \
        -name "${FOLDER_NAME}_driving_force_vtk-*.vtk" -print | sort -V)
    if [[ ${#DRIVING_VTK_FILES[@]} -lt 3 ]]; then
        echo "  Need at least 3 driving-force VTK frames; found ${#DRIVING_VTK_FILES[@]}"
        continue
    fi

    THIRD_LAST_INDEX=$((${#DRIVING_VTK_FILES[@]} - 3))
    DRIVING_VTK_FILE="${DRIVING_VTK_FILES[$THIRD_LAST_INDEX]}"
    TEMP_DRIVING_VTK="$TEMP_DIR/driving_force.vtk"
    POLAR_OUTDIR="$TEMP_DIR/polar_output"
    POLAR_PLOT="$POLAR_OUTDIR/driving_force_polar.png"
    mkdir -p "$POLAR_OUTDIR"
    rm -f "$POLAR_PLOT"
    cp "$DRIVING_VTK_FILE" "$TEMP_DRIVING_VTK"
    echo "  Plotting driving force from $(basename "$DRIVING_VTK_FILE")"

    if python3 "$PLOT_DRIVING_SCRIPT" \
        --infile "$TEMP_DRIVING_VTK" \
        --chi "$CHI" \
        --angle "$ANGLE" \
        --outdir "$POLAR_OUTDIR"; then
        if [[ -f "$POLAR_PLOT" ]]; then
            mv "$POLAR_PLOT" "$OUTDIR/${FOLDER_NAME}_driving_force_polar.png"
            PLOT_COUNT=$((PLOT_COUNT + 1))
        else
            echo "  WARNING: driving-force plotter returned without creating its output"
        fi
    else
        echo "  WARNING: driving-force plotting failed"
    fi
done

echo "==============================================="
echo "Plotting complete"
echo "Processed folders: $FOLDER_COUNT"
echo "Successful plot commands: $PLOT_COUNT"
echo "Plots saved to: $OUTDIR"
echo "==============================================="