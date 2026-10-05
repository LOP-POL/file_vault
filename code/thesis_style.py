"""
thesis_style.py

One place that makes every matplotlib figure match the LaTeX thesis
(page width, font family, font sizes).

Usage in a plotting script:

    import thesis_style as ts
    ts.apply()
    fig, ax = plt.subplots(figsize=ts.figsize(0.8))   # 80 % of the text width
    ...
    ts.save(fig, "path/without_extension")             # writes .pdf (+ .png preview)

In LaTeX include the PDF WITHOUT rescaling, so that 1 pt in the plot is 1 pt on the page:

    \\includegraphics{path/without_extension}          % no width=... here!
"""

import os
import shutil
from pathlib import Path

import matplotlib as mpl

# ----------------------------------------------------------------------------
# 1) EDIT THESE VALUES after measuring them in your LaTeX document
#    (see the explanation in the chat: \the\textwidth and \f@size)
# ----------------------------------------------------------------------------
TEXTWIDTH_PT = 459.6   # \the\textwidth in TeX points. 459.6 pt = A4 with KOMA DIV=13, BCOR=0 (ESTIMATE, verify!)
BASE_FONT_PT = 11.0    # main text size of the thesis (10, 11 or 12 pt) (ESTIMATE, verify!)

# Set to True to let your LaTeX installation typeset all labels (identical fonts
# and macros as the thesis). Needs `latex`, `dvipng` and `ghostscript` installed,
# plus the LaTeX package `cm-super` (error "type1ec.sty not found" = install it).
# "auto" = use LaTeX when it is found, otherwise fall back to matplotlib's
# built-in Computer Modern look-alike.
USE_TEX = "auto"

# LaTeX font sizes as a function of the base size (standard LaTeX/KOMA tables)
_SIZES = {
    10.0: {"small": 9.0,   "footnotesize": 8.0,  "scriptsize": 7.0},
    11.0: {"small": 10.0,  "footnotesize": 9.0,  "scriptsize": 8.0},
    12.0: {"small": 10.95, "footnotesize": 10.0, "scriptsize": 8.0},
}

PT_PER_INCH = 72.27  # TeX points, NOT the 72 of PostScript


def figsize(fraction=1.0, aspect=0.62):
    """Figure size in inches for `fraction` of the text width.

    fraction : 1.0 = full text width, 0.48 = two figures side by side, ...
    aspect   : height / width (0.62 is close to the golden ratio)
    """
    width = fraction * TEXTWIDTH_PT / PT_PER_INCH
    return (width, width * aspect)


def _tex_available():
    if USE_TEX is True:
        return True
    if USE_TEX is False:
        return False
    return all(shutil.which(tool) for tool in ("latex", "dvipng", "gs"))


def apply():
    """Activate the thesis style for all following figures."""
    sizes = _SIZES.get(float(BASE_FONT_PT), _SIZES[11.0])
    use_tex = _tex_available()

    rc = {
        # ---- sizes: text in plots uses the same sizes as captions/footnotes
        "font.size": sizes["small"],
        "axes.labelsize": sizes["small"],
        "axes.titlesize": sizes["small"],
        "xtick.labelsize": sizes["footnotesize"],
        "ytick.labelsize": sizes["footnotesize"],
        "legend.fontsize": sizes["footnotesize"],
        # ---- line widths (thin, as in LaTeX)
        "axes.linewidth": 0.6,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.minor.width": 0.4,
        "ytick.minor.width": 0.4,
        "lines.linewidth": 1.2,
        "lines.markersize": 3.5,
        "grid.linewidth": 0.4,
        "legend.frameon": False,
        # ---- layout and output
        "figure.constrained_layout.use": True,  # keeps the figure size EXACT
        "figure.figsize": figsize(0.8),
        "savefig.dpi": 300,                      # only matters for raster parts (imshow, png)
        "pdf.fonttype": 42,                      # embed real fonts in the pdf
        "axes.unicode_minus": False,
    }

    if use_tex:
        rc.update({
            "text.usetex": True,
            "font.family": "serif",
            "font.serif": ["Computer Modern Roman"],
            # Same packages as in 00-main.tex
            "text.latex.preamble": r"\usepackage{amsmath}\usepackage{amssymb}\usepackage{bm}",
        })
    else:
        rc.update({
            "text.usetex": False,
            "font.family": "serif",
            "font.serif": ["Latin Modern Roman", "cmr10", "DejaVu Serif"],
            "mathtext.fontset": "cm",           # Computer Modern maths
            "axes.formatter.use_mathtext": True,
        })
    mpl.rcParams.update(rc)
    return use_tex


def save(fig, path_without_ext, png_preview=True):
    """Save as PDF (for LaTeX) and optionally as PNG (for a quick look)."""
    base = str(path_without_ext)  # plain string: with_suffix() would cut names like "chi_2.5"
    Path(base).parent.mkdir(parents=True, exist_ok=True)
    # No bbox_inches="tight": it would change the figure size and break the scaling.
    fig.savefig(base + ".pdf")
    if png_preview:
        fig.savefig(base + ".png", dpi=200)
    print(f"Saved: {base}.pdf")
    return base + ".pdf"
