#!/usr/bin/env python3
"""
generate_infiles.py

Takes an existing pace2D .infile as a template and sweeps over a grid of
(chi, angle) values, writing one infile per combination with
DefineConst=chi and DefineConst=angle updated, and the filename following
the same naming convention as the template.

Usage:
    python3 generate_infiles.py TEMPLATE_INFILE [OUTPUT_DIR]

Example:
    python3 generate_infiles.py transversely_iso_no_crack_chi_0_angle_90.infile .
"""

import re
import sys
from pathlib import Path

# --- Sweep values ------------------------------------------------------
# chi: R2 preferred-number series values requested (replaces the plan's
# 0, 1, 2, 5, 10, 20 list)
CHI_VALUES = [1, 2, 6, 16]

# angle: straight from the verification plan
ANGLE_VALUES = [0, 30, 45, 60, 90]

CHI_LINE_RE = re.compile(r'^(DefineConst=chi,)\s*[-+0-9.eE]+\s*$', re.MULTILINE)
ANGLE_LINE_RE = re.compile(r'^(DefineConst=angle,)\s*[-+0-9.eE]+\s*$', re.MULTILINE)


def format_number(value):
    """Format a sweep value the way it should appear inside the infile."""
    if float(value).is_integer():
        return f"{float(value):.1f}"
    return str(value)


def format_for_filename(value):
    """Format a sweep value the way it should appear in the filename."""
    if float(value).is_integer():
        return str(int(value))
    return str(value)


def derive_prefix(template_name):
    """
    Derive the filename prefix by cutting the template name right before
    its '_chi_' segment, e.g.:
      transversely_iso_no_crack_chi_0_angle_90.infile
      -> transversely_iso_no_crack
    Falls back to the template's stem (minus extension) if '_chi_' isn't
    found, so this still works on templates named differently.
    """
    stem = Path(template_name).stem
    marker = "_chi_"
    idx = stem.find(marker)
    if idx == -1:
        return stem
    return stem[:idx]


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate_infiles.py TEMPLATE_INFILE [OUTPUT_DIR]")
        sys.exit(1)

    template_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else template_path.parent

    if not template_path.is_file():
        print(f"Template file not found: {template_path}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    template_text = template_path.read_text()

    if not CHI_LINE_RE.search(template_text):
        print("WARNING: no 'DefineConst=chi,...' line found in the template "
              "-- chi will not be updated in the generated files.")
    if not ANGLE_LINE_RE.search(template_text):
        print("WARNING: no 'DefineConst=angle,...' line found in the "
              "template -- angle will not be updated in the generated files.")

    prefix = derive_prefix(template_path.name)

    generated = []
    for chi in CHI_VALUES:
        for angle in ANGLE_VALUES:
            text = CHI_LINE_RE.sub(rf'\g<1>{format_number(chi)}', template_text)
            text = ANGLE_LINE_RE.sub(rf'\g<1>{format_number(angle)}', text)

            filename = (
                f"{prefix}_chi_{format_for_filename(chi)}"
                f"_angle_{format_for_filename(angle)}.infile"
            )
            out_path = output_dir / filename
            out_path.write_text(text)
            generated.append(filename)

    print(f"Generated {len(generated)} infile(s) in {output_dir}:")
    for name in generated:
        print(f"  {name}")


if __name__ == "__main__":
    main()
