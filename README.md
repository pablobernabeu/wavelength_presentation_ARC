# On the same wavelength: Words, brainwaves and HPC

Slides for the Oxford Research Computing Community Event, 10 September 2026, by Pablo Bernabeu
(Department of Education, University of Oxford).

**[View the slides](https://pablobernabeu.github.io/wavelength_presentation_ARC/)** ·
[PDF](docs/on-the-same-wavelength.pdf)

Psycholinguistic analysis has moved onto the cluster, largely because of what we now do with the
data. We model individual trials instead of condition averages, we simulate whole study designs
before recruiting anyone, and we transcribe interviews that cannot leave the institution.

The talk follows three strands of this work on Oxford's Advanced Research Computing (ARC)
facility. The first is large behavioural datasets, where the number of participants a study needs
has no closed formula and has to be estimated by simulation. The second is EEG, where keeping
every trial turns an analysis that once ran on a laptop into a week of computation. The third is
speech, where data protection rules out cloud transcription and where a GPU earns its place. Two
of the three run entirely on CPUs, and the longest job described never requests a GPU.

## Contents

The deck is written in Quarto and renders to a single self-contained HTML file.

| Path | What it holds |
|---|---|
| `slides/on-the-same-wavelength.qmd` | the deck's source, including speaker notes |
| `assets/css/wavelength.scss` | the theme |
| `assets/img/` | every figure, as SVG |
| `scripts/make_figures.py` | draws the figures from the files in `data/` |
| `scripts/estimate_timing.py` | costs the deck in minutes from its own source |
| `scripts/render.ps1` | rebuilds figures, HTML and the PDF in one step |
| `data/` | the committed result files the figures are drawn from |
| `docs/` | the rendered deck, which is what GitHub Pages serves |
| `notes/abstract.md` | the submitted abstract |

## Presenting

Open `docs/index.html` in a browser. It embeds every image, style and script, so it runs from a
USB stick on a venue laptop with no network. Press <kbd>S</kbd> for speaker view, <kbd>F</kbd>
for full screen, <kbd>Esc</kbd> for the slide overview and <kbd>?</kbd> for the rest of the
shortcuts.

## Rebuilding

```powershell
pwsh -NoProfile -File scripts/render.ps1 -Pdf
```

Or step by step:

```powershell
python scripts/make_figures.py
quarto render slides/on-the-same-wavelength.qmd
Copy-Item slides/index.html docs/index.html -Force
```

The deck uses Quarto's `markdown` engine and every figure is a pre-generated SVG, so no R is
needed. Only `scripts/make_figures.py` requires Python, with matplotlib and numpy.

`python scripts/estimate_timing.py` recomputes the deck's running time from the source, counting
body words at 140 a minute and charging a fixed beat for each code block, table and slide change.
The figure in this README therefore cannot drift away from the slides. The deck runs to about
fifteen minutes.

## Where the figures come from

`data/` holds result files copied out of the projects the talk describes, so that every figure
can be redrawn from what is in this repository.

| File | Source |
|---|---|
| `der_report.csv`, `der_summary.json` | diarisation evaluation on the AMI Meeting Corpus |
| `timestamp_summary.json`, `timestamp_vad.json` | segment-boundary evaluation, before and after voice-activity refinement |
| `03_fit_erp.slurm` | the Slurm array that fits the single-trial ERP models |
| `submit_sweep.sh` | the Slurm array behind the transcription benchmark |

Two figures are schematic, and say so on the slide: the single-trial EEG illustration and the
wave on the title slide.

Every claim on a slide is sourced in small type at the foot of that slide, to a file in one of
the underlying projects or to ARC's own documentation. Other people's work carries a credit in
the same place and a full reference on the last backup slide.

## What is deliberately absent

The deck and this repository carry no job identifiers, no project account codes, no usernames, no
node hostnames, no filesystem paths from the underlying projects, and no totals for compute
consumed. None of it would help an audience, and some of it is nobody else's business.
`data/submit_sweep.sh` is a real submission script with two directory names replaced by
placeholders, and its header says so.

Three runtimes do appear: a decoding array against its wall-clock limit, a set of compiler
timings, and 18 minutes against 43 hours for one simulation batch. Each is there to show why the
work needs a cluster, not to report what it cost.

## Licence and contact

The slides are CC BY 4.0. The underlying research artefacts stay under their own repositories'
licences: the transcription workflow is archived at
[doi.org/10.5281/zenodo.17624830](https://doi.org/10.5281/zenodo.17624830) under CC BY 4.0, and
the AMI Meeting Corpus is CC BY 4.0 and credited on the slides that use it.

The acknowledgement ARC asks for:

> The authors would like to acknowledge the use of the University of Oxford Advanced Research
> Computing (ARC) facility in carrying out this work.
> <https://doi.org/10.5281/zenodo.22558>

Pablo Bernabeu, [pablo.bernabeu@education.ox.ac.uk](mailto:pablo.bernabeu@education.ox.ac.uk) ·
[ORCID 0000-0003-1083-2460](https://orcid.org/0000-0003-1083-2460) ·
[pablobernabeu.github.io](https://pablobernabeu.github.io/)
