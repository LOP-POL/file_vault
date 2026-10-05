#!/usr/bin/env bash

################################################################################
# Acquire simulation data by creating domain cuts, box averages, and VTK files.
#
# Usage:
#     bash acquire_data.sh <parent_dir>
################################################################################

set -euo pipefail

PARENT_DIR=""

while [[ $# -gt 0 ]]; do
    case "$1" in
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

for command_name in domaincut boxaveragecells data2vtk; do
    if ! command -v "$command_name" >/dev/null 2>&1; then
        echo "Error: required command not found: $command_name"
        exit 1
    fi
done

STRESS_COMPONENTS=("11" "22" "21")
DOMAIN_OFFSET_X=0
DOMAIN_OFFSET_Y=0
DOMAIN_END_X=100
DOMAIN_END_Y=100
FOLDER_COUNT=0

shopt -s nullglob
FOLDERS=("$PARENT_DIR"/transversely_iso_no_crack_chi_*_angle_*)
for folder in "${FOLDERS[@]}"; do
    [[ -d "$folder" ]] || continue

    FOLDER_COUNT=$((FOLDER_COUNT + 1))
    FOLDER_NAME="$(basename "$folder")"

    if [[ "$FOLDER_NAME" =~ chi_([0-9.]+)_angle_([0-9.]+) ]]; then
        CHI="${BASH_REMATCH[1]}"
        ANGLE="${BASH_REMATCH[2]}"
    else
        echo "WARNING: Could not extract chi and angle from $FOLDER_NAME; skipping"
        continue
    fi

    WORK_DIR="$folder/domain_cut_analysis"
    mkdir -p "$WORK_DIR"
    echo "Processing $FOLDER_NAME (chi=$CHI, angle=$ANGLE)"

    DISP_SRC="$folder/${FOLDER_NAME}.SolidMechanics_Ux.p3s"
    DISP_CUT="$WORK_DIR/${FOLDER_NAME}_Ux_cut.p3s"
    DISP_BOXAVG="$WORK_DIR/${FOLDER_NAME}_Ux_boxavg.txt"

    if [[ -f "$DISP_SRC" ]]; then
        echo "  Creating displacement domain cut..."
        if domaincut "$DISP_SRC" "$DISP_CUT" \
            -x "$DOMAIN_OFFSET_X" -X "$DOMAIN_END_X" \
            -y "$DOMAIN_OFFSET_Y" -Y "$DOMAIN_END_Y" -f 2>/dev/null; then
            if boxaveragecells "$DISP_CUT" -b "[100,1,0],[100,100,0]" > "$DISP_BOXAVG" 2>/dev/null; then
                echo "  Displacement box average saved: $DISP_BOXAVG"
            else
                echo "  WARNING: boxaveragecells failed for displacement"
            fi
        else
            echo "  WARNING: domaincut failed for displacement"
        fi
    else
        echo "  WARNING: Displacement source not found: $DISP_SRC"
    fi

    SIMGEO_FILE="$folder/${FOLDER_NAME}.p3simgeo"
    if [[ ! -f "$SIMGEO_FILE" ]]; then
        echo "  WARNING: SimGeo file not found: $SIMGEO_FILE"
    else
        for component in "${STRESS_COMPONENTS[@]}"; do
            STRESS_FILE="$folder/${FOLDER_NAME}.SolidMechanics_stress${component}.p3s"
            if [[ ! -f "$STRESS_FILE" ]]; then
                echo "  WARNING: Stress file not found: $STRESS_FILE"
                continue
            fi

            DOMAIN_CUT_FILE="$WORK_DIR/${FOLDER_NAME}_stress${component}_cut.p3s"
            SIMGEO_DOM_CUT_FILE="$WORK_DIR/${FOLDER_NAME}_stress${component}_cut.p3simgeo"
            STRESS_BOXAVG="$WORK_DIR/${FOLDER_NAME}_stress${component}_boxavg.txt"
            VTK_BASE="$WORK_DIR/stress${component}_vtk"

            echo "  Creating stress${component} domain cut..."
            if ! domaincut "$STRESS_FILE" "$DOMAIN_CUT_FILE" \
                -x "$DOMAIN_OFFSET_X" -X "$DOMAIN_END_X" \
                -y "$DOMAIN_OFFSET_Y" -Y "$DOMAIN_END_Y" -f 2>/dev/null; then
                echo "  WARNING: domaincut failed for stress${component}"
                continue
            fi

            if boxaveragecells "$DOMAIN_CUT_FILE" -b "[100,1,0],[100,100,0]" > "$STRESS_BOXAVG" 2>/dev/null; then
                echo "  Stress box average saved: $STRESS_BOXAVG"
            else
                echo "  WARNING: boxaveragecells failed for stress${component}"
            fi

            if [[ ! -f "$SIMGEO_DOM_CUT_FILE" ]]; then
                for simgeo_file in "$WORK_DIR"/*.p3simgeo; do
                    [[ -f "$simgeo_file" ]] || continue
                    mv -- "$simgeo_file" "$SIMGEO_DOM_CUT_FILE"
                    break
                done
            fi

            if [[ ! -f "$SIMGEO_DOM_CUT_FILE" ]]; then
                echo "  WARNING: domaincut did not produce $SIMGEO_DOM_CUT_FILE"
                continue
            fi

            echo "  Converting stress${component} to VTK..."
            if data2vtk "$SIMGEO_DOM_CUT_FILE" -d "$DOMAIN_CUT_FILE" -a "$VTK_BASE" 2>/dev/null; then
                echo "  Stress${component} VTK files saved with base: $VTK_BASE"
            else
                echo "  WARNING: data2vtk failed for stress${component}"
            fi
        done
    fi

    DRIVING_SRC="$(find "$folder" -maxdepth 1 -type f \
        -iname "${FOLDER_NAME}*driving*force*.p3s" -print -quit)"
    if [[ -z "$DRIVING_SRC" ]]; then
        echo "  WARNING: No driving-force .p3s file found in $FOLDER_NAME"
        continue
    fi

    DRIVING_CUT="$WORK_DIR/${FOLDER_NAME}_driving_force_cut.p3s"
    DRIVING_SIMGEO="$WORK_DIR/${FOLDER_NAME}_driving_force_cut.p3simgeo"
    DRIVING_BASE="$WORK_DIR/${FOLDER_NAME}_driving_force_vtk"

    echo "  Creating driving-force domain cut..."
    if ! domaincut "$DRIVING_SRC" "$DRIVING_CUT" \
        -x "$DOMAIN_OFFSET_X" -X "$DOMAIN_END_X" \
        -y "$DOMAIN_OFFSET_Y" -Y "$DOMAIN_END_Y" -f 2>/dev/null; then
        echo "  WARNING: domaincut failed for driving force"
        continue
    fi

    if [[ ! -f "$DRIVING_SIMGEO" ]]; then
        echo "  WARNING: domaincut did not produce $DRIVING_SIMGEO"
        continue
    fi

    echo "  Converting driving force to VTK..."
    if data2vtk "$DRIVING_SIMGEO" -d "$DRIVING_CUT" -a "$DRIVING_BASE" 2>/dev/null; then
        echo "  Driving-force VTK files saved with base: $DRIVING_BASE"
    else
        echo "  WARNING: data2vtk failed for driving force"
    fi
done

echo "==============================================="
echo "Data acquisition complete"
echo "Processed folders: $FOLDER_COUNT"
echo "==============================================="