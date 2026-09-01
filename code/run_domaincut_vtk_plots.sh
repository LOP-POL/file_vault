#!/bin/bash
#
# run_domaincut_vtk_plots.sh
#
# Sits inside the directory that contains one result folder per simulation
# (e.g. transversely_iso_no_crack_chi_2.5_angle_0_01-Sep-2026_13:43/). For
# each folder it:
#   1. Parses chi and angle out of the folder name.
#   2. Domain-cuts the stress11, stress22 and stress12 .p3s files at
#      xoffset=-50, yoffset=-50 (XOFFSET/YOFFSET below).
#   3. Runs data2vtk on the cut files to produce a VTK series.
#   4. Calls a user-supplied Python script on the LAST frame of that
#      series to produce one plot per stress component (stress11,
#      stress22, stress12), named with chi/angle/component.
#
# Requires `domaincut` and `data2vtk` to be on PATH.
#
# Usage:
#   bash run_domaincut_vtk_plots.sh /path/to/plot_vtk_stress.py /path/to/plots_output_dir
#
# The Python script is called as:
#   python3 PLOT_SCRIPT --vtk <last_frame.vtk> --chi <chi> --angle <angle> --outdir <PLOTS_OUTPUT_DIR>/<folder_name>

set -uo pipefail

# --- Domain-cut parameters (adjust as needed) --------------------------------
XOFFSET=50
YOFFSET=50
# XEND / YEND are left at their tool defaults (-1 = keep everything up to the
# domain max). Add -X "$XEND" / -Y "$YEND" to the domaincut calls below if you
# need an upper bound too.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"
MASTER_LOG="$LOG_DIR/domaincut_vtk_plots_$(date +%Y%m%d_%H%M%S).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$MASTER_LOG"
}

# --- Arguments ---------------------------------------------------------------
if [ "$#" -lt 2 ]; then
    echo "Usage: $0 /path/to/plot_vtk_stress.py /path/to/plots_output_dir" >&2
    exit 1
fi

PYTHON_SCRIPT="$1"
PLOTS_OUTPUT_DIR="$2"

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Python script not found: $PYTHON_SCRIPT" >&2
    exit 1
fi

mkdir -p "$PLOTS_OUTPUT_DIR"

# --- Tool availability check ---------------------------------------------------
for tool in domaincut data2vtk python3; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "Required tool '$tool' not found on PATH." >&2
        exit 1
    fi
done

# --- Collect result folders ---------------------------------------------------
# Only directories whose name contains chi_<num>_angle_<num> are treated as
# simulation result folders. This silently skips the script's own logs/
# folder, the plots output directory (if it happens to live alongside the
# results), or anything else that doesn't match the naming convention.
folders=()
for d in "$SCRIPT_DIR"/*/; do
    [ -d "$d" ] || continue
    name="$(basename "${d%/}")"
    if [[ "$name" =~ chi_([0-9]+(\.[0-9]+)?)_angle_([0-9]+(\.[0-9]+)?) ]]; then
        folders+=("${d%/}")
    fi
done

if [ ${#folders[@]} -eq 0 ]; then
    log "No result folders matching '*chi_<num>_angle_<num>*' found in $SCRIPT_DIR. Exiting."
    exit 1
fi

log "Found ${#folders[@]} folder(s) in $SCRIPT_DIR."

failed_folders=()

# --- Main loop -----------------------------------------------------------------
for folder in "${folders[@]}"; do
    folder_name="$(basename "$folder")"

    # Extract chi and angle from the folder name, e.g.
    # transversely_iso_no_crack_chi_2.5_angle_0_01-Sep-2026_13:43
    if [[ "$folder_name" =~ chi_([0-9]+(\.[0-9]+)?)_angle_([0-9]+(\.[0-9]+)?) ]]; then
        chi="${BASH_REMATCH[1]}"
        angle="${BASH_REMATCH[3]}"
    else
        log "WARNING: could not parse chi/angle from folder name '$folder_name' -- skipping."
        failed_folders+=("$folder_name")
        continue
    fi

    log "=== Processing $folder_name (chi=$chi, angle=$angle) ==="

    prefix="$folder_name"   # files inside the folder share this prefix
    stress11="${folder}/${prefix}.SolidMechanics_stress11.p3s"
    stress22="${folder}/${prefix}.SolidMechanics_stress22.p3s"
    stress12="${folder}/${prefix}.SolidMechanics_stress12.p3s"   # covers stress21 by symmetry

    missing=0
    for f in "$stress11" "$stress22" "$stress12"; do
        if [ ! -f "$f" ]; then
            log "WARNING: expected file missing: $f"
            missing=1
        fi
    done
    if [ "$missing" -eq 1 ]; then
        log "WARNING: skipping $folder_name due to missing input file(s)."
        failed_folders+=("$folder_name")
        continue
    fi

    work_dir="${folder}/domaincut_vtk"
    mkdir -p "$work_dir"

    # --- Domain cut each stress file (each call also produces its own
    #     matching .p3simgeo and .p3minmax alongside the .p3s) -------------
    stress11_cut="${work_dir}/${prefix}_stress11_domaincut.p3s"
    stress22_cut="${work_dir}/${prefix}_stress22_domaincut.p3s"
    stress12_cut="${work_dir}/${prefix}_stress12_domaincut.p3s"
    stress11_cut_simgeo="${work_dir}/${prefix}_stress11_domaincut.p3simgeo"

    cut_ok=1
    if ! domaincut -f  "$stress11" "$stress11_cut" -X "$XOFFSET" -Y "$YOFFSET" >> "$MASTER_LOG" 2>&1; then
        log "WARNING: domaincut failed for stress11 in $folder_name"
        cut_ok=0
    fi
    if ! domaincut -f  "$stress22" "$stress22_cut" -X "$XOFFSET" -Y "$YOFFSET" >> "$MASTER_LOG" 2>&1; then
        log "WARNING: domaincut failed for stress22 in $folder_name"
        cut_ok=0
    fi
    if ! domaincut -f  "$stress12" "$stress12_cut" -X "$XOFFSET" -Y "$YOFFSET" >> "$MASTER_LOG" 2>&1; then
        log "WARNING: domaincut failed for stress12 in $folder_name"
        cut_ok=0
    fi

    if [ "$cut_ok" -eq 0 ] || [ ! -f "$stress11_cut_simgeo" ]; then
        log "WARNING: skipping $folder_name -- domain cut did not complete successfully."
        failed_folders+=("$folder_name")
        continue
    fi

    # --- data2vtk: use the cut geometry from the stress11 cut (all three
    #     cuts use the same offsets, so any one of them matches) -----------
    vtk_prefix="${work_dir}/${prefix}_vtk"
    if ! data2vtk "$stress11_cut_simgeo" \
            -d "${stress11_cut}; ${stress22_cut}; ${stress12_cut}" \
            "$vtk_prefix" >> "$MASTER_LOG" 2>&1
    then
        log "WARNING: data2vtk failed for $folder_name -- skipping."
        failed_folders+=("$folder_name")
        continue
    fi

    # Pick the last (highest-numbered) frame in the series, e.g.
    # <vtk_prefix>-00003.vtk out of -00001/-00002/-00003
    last_vtk="$(ls "${vtk_prefix}"-*.vtk 2>/dev/null | sort -V | tail -n 1)"
    if [ -z "$last_vtk" ]; then
        log "WARNING: no VTK frames produced for $folder_name -- skipping plotting."
        failed_folders+=("$folder_name")
        continue
    fi
    log "Using final frame for plotting: $(basename "$last_vtk")"

    # --- Plot ---------------------------------------------------------------
    plot_outdir="${PLOTS_OUTPUT_DIR}/${folder_name}"
    mkdir -p "$plot_outdir"

    if ! python3 "$PYTHON_SCRIPT" \
            --vtk "$last_vtk" \
            --chi "$chi" \
            --angle "$angle" \
            --outdir "$plot_outdir" >> "$MASTER_LOG" 2>&1
    then
        log "WARNING: plotting failed for $folder_name -- see $MASTER_LOG"
        failed_folders+=("$folder_name")
        continue
    fi

    log "=== Done with $folder_name -- plots in $plot_outdir ==="
done

log "All folders processed."

if [ ${#failed_folders[@]} -gt 0 ]; then
    log "Completed with issues in: ${failed_folders[*]}"
else
    log "All folders completed successfully."
fi
