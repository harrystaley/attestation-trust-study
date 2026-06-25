"""Prepare the reconstructed pilot data for mixed-effects analysis.

AI assistance disclosure: this data-cleaning/plumbing utility was written with
the assistance of an AI assistant (Claude) and reviewed by the author. It parses
Qualtrics text labels into numeric codes and adds analysis codings; it does not
fit models, interpret results, or author any analytical conclusions. This is
tooling, not graded analytical content. Use of generative AI follows the CS 6795
course policy.

WHAT IT DOES
------------
Takes the long-format file from ``reconstruct_pilot_conditions.py`` (one row per
participant-trial, with condition codes restored) and produces a model-ready
file by:

  1. Parsing TRUST from its Qualtrics label (e.g. "5 Slightly Trust") to the
     integer 1..7 (the leading number). Handles label variants that share a
     number (e.g. two phrasings of "4").
  2. Coding RELIANCE from its three text options to an ordinal 1/2/3
     (reject / verify / use), ordered by increasing uncritical reliance.
  3. Parsing CONSEQUENCE from its label to the integer 1..5.
  4. Adding analysis codings that MATCH the power simulation, so the prepped
     data is directly comparable to the simulated design:
       - att_code: none=0, weak=1, strong=2  (linear-trend coding)
       - corr_code: incorrect=-0.5, correct=+0.5  (centered)
       - stakes_code: low=-0.5, high=+0.5  (centered)
  5. Validating: every trust/consequence value parses to its expected range,
     every reliance maps to a known option, and reporting any rows that fail.

WHAT IT DOES NOT DO
-------------------
It does not fit models, compute effect sizes, test hypotheses, or apply
exclusion criteria (attention-check / completion-time / bot screens). Those are
separate, author-owned steps. Note also: this PILOT (n=16) is for pipeline
validation and rough power-input estimation only -- it is far too small for
hypothesis testing, and no quality-exclusions are applied here.

INPUT CONTRACT
--------------
A CSV with columns: response_id, version, trial_position, loop_num, stem_id,
stakes, att_level, correctness, trust, reliance, consequence
(i.e. the output of reconstruct_pilot_conditions.py).

OUTPUT
------
A CSV adding numeric columns: trust_num, reliance_code, consequence_num,
att_code, corr_code, stakes_code. Original columns are preserved.
"""

from __future__ import annotations
from pathlib import Path
import csv
import re

# ---- editor-run config ------------------------------------------------------
INPUT_DIR = "../prepped_data"
INPUT_FILE = "long_reconstructed.csv"
OUTPUT_DIR = "../prepped_data"
OUTPUT_FILE = "long_coded.csv"
# ----------------------------------------------------------------------------

# Reliance text -> ordinal, ordered by increasing uncritical reliance.
# Matched by a distinctive substring so minor punctuation differences still map.
RELIANCE_CODE = {
    "reject": 1,   # "Reject — do not use..."
    "verify": 2,   # "Verify before taking action..."
    "use": 3,      # "Use the information or take the recommended action..."
}

# Categorical -> numeric codings (MATCH the power simulation).
ATT_CODE = {"none": 0, "weak": 1, "strong": 2}
CORR_CODE = {"incorrect": -0.5, "correct": 0.5}
STAKES_CODE = {"low": -0.5, "high": 0.5}

_LEADING_INT = re.compile(r"^\s*(\d+)")


def parse_leading_int(label: str) -> int | None:
    """Return the leading integer in a Qualtrics scale label, or None.

    Examples: "5 Slightly Trust" -> 5; "4 (Neither trust nor distrust)" -> 4;
    "1 (Not serious at all)" -> 1; "" -> None.
    """
    if label is None:
        return None
    m = _LEADING_INT.match(label)
    return int(m.group(1)) if m else None


def code_reliance(label: str) -> int | None:
    """Map a reliance option label to its ordinal code (1/2/3), or None.

    Matches by a distinctive lowercase substring (reject / verify / use) so that
    em-dash vs hyphen or trailing-text differences do not break the mapping.
    """
    if not label:
        return None
    low = label.strip().lower()
    if low.startswith("reject"):
        return RELIANCE_CODE["reject"]
    if low.startswith("verify"):
        return RELIANCE_CODE["verify"]
    if low.startswith("use"):
        return RELIANCE_CODE["use"]
    return None


def prepare(in_csv: str | Path, out_csv: str | Path) -> None:
    """Code the reconstructed data into model-ready numeric form.

    Args:
        in_csv: Path to the reconstructed long-format CSV.
        out_csv: Path to write the coded CSV (parent dir created if absent).

    Raises:
        KeyError: if a required column is missing.

    Prints a validation report: how many rows coded cleanly and any that failed
    (with their row index), so parsing problems are visible rather than silent.
    """
    in_path = Path(in_csv)
    with in_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"response_id", "stem_id", "stakes", "att_level",
                    "correctness", "trust", "reliance", "consequence"}
        header = set(reader.fieldnames or [])
        missing = required - header
        if missing:
            raise KeyError(f"input missing required columns: {sorted(missing)}")
        rows = list(reader)

    out_fields = list(rows[0].keys()) + [
        "trust_num", "reliance_code", "consequence_num",
        "att_code", "corr_code", "stakes_code",
    ]

    fails: list[tuple[int, str]] = []
    for idx, r in enumerate(rows):
        trust = parse_leading_int(r.get("trust", ""))
        rel = code_reliance(r.get("reliance", ""))
        cons = parse_leading_int(r.get("consequence", ""))
        att = ATT_CODE.get((r.get("att_level") or "").strip().lower())
        corr = CORR_CODE.get((r.get("correctness") or "").strip().lower())
        stk = STAKES_CODE.get((r.get("stakes") or "").strip().lower())

        # validation: flag any unparseable / out-of-range field
        if trust is None or not (1 <= trust <= 7):
            fails.append((idx, f"trust={r.get('trust')!r}"))
        if rel is None:
            fails.append((idx, f"reliance={r.get('reliance')!r}"))
        if cons is None or not (1 <= cons <= 5):
            fails.append((idx, f"consequence={r.get('consequence')!r}"))
        if att is None:
            fails.append((idx, f"att_level={r.get('att_level')!r}"))
        if corr is None:
            fails.append((idx, f"correctness={r.get('correctness')!r}"))
        if stk is None:
            fails.append((idx, f"stakes={r.get('stakes')!r}"))

        r["trust_num"] = trust if trust is not None else ""
        r["reliance_code"] = rel if rel is not None else ""
        r["consequence_num"] = cons if cons is not None else ""
        r["att_code"] = att if att is not None else ""
        r["corr_code"] = corr if corr is not None else ""
        r["stakes_code"] = stk if stk is not None else ""

    out_path = Path(out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=out_fields)
        w.writeheader()
        w.writerows(rows)

    n_ok = len(rows) - len({i for i, _ in fails})
    print(f"Coded {len(rows)} rows -> {out_path}")
    print(f"  cleanly coded rows: {n_ok}/{len(rows)}")
    if fails:
        print(f"  WARNING: {len(fails)} field-level parse problems:")
        for idx, msg in fails[:20]:
            print(f"    row {idx}: {msg}")
        if len(fails) > 20:
            print(f"    ... and {len(fails) - 20} more")
    else:
        print("  all fields parsed and in range.")
    print("\nNOTE: this is PILOT data (n small), prepped for pipeline validation")
    print("and rough power-input estimation only -- not hypothesis testing, and")
    print("no quality-exclusions are applied here.")


if __name__ == "__main__":
    here = Path(__file__).parent
    inp = Path(INPUT_DIR) / INPUT_FILE
    if not inp.is_absolute():
        inp = here / INPUT_DIR / INPUT_FILE
    outp = Path(OUTPUT_DIR) / OUTPUT_FILE
    if not outp.is_absolute():
        outp = here / OUTPUT_DIR / OUTPUT_FILE
    if not inp.exists():
        print(f"Input not found: {inp}")
        print("Set INPUT_DIR/INPUT_FILE to your reconstructed long CSV.")
    else:
        prepare(inp, outp)