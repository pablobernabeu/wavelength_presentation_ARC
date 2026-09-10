"""Estimate how long the deck takes to deliver, from the deck itself.

The point is that the estimate cannot drift away from the slides. Every earlier version of this
talk carried a hand-written total in the README, and every one of them was optimistic, because
the arithmetic was done once and the slides kept growing.

Method. Prose on a slide is costed at a delivery rate; code blocks and tables are costed as
fixed reading beats instead, because a speaker walks those with the audience rather than
uttering every token. Speaker notes and provenance footers are excluded: they are not spoken as
written. The backup slides are excluded: they are for questions.

The rate is the conservative end of what a technical talk actually runs (roughly 130-150 words
a minute); a rehearsed speaker who summarises dense bullets rather than reading them will come
in under the estimate, which is the direction an estimate should err in.

Run:  python scripts/estimate_timing.py
"""

from __future__ import annotations

import re
from pathlib import Path

WORDS_PER_MINUTE = 140   # conservative for a technical talk
CODE_BEAT_S = 18         # walking one slide's sbatch header with the audience
TABLE_BEAT_S = 10        # walking one table
TRANSITION_S = 2         # per slide change
OPENING_S = 25           # the scripted opening, spoken over the title slide

DECK = Path(__file__).resolve().parent.parent / "slides" / "on-the-same-wavelength.qmd"


def main() -> None:
    source = DECK.read_text(encoding="utf-8").split("---", 2)[2]
    source = re.sub(r"::: notes.*?\n:::\n", "", source, flags=re.S)

    prose_words = code_slides = table_slides = slides = 0
    rows: list[tuple[int, str]] = []

    for part in re.split(r"\n#{1,2} ", source)[1:]:
        heading = part.split("\n")[0]
        if "appendix" in heading:          # backup slides are not part of the talk
            continue

        body = re.sub(r"::: src.*?\n:::\n", "", part, flags=re.S)

        has_code = bool(re.search(r"``` bash\n.*?```", body, flags=re.S))
        body = re.sub(r"``` bash\n.*?```", "", body, flags=re.S)

        has_table = any(line.strip().startswith("|") for line in body.split("\n"))
        body = "\n".join(l for l in body.split("\n") if not l.strip().startswith("|"))

        body = re.sub(r"[:`|*{}\[\]#>]", " ", body)
        body = re.sub(r"\bstyle=\S+", " ", body)
        words = len([w for w in body.split() if any(c.isalnum() for c in w)])

        prose_words += words
        slides += 1
        code_slides += has_code
        table_slides += has_table
        rows.append((words, heading.split("{")[0].strip()))

    overhead = (
        OPENING_S
        + code_slides * CODE_BEAT_S
        + table_slides * TABLE_BEAT_S
        + slides * TRANSITION_S
    )
    seconds = prose_words / WORDS_PER_MINUTE * 60 + overhead

    for words, heading in rows:
        print(f"{words:5d}  {heading}")
    print()
    print(f"{slides} content slides, {prose_words} words of body prose")
    print(f"  speaking at {WORDS_PER_MINUTE} wpm      {prose_words / WORDS_PER_MINUTE * 60:6.0f} s")
    print(f"  opening over the title slide  {OPENING_S:6d} s")
    print(f"  {code_slides} code blocks walked         {code_slides * CODE_BEAT_S:6d} s")
    print(f"  {table_slides} tables walked              {table_slides * TABLE_BEAT_S:6d} s")
    print(f"  {slides} slide changes            {slides * TRANSITION_S:6d} s")
    print(f"  ESTIMATED TOTAL               {seconds:6.0f} s"
          f"  = {int(seconds // 60)} min {round(seconds % 60):02d} s")
    if seconds > 900:
        print(f"\n  Over the 15-minute slot by {round(seconds - 900)} s."
              " See the cut list in README.md.")


if __name__ == "__main__":
    main()
