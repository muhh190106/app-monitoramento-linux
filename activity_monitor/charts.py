"""Matplotlib chart rendering shared by the desktop app and headless checks."""

from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator

from .i18n import translate

PANEL = "#111e2d"
TEXT = "#e7eef7"
MUTED = "#94a7bb"
ACCENT = "#57d9c0"


def draw_timeline(figure: Figure, report, language: str):
    figure.clear()
    figure.set_facecolor(PANEL)
    axis = figure.add_subplot(111)
    axis.set_facecolor(PANEL)
    text = lambda key: translate(language, key)
    if not report.active_seconds and not report.idle_seconds:
        axis.text(.5, .54, text("empty"), transform=axis.transAxes, ha="center", color=TEXT, fontsize=13)
        axis.text(.5, .40, text("empty_hint"), transform=axis.transAxes, ha="center", color=MUTED, fontsize=10)
        axis.set_axis_off()
    else:
        points = report.timeline
        active = [p.active_seconds / 60 for p in points]
        idle = [p.idle_seconds / 60 for p in points]
        positions = list(range(len(points)))
        axis.bar(positions, active, width=.58, color=ACCENT, label=text("active"), zorder=3)
        axis.bar(positions, idle, bottom=active, width=.58, color="#4b6380", label=text("idle"), zorder=3)
        step = max(1, len(points) // 6)
        ticks = list(range(0, len(points), step))
        axis.set_xticks(ticks, [points[i].timestamp.strftime("%H:%M" if len(points) == 24 else "%d/%m") for i in ticks])
        axis.set_xlim(-.8, len(points) - .2)
        axis.set_ylim(bottom=0)
        axis.yaxis.set_major_locator(MaxNLocator(nbins=4, integer=True))
        axis.set_ylabel(text("minutes"), color=MUTED, fontsize=9, labelpad=12)
        axis.tick_params(colors=MUTED, labelsize=9, length=0, pad=10)
        axis.grid(axis="y", color="#243449", linewidth=.7, zorder=0)
        for spine in axis.spines.values():
            spine.set_visible(False)
        axis.legend(loc="upper left", frameon=False, labelcolor=MUTED, fontsize=9, ncol=2, bbox_to_anchor=(0, 1.14))
        axis.margins(y=.18)
    figure.subplots_adjust(left=.19, right=.97, bottom=.18, top=.84)
    return axis
