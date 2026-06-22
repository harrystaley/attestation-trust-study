"""Create paste-ready Qualtrics question-block text.

AI assistance disclosure: this formatting/plumbing utility was written with the
assistance of an AI assistant (Claude) and reviewed by the author. It maps the
version-CSV columns to Qualtrics Loop & Merge piped fields and emits paste-ready
block text; the MEASURE WORDING (trust, reliance, perceived-consequence items)
is the author's instrument and is marked for the author to fill/confirm. This is
tooling, not graded analytical content. Use of generative AI follows the CS 6795
course policy.

What it produces
----------------
A text file you paste into Qualtrics (advanced-format import), containing:
  (1) the STIMULUS DISPLAY block (question + AI answer + attestation), with
      Loop & Merge piped fields (${lm://Field/N}) wired to the version-CSV
      columns by position, and
  (2) the THREE per-trial MEASURES (trust, reliance, perceived consequence)
      as separate questions.

This is item-agnostic tooling: it emits the SAME block text regardless of which
stimuli are in the CSV, because the actual stimulus content is supplied by
Qualtrics at run time via Loop & Merge piped fields, not embedded here.

Two things this version fixes vs. the earlier draft
---------------------------------------------------
  * Section markers are now Python comments only; they are NOT written into the
    emitted block text, so they cannot leak into the rendered question body.
  * The stimulus HTML follows its [[Question:Text]] header with correct
    adjacency (no comment or blank line between header and body).
  * Adds an optional CSV preprocessing helper that derives the <br>-rendered
    attestation column (newlines -> <br>) so the generator does not depend on
    the upstream CSV-builder having produced that column. Run-time use of the
    helper against any specific CSV is the author's step; the helper is generic.
"""

from __future__ import annotations
from pathlib import Path
import csv

# ---- Loop & Merge field map -------------------------------------------------
# These numbers are the 1-based column positions in the version_N.csv you import
# into the Loop & Merge field set. The default below matches the columns:
#   1 version | 2 stem_id | 3 stakes | 4 question_text | 5 answer_text |
#   6 att_level | 7 correctness | 8 attestation_text | 9 attestation_qualtrics
# Use the *_qualtrics column (newlines -> <br>) for the displayed attestation.
FIELD = {
    "question_text": 4,
    "answer_text": 5,
    "attestation": 9,   # attestation_qualtrics (the <br>-rendered version)
    "stem_id": 2,
    "stakes": 3,
    "att_level": 6,
    "correctness": 7,
}

OUT = Path("output/qualtrics_block.txt")


def lm(field: str) -> str:
    """Return the Qualtrics Loop & Merge piped reference for a mapped field."""
    return f"${{lm://Field/{FIELD[field]}}}"


# ---- CSV preprocessing helper (generic, item-agnostic) ----------------------
def add_br_attestation_column(
    in_csv: str | Path,
    out_csv: str | Path,
    src_col: str = "attestation_text",
    new_col: str = "attestation_qualtrics",
) -> None:
    """Copy a CSV, adding a column whose value is `src_col` with newlines -> <br>.

    This makes the generator independent of whether the upstream CSV-builder
    already produced the <br>-rendered attestation column. It operates on
    whatever rows are present and does not inspect or judge their content; it is
    pure newline->markup conversion. Point it at the CSV of your choice.
    """
    in_path, out_path = Path(in_csv), Path(out_csv)
    with in_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        if src_col not in fieldnames:
            raise KeyError(f"source column {src_col!r} not in CSV header: {fieldnames}")
        if new_col not in fieldnames:
            fieldnames.append(new_col)
        rows = []
        for row in reader:
            raw = row.get(src_col, "") or ""
            # Normalize CRLF/CR to LF first, then convert LF to <br>.
            normalized = raw.replace("\r\n", "\n").replace("\r", "\n")
            row[new_col] = normalized.replace("\n", "<br>")
            rows.append(row)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_block() -> str:
    """Build the paste-ready block text.

    No stimulus content appears here: every piece of per-trial content is a
    Loop & Merge piped reference resolved by Qualtrics at run time.
    """
    q = lm("question_text")
    a = lm("answer_text")
    att = lm("attestation")

    # (1) STIMULUS DISPLAY -----------------------------------------------------
    # Rendered as the body of a [[Question:Text]] (Descriptive Text / Graphic),
    # which renders HTML. The attestation field is empty for the 'none'
    # condition, so the provenance area renders blank -- identical container.
    # NOTE: no HTML comment is emitted into the body (that would render to the
    # participant). Section labels live only in this source, as Python comments.
    stimulus = (
        '<div style="max-width:640px">\n'
        f'  <p><strong>Question:</strong> {q}</p>\n'
        '  <div style="border:1px solid #ccc; border-radius:6px; '
        'padding:12px; margin-top:8px">\n'
        f'    <p style="margin:0">{a}</p>\n'
        '    <div style="color:#555; font-size:0.9em; margin-top:10px">'
        f'{att}</div>\n'
        '  </div>\n'
        '</div>'
    )

    # (2) MEASURES -------------------------------------------------------------
    # WORDING IS YOURS. The text below is placeholder phrasing matching your
    # report's measures; replace with your authored item wording before use.
    # (Anchor wording here must be reconciled with the report's tab:trust-scale;
    # the two currently differ -- author's decision.)
    trust = (
        "[[Question:MC:SingleAnswer:Horizontal]]\n"
        "[[ID:trust]]\n"
        "How much do you trust this answer?\n"
        "[[Choices]]\n"
        "1 (Do not trust at all)\n"
        "2\n3\n4 (Neither trust nor distrust)\n5\n6\n"
        "7 (Completely trust)"
    )

    reliance = (
        "[[Question:MC:SingleAnswer]]\n"
        "[[ID:reliance]]\n"
        "What would you do with this answer?\n"
        "[[Choices]]\n"
        "Reject \u2014 do not use the information or take the recommended action.\n"
        "Verify before taking action or using the information.\n"
        "Use the information or take the recommended action (do not double-check)."
    )

    consequence = (
        "[[Question:MC:SingleAnswer:Horizontal]]\n"
        "[[ID:consequence]]\n"
        "If you acted on this answer and it turned out to be wrong, "
        "how serious would the outcome be?\n"
        "[[Choices]]\n"
        "1 (Not serious at all)\n2\n3\n4\n5 (Extremely serious)"
    )

    # Assemble. The stimulus HTML immediately follows its [[Question:Text]]
    # header with no intervening comment or blank line, so Qualtrics treats it
    # as that question's body.
    blocks = [
        "[[AdvancedFormat]]",
        "",
        "[[Block:Trial]]",
        "",
        "[[Question:Text]]",
        stimulus,
        "",
        trust,
        "",
        reliance,
        "",
        consequence,
        "",
    ]
    return "\n".join(blocks)


def main() -> None:
    text = build_block()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")

    print(f"Wrote paste-ready block -> {OUT}\n")
    print("Loop & Merge field map (1-based column position in version_N.csv):")
    for name, num in FIELD.items():
        print(f"  Field {num}: {name}")
    print("\nIMPORTANT:")
    print("  - Qualtrics ADVANCED-FORMAT text import:")
    print("    Survey > Tools > Import/Export > Import Questions From... > paste this file.")
    print("  - Confirm your imported Loop & Merge column order matches the field map.")
    print("  - The attestation field uses column 9 (attestation_qualtrics, <br>-rendered).")
    print("    If your CSV lacks column 9, run add_br_attestation_column() on it first.")
    print("  - MEASURE WORDING is placeholder; replace with your authored items, and")
    print("    reconcile the trust anchors with the report's tab:trust-scale.")
    print("  - Advanced-format import creates QUESTIONS; you still build the Loop & Merge,")
    print("    the 6-version Randomizer, and the Survey Flow in the UI.")
    print("  - VERIFY RENDERING: preview one trial whose attestation is the multi-line")
    print("    (strong) condition and confirm the lines stack (HTML) rather than showing")
    print("    literal <br>. If literal, switch the question body to HTML/rich-content mode.")


if __name__ == "__main__":
    main()