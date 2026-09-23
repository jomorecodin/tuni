"""Render LaTeX math expressions to PNG images for Telegram.

Handles two categories:
- Regular formulas (fractions, integrals, sums, etc.) via matplotlib mathtext
- Matrix environments via custom grid rendering (mathtext doesn't support them)

Usage in chat handler:
    from app.bot.services.latex_renderer import has_renderable_math, render_all_blocks, clean_text

    if has_renderable_math(response):
        images = render_all_blocks(response)
        cleaned = clean_text(response)
"""

import io
import re
import logging

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

# $$...$$ display math blocks
DISPLAY_MATH_RE = re.compile(r"\$\$(.*?)\$\$", re.DOTALL)

# \begin{pmatrix}...\end{pmatrix} and variants
MATRIX_RE = re.compile(
    r"\\begin\{([a-z]*matrix)\}(.*?)\\end\{\1\}", re.DOTALL
)


def has_renderable_math(text: str) -> bool:
    """Return True if the text contains $$...$$ blocks."""
    return bool(DISPLAY_MATH_RE.search(text))


def extract_math_blocks(text: str) -> list[str]:
    """Return all $$...$$ block contents from text."""
    return [m.strip() for m in DISPLAY_MATH_RE.findall(text) if m.strip()]


# ---------------------------------------------------------------------------
# Formula rendering (matplotlib mathtext)
# ---------------------------------------------------------------------------

def _render_mathtext(latex: str, fontsize: int = 22, dpi: int = 150) -> bytes | None:
    """Render a LaTeX expression via matplotlib mathtext. Returns PNG bytes."""
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.patch.set_facecolor("white")
    try:
        clean = latex.strip().strip("$")
        text_obj = fig.text(0, 0, f"${clean}$", fontsize=fontsize,
                            color="black", ha="left", va="bottom")
        fig.canvas.draw()
        bbox = text_obj.get_window_extent(fig.canvas.get_renderer())
        bbox_in = bbox.transformed(fig.dpi_scale_trans.inverted())
        fig.set_size_inches(bbox_in.width + 0.3, bbox_in.height + 0.3)
        text_obj.set_position((0.15 / fig.get_figwidth(),
                               0.15 / fig.get_figheight()))

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight",
                    pad_inches=0.15, facecolor="white", edgecolor="none")
        buf.seek(0)
        return buf.read()
    except Exception as e:
        logger.debug("mathtext render failed for %r: %s", latex[:60], e)
        return None
    finally:
        plt.close(fig)


# ---------------------------------------------------------------------------
# Matrix rendering (custom grid with brackets)
# ---------------------------------------------------------------------------

def _parse_matrix(content: str) -> list[list[str]]:
    """Parse '1 & 2 \\\\ 3 & 4' into [['1','2'],['3','4']]."""
    rows = re.split(r"\\\\", content)
    matrix = []
    for row in rows:
        row = row.strip()
        if not row:
            continue
        cells = [c.strip() for c in row.split("&")]
        matrix.append(cells)
    return matrix


def _render_matrix(matrix: list[list[str]], bracket: str = "pmatrix",
                   fontsize: int = 18, dpi: int = 150) -> bytes | None:
    """Render a matrix as a grid image with bracket symbols."""
    if not matrix or not matrix[0]:
        return None

    nrows = len(matrix)
    ncols = max(len(r) for r in matrix)

    # Pad short rows
    for r in matrix:
        while len(r) < ncols:
            r.append("")

    fig_w = max(ncols * 0.9, 1.6)
    fig_h = max(nrows * 0.55, 0.9)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.axis("off")
    fig.patch.set_facecolor("white")

    brackets = {
        "pmatrix": ("(", ")"),
        "bmatrix": ("[", "]"),
        "Bmatrix": ("{", "}"),
        "vmatrix": ("|", "|"),
        "Vmatrix": ("\u2016", "\u2016"),
        "matrix": ("", ""),
    }
    left_b, right_b = brackets.get(bracket, ("(", ")"))

    cell_w = 1.0 / (ncols + 2)
    cell_h = 1.0 / max(nrows, 1)

    for i, row in enumerate(matrix):
        y = 1.0 - (i + 0.5) * cell_h
        for j, cell in enumerate(row):
            x = (j + 1.5) * cell_w
            label = f"${cell}$" if cell else ""
            ax.text(x, y, label, fontsize=fontsize,
                    ha="center", va="center", transform=ax.transAxes)

    bracket_size = fontsize * min(2.5, 1.0 + nrows * 0.5)
    if left_b:
        ax.text(0.5 * cell_w, 0.5, left_b, fontsize=bracket_size,
                ha="center", va="center", transform=ax.transAxes,
                fontfamily="serif")
    if right_b:
        ax.text(1.0 - 0.5 * cell_w, 0.5, right_b, fontsize=bracket_size,
                ha="center", va="center", transform=ax.transAxes,
                fontfamily="serif")

    try:
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight",
                    pad_inches=0.1, facecolor="white", edgecolor="none")
        buf.seek(0)
        return buf.read()
    except Exception as e:
        logger.debug("matrix render failed: %s", e)
        return None
    finally:
        plt.close(fig)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def render_block(latex: str) -> bytes | None:
    """Render a single LaTeX block to PNG. Auto-detects matrices."""
    m = MATRIX_RE.search(latex)
    if m:
        env_type = m.group(1)
        content = m.group(2)
        matrix = _parse_matrix(content)
        return _render_matrix(matrix, bracket=env_type)

    return _render_mathtext(latex)


def render_all_blocks(text: str) -> list[bytes]:
    """Extract $$...$$ blocks from text, render each to PNG.

    Returns list of PNG byte arrays; blocks that fail to render are skipped.
    """
    blocks = extract_math_blocks(text)
    images = []
    for block in blocks:
        png = render_block(block)
        if png:
            images.append(png)
    return images


def clean_text(text: str) -> str:
    """Replace $$...$$ blocks with a placeholder for the text message."""
    def _replacer(match):
        return "\n[ver formula en imagen]\n"
    return DISPLAY_MATH_RE.sub(_replacer, text).strip()
