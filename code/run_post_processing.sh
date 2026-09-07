#!/bin/bash
# Run post-processing plots after get_data.sh has completed

set -e

PARENT_DIR="${1:-.}"
OUTDIR="${2:-$PARENT_DIR/plots}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STRESS22_SCRIPT="$SCRIPT_DIR/stress22_by_chi.py"
MULTI_SCRIPT="$SCRIPT_DIR/plot_stress_vs_disp_multiple.py"

if [[ ! -f "$STRESS22_SCRIPT" ]]; then
    echo "Missing $STRESS22_SCRIPT"
    exit 1
fi
if [[ ! -f "$MULTI_SCRIPT" ]]; then
    echo "Missing $MULTI_SCRIPT"
    exit 1
fi

mkdir -p "$OUTDIR"

# collect unique angles and chis
angles=()
chis=()
for f in "$PARENT_DIR"/transversely_iso_no_crack_chi_*_angle_*; do
    [[ -d "$f" ]] || continue
    name=$(basename "$f")
    if [[ $name =~ chi_([0-9.]+)_angle_([0-9.]+) ]]; then
        chi=${BASH_REMATCH[1]}
        angle=${BASH_REMATCH[2]}
        angles+=("$angle")
        chis+=("$chi")
    fi
done

# reduce to unique
unique_angles=($(printf "%s\n" "${angles[@]}" | sort -u))
unique_chis=($(printf "%s\n" "${chis[@]}" | sort -u -n))

echo "Found angles: ${unique_angles[*]}"
echo "Found chis: ${unique_chis[*]}"

# For each angle: stress22 vs chi and stress vs disp overlay for chi-series
for angle in "${unique_angles[@]}"; do
    echo "Plotting stress22 vs chi for angle=$angle"
    python3 "$STRESS22_SCRIPT" --parent_dir "$PARENT_DIR" --angle "$angle" --outdir "$OUTDIR" || echo "Warning: stress22 plot failed for angle $angle"

    echo "Plotting stress-vs-displacement overlay for angle=$angle"
    python3 "$MULTI_SCRIPT" --parent_dir "$PARENT_DIR" --mode angle --angle "$angle" --outdir "$OUTDIR" || echo "Warning: overlay plot failed for angle $angle"
done

# For each chi: stress vs disp overlay across angles
for chi in "${unique_chis[@]}"; do
    echo "Plotting stress-vs-displacement overlay for chi=$chi"
    python3 "$MULTI_SCRIPT" --parent_dir "$PARENT_DIR" --mode chi --chi "$chi" --outdir "$OUTDIR" || echo "Warning: overlay plot failed for chi $chi"
done

echo "Post-processing complete. Plots in: $OUTDIR"
