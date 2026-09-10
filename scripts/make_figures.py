"""Generate the deck's figures.

Every data figure is built from a result file committed in one of the source
repositories, copied into ``data/``.  Nothing here invents a number.  The two
schematic figures (the single-trial illustration and the array-grid diagram)
are drawn, not measured, and are labelled as such on the slide.

Run:  python scripts/make_figures.py
Out:  assets/img/*.svg
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "assets" / "img"
OUT.mkdir(parents=True, exist_ok=True)

# House palette: the teal is the one colour his Marp deck theme and his
# Meridian documentation brand independently agree on (#0f6e6e).
INK = "#1c2024"
TEAL = "#0f6e6e"
MUTED = "#5b6470"
RULE = "#d6dbe0"
REDLINE = "#a3271f"
AMBER = "#e8a33d"
PAPER = "#fbfbfc"

# Okabe-Ito, as shipped in his own depictr package (colourblind-safe).
OI_SKY = "#56b4e9"
OI_ORANGE = "#e69f00"
OI_VERMILLION = "#d55e00"
OI_BLUE = "#005b96"

plt.rcParams.update(
    {
        "svg.fonttype": "path",  # self-contained: no font dependency in the browser
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "Helvetica Neue", "Arial", "DejaVu Sans"],
        "text.color": INK,
        "axes.labelcolor": INK,
        "axes.edgecolor": RULE,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "axes.facecolor": PAPER,
        "figure.facecolor": PAPER,
        "savefig.facecolor": PAPER,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": False,
    }
)


def save(fig: plt.Figure, name: str) -> None:
    path = OUT / name
    fig.savefig(path, format="svg", bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    print(f"  {name}  ({path.stat().st_size // 1024} KB)")


# ---------------------------------------------------------------------------
# 1. MVPA decoding runtimes against the requested 14-day wall. The long
#    partition allows thirty days; fourteen is what the job asked for, so the
#    annotation says so and does not read as a system limit.
#    Source: LESS-morphosyntactic-transfer/paper_1_transfer/hpc/08_decoding.slurm
# ---------------------------------------------------------------------------
def fig_decoding_runtime() -> None:
    labels = [
        "Verb–object number\nagreement",
        "Differential object\nmarking",
        "Gender agreement",
    ]
    hours = [4 * 24 + 15, 7 * 24 + 15, 9 * 24]  # 4d15h, 7d15h, past 9d when last recorded
    done = [True, True, False]
    wall = 14 * 24

    fig, ax = plt.subplots(figsize=(7.4, 2.5))
    y = np.arange(len(labels))[::-1]

    for yi, h, is_done in zip(y, hours, done):
        ax.barh(yi, h, height=0.52, color=TEAL if is_done else AMBER, zorder=3)
        if is_done:
            d, r = divmod(h, 24)
            ax.text(h + 6, yi, f"{d} d {r} h", va="center", ha="left",
                    fontsize=12.5, color=INK, fontweight="bold", zorder=4)
        else:
            # Past nine days when the job script was last annotated. The completed
            # 1,000-permutation artefacts are committed, so it landed inside the wall;
            # the exact elapsed time was never recorded, hence the open bar.
            ax.annotate(
                "", xy=(wall - 26, yi), xytext=(h, yi),
                arrowprops=dict(arrowstyle="-|>", color=AMBER, lw=1.8,
                                linestyle=(0, (3, 2))), zorder=4,
            )
            ax.text(h + 8, yi + 0.38, "past 9 d, finished inside the wall",
                    va="center", ha="left", fontsize=11.5, color=INK,
                    fontweight="bold", zorder=4)

    ax.axvline(wall, color=REDLINE, lw=1.6, zorder=5)
    ax.text(wall - 6, 2.62, "14-day wall requested", ha="right", va="bottom",
            fontsize=12, color=REDLINE, fontweight="bold")

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=12, color=INK)
    ax.set_xlim(0, wall + 30)
    ax.set_xticks([0, 48, 96, 144, 192, 240, 288, 336])
    ax.set_xticklabels(["0", "2 d", "4 d", "6 d", "8 d", "10 d", "12 d", "14 d"],
                       fontsize=11.5)
    ax.set_ylim(-0.6, 2.95)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("Elapsed wall-clock time per array task", fontsize=12,
                  color=MUTED, labelpad=8)
    save(fig, "fig-decoding-runtime.svg")


# ---------------------------------------------------------------------------
# 2. Diarisation error rate per AMI meeting, decomposed
#    Source: the speech-transcription workflow's evaluation output, copied into
#            data/ as der_report.csv and der_summary.json. That project is not
#            public, so it is described rather than named.
# ---------------------------------------------------------------------------
def fig_der_meetings() -> None:
    with open(DATA / "der_report.csv", newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    with open(DATA / "der_summary.json", encoding="utf-8") as fh:
        summary = json.load(fh)

    rows.sort(key=lambda r: float(r["der"]))
    names = [r["meeting_id"] for r in rows]
    missed = np.array([float(r["missed_speech"]) for r in rows]) * 100
    fa = np.array([float(r["false_alarm"]) for r in rows]) * 100
    conf = np.array([float(r["speaker_confusion"]) for r in rows]) * 100

    fig, ax = plt.subplots(figsize=(6.8, 1.34))
    x = np.arange(len(names))
    ax.bar(x, missed, color=OI_SKY, label="Missed speech", zorder=3)
    ax.bar(x, fa, bottom=missed, color=OI_ORANGE, label="False alarm", zorder=3)
    ax.bar(x, conf, bottom=missed + fa, color=OI_VERMILLION,
           label="Speaker confusion", zorder=3)

    macro = summary["macro_der"] * 100
    ax.axhline(macro, color=INK, lw=1.3, ls=(0, (4, 2)), zorder=5)
    # Annotate at the left, over the short bars: at the right it sits on top of
    # the worst meetings, which are the ones the spread is about.
    ax.text(-0.3, macro + 2.4, f"macro DER {macro:.1f}%",
            ha="left", fontsize=11, color=INK, fontweight="bold")

    # The AMI meeting identifiers carry nothing a listener can use, and sixteen
    # of them rotated at 45 degrees cost a third of the figure's height. The
    # argument is the spread, so label the axis with what the bars are.
    ax.set_xticks([])
    ax.set_xlabel("16 AMI meetings, each a separate recording, sorted by error rate",
                  fontsize=10.5, color=MUTED)
    ax.set_ylabel("Diarisation error rate (%)", fontsize=11, color=MUTED)
    ax.set_ylim(0, 82)
    ax.legend(frameon=False, fontsize=10.5, ncol=3, loc="upper left",
              bbox_to_anchor=(0, 1.18), handlelength=1.1)
    ax.text(1.0, 1.18, f"{summary['collar_s']} s collar, "
            f"{summary['total_ref_duration']:.0f} s of reference speech",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=9.8, color=MUTED)
    save(fig, "fig-der-meetings.svg")


# ---------------------------------------------------------------------------
# 3. Inverse scaling: fit to human reading times against model size
#    Source: the language-data book's chapter 19 freeze output, the committed
#            result of the ARC GPU job that produced natural_stories_surprisal.csv.
#            That book is not public yet, so it is described rather than named.
# ---------------------------------------------------------------------------
def fig_inverse_scaling() -> None:
    # Values transcribed verbatim from the chapter's own rendered results table.
    models = ["70m", "160m", "410m", "1b", "1.4b", "2.8b"]
    params = np.array([70, 160, 410, 1000, 1400, 2800], dtype=float)
    delta_r2 = np.array(
        [0.03081831, 0.03459748, 0.03687462, 0.03544515, 0.03346395, 0.03086981]
    )
    slope = np.array(
        [1.586615, 1.980673, 2.064601, 2.109534, 2.010470, 2.010685]
    )

    fig, axes = plt.subplots(1, 2, figsize=(7.5, 3.0))

    ax = axes[0]
    ax.plot(params, slope, color=MUTED, lw=1.8, marker="o", ms=6, zorder=3)
    ax.set_xscale("log")
    ax.set_xticks(params)
    ax.set_xticklabels(models, fontsize=11.5)
    ax.minorticks_off()
    ax.set_ylabel("ms of reading time per bit", fontsize=11.5, color=MUTED)
    ax.set_title("Cost per bit — rises, then flattens", fontsize=12.5,
                 color=INK, pad=10, loc="left")

    ax = axes[1]
    ax.plot(params, delta_r2, color=TEAL, lw=2.2, marker="o", ms=6, zorder=3)
    peak = int(np.argmax(delta_r2))
    ax.plot(params[peak], delta_r2[peak], marker="o", ms=12, mfc="none",
            mec=TEAL, mew=2, zorder=4)
    ax.annotate("pythia-410m", xy=(params[peak], delta_r2[peak]),
                xytext=(0, 16), textcoords="offset points", ha="center",
                fontsize=11, color=TEAL, fontweight="bold")
    ax.set_xscale("log")
    ax.set_xticks(params)
    ax.set_xticklabels(models, fontsize=11.5)
    ax.minorticks_off()
    ax.set_ylim(0.0295, 0.0385)
    ax.set_ylabel("$\\Delta R^2$ beyond word length", fontsize=10.5, color=MUTED)
    ax.set_title("Fit to human reading — peaks, then falls",
                 fontsize=12.5, color=TEAL, pad=10, loc="left")

    for ax in axes:
        ax.set_xlabel("Pythia model size (parameters, log scale)",
                      fontsize=11.5, color=MUTED, labelpad=6)

    fig.text(0.5, -0.06, "61,488 aligned word-observations, Natural Stories corpus.",
             ha="center", fontsize=10, color=MUTED)
    fig.subplots_adjust(wspace=0.34)
    save(fig, "fig-inverse-scaling.svg")


# ---------------------------------------------------------------------------
# 4. The array index IS the design grid
#    Source: 03_fit_erp.slurm PARAMS block (property-major, then window,
#            then macroregion) -- reproduced exactly.
# ---------------------------------------------------------------------------
def fig_array_grid() -> None:
    properties = ["Gender\nagreement", "Differential\nobject marking",
                  "Verb–object number\nagreement"]
    windows = ["200–500 ms", "300–600 ms", "400–900 ms"]
    regions = ["lat", "mid"]

    fig, ax = plt.subplots(figsize=(6.2, 3.0))
    cw, ch, gap = 1.0, 0.78, 0.10

    idx = 0
    for pi, _prop in enumerate(properties):
        for wi, _win in enumerate(windows):
            for ri, _reg in enumerate(regions):
                x = wi * (cw + gap) + ri * (cw / 2)
                y = -pi * (ch + gap)
                ax.add_patch(Rectangle((x, y), cw / 2 - 0.02, ch,
                                       facecolor=TEAL if ri == 0 else "#e7eeef",
                                       edgecolor=RULE, lw=0.8, zorder=3))
                ax.text(x + cw / 4 - 0.01, y + ch / 2, str(idx),
                        ha="center", va="center", fontsize=12,
                        fontweight="bold",
                        color="white" if ri == 0 else INK, zorder=4)
                idx += 1

    for wi, win in enumerate(windows):
        ax.text(wi * (cw + gap) + cw / 2 - 0.01, ch + 0.14, win, ha="center",
                va="bottom", fontsize=11.5, color=INK, fontweight="bold")
    for pi, prop in enumerate(properties):
        ax.text(-0.22, -pi * (ch + gap) + ch / 2, prop, ha="right", va="center",
                fontsize=11.5, color=INK)

    ax.text(0, -3 * (ch + gap) + 0.30,
            "teal = lateral   ·   pale = midline   ·   "
            "enumerated property-major, then window, then macroregion",
            fontsize=10.5, color=MUTED, va="top")

    ax.set_xlim(-1.85, 3 * (cw + gap) + 0.1)
    ax.set_ylim(-3 * (ch + gap) + 0.05, ch + 0.46)
    ax.axis("off")
    save(fig, "fig-array-grid.svg")


# ---------------------------------------------------------------------------
# 5. Schematic: averaging away the data, versus keeping it
#    Illustrative only -- drawn, not measured. Labelled as such on the slide.
# ---------------------------------------------------------------------------
def fig_single_trial() -> None:
    rng = np.random.default_rng(20260910)
    t = np.linspace(-100, 900, 260)

    def erp(amp_p600: float) -> np.ndarray:
        n400 = -3.2 * np.exp(-((t - 380) ** 2) / (2 * 70.0**2))
        p600 = amp_p600 * np.exp(-((t - 620) ** 2) / (2 * 110.0**2))
        return n400 + p600

    fig, axes = plt.subplots(1, 2, figsize=(12.0, 1.40), sharey=True)

    trials = np.array([
        erp(rng.normal(4.2, 1.4))
        + np.cumsum(rng.normal(0, 0.42, t.size)) * 0.30
        + rng.normal(0, 0.9, t.size)
        for _ in range(48)
    ])

    ax = axes[0]
    for tr in trials:
        ax.plot(t, tr, color=MUTED, lw=0.4, alpha=0.16, zorder=2)
    ax.plot(t, trials.mean(axis=0), color=INK, lw=2.6, zorder=4)
    ax.set_title("Average first, then model", fontsize=13.5, color=INK,
                 loc="left", pad=10)
    ax.text(0.03, 0.04, "1 number per person per condition",
            transform=ax.transAxes, fontsize=12, color=INK,
            fontweight="bold")

    ax = axes[1]
    for tr in trials:
        ax.plot(t, tr, color=TEAL, lw=0.5, alpha=0.30, zorder=2)
    ax.set_title("Model every trial", fontsize=13.5, color=TEAL, loc="left",
                 pad=10)
    ax.text(0.03, 0.04, "75,654 rows in the largest cell",
            transform=ax.transAxes, fontsize=12, color=TEAL,
            fontweight="bold")

    for ax in axes:
        ax.axhline(0, color=RULE, lw=0.9, zorder=1)
        ax.axvline(0, color=RULE, lw=0.9, zorder=1)
        ax.set_xlabel("Time from word onset (ms)", fontsize=11.5, color=MUTED)
        ax.set_xlim(-100, 900)
        ax.set_ylim(-11, 13)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.tick_params(labelsize=9.5)
    axes[0].set_ylabel("Voltage (schematic)", fontsize=11.5, color=MUTED)

    # No figure caption: the slide's provenance line already says the panel is
    # a schematic, and at this height an in-figure caption collides with the
    # x-axis label.
    fig.subplots_adjust(wspace=0.08)
    save(fig, "fig-single-trial.svg")


# ---------------------------------------------------------------------------
# 7. Title-slide banner: the two signals the talk is actually about.
#    Decorative and schematic -- a speech waveform and an ERP trace.
# ---------------------------------------------------------------------------
def fig_title_waves() -> None:
    """One wave, drawn edge to edge.

    The title says two signals are on the same wavelength, so the cover shows a
    single continuous trace rather than a speech waveform and a brain trace side
    by side, labelled as two different things.

    This one figure is written without ``save()``: the axes fill the figure and
    there is no tight bounding box, so the ink reaches both ends of the canvas
    exactly. A tight box would crop to the ink and add ``pad_inches``, leaving a
    transparent gutter at each edge that ``preserveAspectRatio`` then centres --
    which is the difference between a full bleed and one that almost works.
    """
    rng = np.random.default_rng(1809)

    fig = plt.figure(figsize=(12.8, 1.94))
    ax = fig.add_axes((0.0, 0.0, 1.0, 1.0))

    t = np.linspace(0, 1, 4000)

    # Eight events, each with an event-related potential's own morphology: a
    # sharp negative deflection followed by a broader, larger positive one.
    # Amplitudes range over a factor of three and the spacing is uneven, with one
    # long quiet stretch, so the line reads as a recording and not as a repeating
    # motif. Decorative all the same: it illustrates nothing measured.
    #    (dip centre, dip depth, dip width, peak offset, peak height, peak width)
    events = (
        (0.030, -1.2, 0.011, 0.034, 1.9, 0.024),
        (0.150, -2.8, 0.014, 0.046, 4.2, 0.032),
        (0.255, -1.1, 0.009, 0.030, 1.6, 0.019),
        (0.430, -3.2, 0.016, 0.052, 4.8, 0.036),
        (0.585, -1.4, 0.010, 0.034, 2.2, 0.022),
        (0.700, -2.4, 0.013, 0.042, 3.4, 0.029),
        (0.870, -3.0, 0.015, 0.050, 4.4, 0.034),
        (0.975, -1.3, 0.010, 0.032, 1.8, 0.021),
    )
    wave = np.zeros_like(t)
    for centre, dip, dip_w, offset, peak, peak_w in events:
        wave += dip * np.exp(-((t - centre) ** 2) / (2 * dip_w**2))
        wave += peak * np.exp(-((t - centre - offset) ** 2) / (2 * peak_w**2))

    # A drift tied back to zero at both ends, so the quiet stretches stay alive
    # without the line wandering out of frame.
    drift = np.cumsum(rng.normal(0, 0.05, t.size))
    drift -= np.linspace(drift[0], drift[-1], t.size)
    wave += drift * 0.11

    ax.plot(t, wave, color=TEAL, lw=2.4, solid_capstyle="round")
    ax.set_xlim(0, 1)
    ax.set_ylim(-5.5, 5.5)
    ax.axis("off")

    path = OUT / "fig-title-waves.svg"
    fig.savefig(path, format="svg", transparent=True)
    plt.close(fig)
    print(f"  fig-title-waves.svg  ({path.stat().st_size // 1024} KB)")


# ---------------------------------------------------------------------------
def compose_title_background() -> None:
    import re

    def inner(path: Path, x: float, y: float, w: float, h: float) -> str:
        svg = path.read_text(encoding="utf-8")
        svg = re.sub(r"<\?xml[^>]*\?>", "", svg)
        svg = re.sub(r"<!DOCTYPE[^>]*>", "", svg, flags=re.S)
        svg = svg.strip()

        # Rewrite the nested root's geometry. The existing width/height MUST be
        # stripped first: repeating an attribute makes the document invalid XML,
        # and the whole composite then fails to render with no error shown.
        m = re.match(r"<svg\b([^>]*)>", svg, flags=re.S)
        if m is None:
            raise ValueError(f"no <svg> root in {path}")
        attrs = m.group(1)
        attrs = re.sub(r'\s(?:width|height|x|y)\s*=\s*"[^"]*"', "", attrs)
        head = (
            f'<svg x="{x}" y="{y}" width="{w}" height="{h}"'
            f' preserveAspectRatio="xMidYMid meet"{attrs}>'
        )
        return head + svg[m.end():]

    crest = inner(OUT / "oxford-crest.svg", 1148, 26, 92, 92)
    # Full bleed: x=0 to x=1280. The height matches the figure's own aspect
    # ratio (12.8 x 1.94 in), so "xMidYMid meet" has no gutter to letterbox
    # and the trace runs off both edges of the slide.
    waves = inner(OUT / "fig-title-waves.svg", 0, 486, 1280, 194)

    out = (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        'viewBox="0 0 1280 760" width="1280" height="760">\n'
        f"{crest}\n{waves}\n</svg>\n"
    )
    path = OUT / "title-background.svg"
    path.write_text(out, encoding="utf-8")
    print(f"  title-background.svg  ({path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    print("Building figures from committed result files...")
    fig_title_waves()
    fig_decoding_runtime()
    fig_der_meetings()
    fig_inverse_scaling()
    fig_array_grid()
    fig_single_trial()
    compose_title_background()
    print("Done.")
