"""House chart style: red accent bar, bold one-message title, subtitle with units, source line.

Use frame() to get a figure with the house furniture, add your own axes, then save().
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RED = "#e3120b"
DARK = "#1a1a1a"
GREY = "#8c8c8c"
BLUE = "#2b6ca3"
LIGHT = "#d9d9d9"
PALE_RED = "#fbe3e1"
GRID = "#eeeeee"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": False,
})


def frame(title, sub, src, figsize=(8, 6)):
    """A figure with the accent bar, title, subtitle and source line. Add axes yourself."""
    fig = plt.figure(figsize=figsize)
    fig.patches.append(plt.Rectangle((0.04, 0.975), 0.06, 0.012,
                                     transform=fig.transFigure, color=RED))
    fig.text(0.04, 0.93, title, fontsize=17, fontweight="bold", color=DARK, va="top")
    fig.text(0.04, 0.86, sub, fontsize=11.5, color="#444444", va="top")
    fig.text(0.04, 0.02, src, fontsize=8, color=GREY)
    return fig


def main_axes(fig, rect=(0.08, 0.12, 0.88, 0.62)):
    """The standard plotting area under the subtitle."""
    return fig.add_axes(list(rect))


def label_bars(ax, bars, fmt="{:+.1f}", size=12):
    """Bold value labels above positive bars and below negative ones."""
    lo, hi = ax.get_ylim()
    pad = 0.04 * (hi - lo)
    for r in bars:
        v = r.get_height()
        ax.text(r.get_x() + r.get_width() / 2, v + (pad if v >= 0 else -pad), fmt.format(v),
                ha="center", va="bottom" if v >= 0 else "top", fontsize=size, fontweight="bold")


def save(fig, path, dpi=200):
    """Save a figure as PNG, creating the folder if needed, then close it."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi)
    plt.close(fig)
