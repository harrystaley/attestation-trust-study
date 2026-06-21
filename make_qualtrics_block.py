"""Create paste-ready Qualtrics question-block text.

AI assistance disclosure: this formatting/plumbing utility was written with the
assistance of an AI assistant (Claude) and reviewed by the author. It maps the
version-CSV columns to Qualtrics Loop & Merge piped fields and emits paste-ready
block text; the MEASURE WORDING (trust, reliance, consequence, knowledge items)
is the author's instrument and is marked for the author to fill/confirm. This is
tooling, not graded analytical content. Use of generative AI follows the CS 6795
course policy.

What it produces
----------------
A text file you paste into Qualtrics, containing:
  (1) the STIMULUS DISPLAY block (question + AI answer + attestation), with
      Loop & Merge piped fields (${lm://Field/N}) already wired to the version
      CSV columns by position, and
  (2) the THREE per-trial MEASURES (trust, reliance, perceived
      consequence) as separate questions.

Loop & Merge field numbers are the 1-based COLUMN POSITION in the version CSV
you import. Confirm your imported column order matches the map printed below.
"""

from __future__ import annotations
from pathlib import Path

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


def build_block() -> str:
    """Build the paste-ready block text."""
    q = lm("question_text")
    a = lm("answer_text")
    att = lm("attestation")

    # ---- (1) STIMULUS DISPLAY -------------------------------------------------
    # Pasted as a Descriptive Text / Text-Graphic question, or as the header of
    # the trust question. The attestation field is empty for the 'none' condition,
    # so the provenance area simply renders blank -- identical container.
    stimulus = f"""<!-- ===== STIMULUS DISPLAY (paste as a Text/Graphic question) ===== -->
<div style="max-width:640px">
  <p><strong>Question:</strong> {q}</p>
  <div style="border:1px solid #ccc; border-radius:6px; padding:12px; margin-top:8px">
    <p style="margin:0">{a}</p>
    <div style="color:#555; font-size:0.9em; margin-top:10px">{att}</div>
  </div>
</div>"""

    # ---- (2) MEASURES ---------------------------------------------------------
    # WORDING IS YOURS. The text below is placeholder/standard phrasing matching
    # your report's measures; replace with your authored item wording before use.
    trust = """<!-- ===== MEASURE 1: STATE TRUST (1-7, primary outcome) ===== -->
[[Question:MC:SingleAnswer:Horizontal]]
[[ID:trust]]
How much do you trust this answer?
[[Choices]]
1 (Do not trust at all)
2
3
4 (Neither trust nor distrust)
5
6
7 (Completely trust)"""

    reliance = """<!-- ===== MEASURE 2: BEHAVIORAL RELIANCE (reject/verify/act) ===== -->
[[Question:MC:SingleAnswer]]
[[ID:reliance]]
What would you do with this answer?
[[Choices]]
Reject — do not use the information or take the recommended action.
Verify before taking action or using the information.
Use the information or take the recommended action (do not double-check)."""

    consequence = """<!-- ===== MEASURE 3: PERCEIVED CONSEQUENCE (mediator) ===== -->
[[Question:MC:SingleAnswer:Horizontal]]
[[ID:consequence]]
If you acted on this answer and it turned out to be wrong, how serious would the outcome be?
[[Choices]]
1 (Not serious at all)
2
3
4
5 (Extremely serious)"""

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
    print("  - This uses Qualtrics ADVANCED-FORMAT text import. In Qualtrics:")
    print("    Survey > Tools > Import/Export > Import Questions From... > paste this file.")
    print("  - Confirm your imported Loop & Merge column order matches the field map.")
    print("  - The attestation field uses column 9 (attestation_qualtrics, <br>-rendered).")
    print("  - MEASURE WORDING is placeholder-standard; replace with your authored items.")
    print("  - Advanced-format import creates QUESTIONS; you still build the Loop & Merge,")
    print("    the 6-version Randomizer, and the Survey Flow in the UI.")


if __name__ == "__main__":
    main()