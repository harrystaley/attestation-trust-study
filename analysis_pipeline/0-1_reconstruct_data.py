"""Reconstruct per-trial condition codes for the pilot Qualtrics export.

AI assistance disclosure: this data-reshaping/plumbing utility was written with
the assistance of an AI assistant (Claude) and reviewed by the author. It joins
exported response cells to condition codes by structural keys (block signature,
loop position) and the author's version files; it does not inspect, judge, or
author any stimulus content. This is tooling, not graded analytical content.
Use of generative AI follows the CS 6795 course policy.

THE PROBLEM THIS SOLVES
-----------------------
The Qualtrics export saved per-trial responses (trust/reliance/consequence) but
NOT the per-trial condition codes (stem_id, att_level, correctness, stakes),
because the Loop & Merge fields were not written to the response data. This
script reconstructs those codes.

WHY RECONSTRUCTION IS POSSIBLE (and its load-bearing assumption)
---------------------------------------------------------------
Each respondent went through exactly one of six Trial blocks (one per version),
identifiable by the block's distinct question-ID signature. Within a block, the
12 trials appear under consecutive loop numbers. Because loop order was FIXED
(Qualtrics Loop & Merge Randomization='All' in the exported QSF), loop POSITION
i (1..12) corresponds to ROW i of that block's version file. So:

    respondent -> block signature -> version file -> row i -> condition codes

*** CRITICAL ASSUMPTION: loop order was NOT randomized at collection. ***
If loop order WAS randomized when the pilot ran, presentation order does not
match version-file row order, and this reconstruction is INVALID -- the per-trial
condition mapping cannot be recovered from this export, and the real fix is to
capture condition codes as embedded data before the real launch. The exported
QSF showed 'All' (fixed), which is the basis for proceeding; verify this matches
how the survey actually ran when the pilot was collected.

WHAT YOU MUST SUPPLY
--------------------
BLOCK_TO_VERSION below maps each block's question-ID signature to the version
file number you loaded into that block. The default assumes Trial blocks were
built in order (block 1 <- version_1 ... block 6 <- version_6), inferred from the
loop-number ordering. CONFIRM THIS against how you actually assigned versions to
blocks; a wrong mapping silently mislabels every condition.

OUTPUT
------
A long-format CSV: one row per participant-trial, with columns
    response_id, version, trial_position, stem_id, stakes, att_level,
    correctness, trust, reliance, consequence,
    age, gender, education, ai_frequency, ai_expertise, baseline_trust, consent
suitable for the mixed-effects analysis and for estimating pilot effect sizes.
The trailing intake columns (age..consent) are per-participant values, answered
once and repeated on every trial row for that participant; they come from plain
(non-looped) Qualtrics columns and are configured in INTAKE_COLUMNS below.
"""

from __future__ import annotations
from pathlib import Path
import csv
import re
import zipfile
import tempfile

# ---- editor-run config ------------------------------------------------------
# EXPORT may be EITHER a Qualtrics .zip export OR the .csv inside it. If a .zip
# is given, the CSV is extracted automatically (you do not need to unzip first).
EXPORT_DIR = "../qdata"
EXPORT_FILE = "AI_Attestation_Trust_Study_06-25-2026T1938.zip"
VERSION_DIR = "../versions_output"   # folder holding version_1.csv .. version_6.csv
OUTPUT_DIR = "../prepped_data"
OUTPUT_CSV = "long_reconstructed.csv"

# Map each block's question-ID signature -> version file number.
# DEFAULT inferred from loop-number order (block creation order). CONFIRM!
# The measure question IDs per block (Trust, Reliance, Consequence in that order):
BLOCK_TO_VERSION = {
    ("Trust", "Reliance", "Consiquence"): 1,   # block 1 (loops 1-12)
    ("Q22", "Q23", "Q24"): 2,                   # block 2 (loops 2-13)
    ("Q26", "Q27", "Q28"): 3,                   # block 3 (loops 14-25)
    ("Q30", "Q31", "Q32"): 4,                   # block 4 (loops 26-37)
    ("Q34", "Q35", "Q36"): 5,                   # block 5 (loops 38-49)
    ("Q38", "Q39", "Q40"): 6,                   # block 6 (loops 50-61)
}

# Within each block, which Q-id is which measure. The trio is ordered
# (Trust-col, Reliance-col, Consequence-col) for each block.
MEASURE_TRIPLES = {
    1: ("Trust", "Reliance", "Consiquence"),
    2: ("Q22", "Q23", "Q24"),
    3: ("Q26", "Q27", "Q28"),
    4: ("Q30", "Q31", "Q32"),
    5: ("Q34", "Q35", "Q36"),
    6: ("Q38", "Q39", "Q40"),
}

# Per-participant intake / control items, answered ONCE (not per loop). These are
# plain Qualtrics columns named by their DataExportTag (recovered from the QSF).
# Each is attached to every trial row for that respondent, keyed on ResponseId.
# LEFT = the export column header; RIGHT = the output column name.
# If your export headers differ, edit the LEFT side.
INTAKE_COLUMNS = {
    "Age":            "age",
    "Gender":         "gender",
    "Education":      "education",
    "AI Use":         "ai_frequency",     # Never/Monthly/Weekly/Daily
    "Q44":            "ai_expertise",     # Novice..Expert/Specialist (tag is Q44)
    "Baseline Trust": "baseline_trust",   # general trust in AI (5-point)
    "Consent":        "consent",          # Agree/Disagree (useful as a screen)
}
# ----------------------------------------------------------------------------

QID_RE = re.compile(r'^(\d+)_(Q\d+|Trust|Reliance|Consiquence|Consequence)$')


def resolve_export_csv(export_path: str | Path) -> tuple[Path, tempfile.TemporaryDirectory | None]:
    """Return a path to the response CSV, extracting from a .zip if needed.

    Accepts either a Qualtrics ``.zip`` export or the ``.csv`` directly. For a
    zip, extracts to a temporary directory and locates the single CSV inside
    (matching by extension, not by exact name, so the timestamped Qualtrics
    filename does not have to be specified).

    Args:
        export_path: Path to a ``.zip`` or ``.csv``.

    Returns:
        A tuple ``(csv_path, tmpdir)``. ``tmpdir`` is a TemporaryDirectory that
        must be kept alive while the CSV is read (the caller holds it and lets it
        clean up on exit); it is ``None`` when the input was already a CSV.

    Raises:
        FileNotFoundError: if the path does not exist.
        ValueError: if a zip contains zero or multiple CSVs, or the file is
            neither .zip nor .csv.
    """
    p = Path(export_path)
    if not p.exists():
        raise FileNotFoundError(f"export not found: {p}")

    if p.suffix.lower() == ".csv":
        return p, None

    if p.suffix.lower() == ".zip":
        tmp = tempfile.TemporaryDirectory(prefix="qualtrics_export_")
        with zipfile.ZipFile(p) as zf:
            csv_names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
            if not csv_names:
                tmp.cleanup()
                raise ValueError(f"no .csv found inside zip: {p}")
            if len(csv_names) > 1:
                # Qualtrics exports one CSV; if more, that's unexpected -- be loud.
                tmp.cleanup()
                raise ValueError(
                    f"expected one CSV in zip, found {len(csv_names)}: {csv_names}"
                )
            zf.extract(csv_names[0], tmp.name)
        return Path(tmp.name) / csv_names[0], tmp

    raise ValueError(f"export must be .zip or .csv, got: {p.suffix!r}")


def load_versions(version_dir: str | Path) -> dict[int, list[dict]]:
    """Load version_1.csv .. version_6.csv. Returns {version_num: [row,...]}.

    Each row keeps stem_id, stakes, att_level, correctness in file order, so
    list index i is loop position i.
    """
    vdir = Path(version_dir)
    versions: dict[int, list[dict]] = {}
    for v in range(1, 7):
        path = vdir / f"version_{v}.csv"
        with path.open(newline="", encoding="utf-8") as f:
            versions[v] = list(csv.DictReader(f))
        if len(versions[v]) != 12:
            raise ValueError(f"version_{v}.csv has {len(versions[v])} rows; expected 12")
    return versions


def reconstruct(export_csv: str | Path, version_dir: str | Path,
                out_csv: str | Path) -> None:
    """Join responses to condition codes and write the long-format file.

    For each respondent: identify their block by the question-ID signature,
    look up the version file, and for each loop position read the trust/
    reliance/consequence cells and attach that version row's condition codes.

    Raises:
        ValueError: if a respondent's block signature is not in BLOCK_TO_VERSION,
            or a version file is the wrong length.
    """
    versions = load_versions(version_dir)

    resolved_csv, _tmp = resolve_export_csv(export_csv)
    try:
        with open(resolved_csv, encoding="utf-8") as fh:
            rows = list(csv.reader(fh))
    finally:
        if _tmp is not None:
            _tmp.cleanup()
    varnames = rows[0]
    data = rows[3:]  # 3 Qualtrics header rows
    rid_idx = varnames.index("ResponseId") if "ResponseId" in varnames else 7

    # index columns: (loop_num, qid) -> column index
    col_map: dict[tuple[int, str], int] = {}
    for i, v in enumerate(varnames):
        m = QID_RE.match(v)
        if m:
            col_map[(int(m.group(1)), m.group(2))] = i

    # index the per-participant intake columns (plain headers, answered once).
    # intake_idx maps output-field-name -> column index in the export.
    intake_idx: dict[str, int] = {}
    for header, out_name in INTAKE_COLUMNS.items():
        if header in varnames:
            intake_idx[out_name] = varnames.index(header)
    missing_intake = [h for h in INTAKE_COLUMNS if h not in varnames]
    if missing_intake:
        print(f"  NOTE: intake columns not found in export (will be blank): "
              f"{missing_intake}")
        print("        edit INTAKE_COLUMNS left-side keys to match your headers.")

    out_rows: list[dict] = []
    skipped: list[str] = []

    for row in data:
        rid = row[rid_idx] if rid_idx < len(row) else ""
        # find which qids this respondent has data in -> block signature
        present_qids = set()
        loopnums = set()
        for (ln, qid), ci in col_map.items():
            if ci < len(row) and row[ci].strip():
                present_qids.add(qid)
                loopnums.add(ln)
        if not present_qids:
            continue

        # match this respondent's qid set to a block signature
        version_num = None
        for sig, vnum in BLOCK_TO_VERSION.items():
            if set(sig).issubset(present_qids):
                version_num = vnum
                break
        if version_num is None:
            skipped.append(rid)
            continue

        trust_q, rel_q, cons_q = MEASURE_TRIPLES[version_num]
        vfile = versions[version_num]
        loops_sorted = sorted(loopnums)

        # read this respondent's intake values once (same for all their trials)
        intake_vals = {
            name: (row[ci].strip() if ci < len(row) else "")
            for name, ci in intake_idx.items()
        }

        # loop position (1..12) -> version row index (0..11), fixed order assumption
        for pos, ln in enumerate(loops_sorted):
            if pos >= len(vfile):
                break
            vrow = vfile[pos]
            def cell(qid):
                ci = col_map.get((ln, qid))
                return row[ci] if ci is not None and ci < len(row) else ""
            out_row = {
                "response_id": rid,
                "version": version_num,
                "trial_position": pos + 1,
                "loop_num": ln,
                "stem_id": vrow.get("stem_id", ""),
                "stakes": vrow.get("stakes", ""),
                "att_level": vrow.get("att_level", ""),
                "correctness": vrow.get("correctness", ""),
                "trust": cell(trust_q),
                "reliance": cell(rel_q),
                "consequence": cell(cons_q),
            }
            out_row.update(intake_vals)  # attach per-participant intake to every trial
            out_rows.append(out_row)

    out_path = Path(out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["response_id", "version", "trial_position", "loop_num",
                  "stem_id", "stakes", "att_level", "correctness",
                  "trust", "reliance", "consequence"] + list(INTAKE_COLUMNS.values())
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out_rows)

    n_resp = len({r["response_id"] for r in out_rows})
    print(f"Wrote {len(out_rows)} trial rows for {n_resp} respondents -> {out_path}")
    print(f"  (expected ~{n_resp*12} rows = {n_resp} respondents x 12 trials)")
    if skipped:
        print(f"  WARNING: {len(skipped)} respondents had an unrecognized block "
              f"signature and were skipped: {skipped}")
    print("\nVERIFY before trusting this:")
    print("  1. Confirm BLOCK_TO_VERSION matches how you assigned versions to blocks.")
    print("  2. Confirm loop order was FIXED (not randomized) when the pilot ran.")
    print("     If randomized, trial_position does NOT map to version row and this")
    print("     reconstruction is invalid.")
    print("  3. Spot-check a couple of rows against what you remember a participant saw.")


if __name__ == "__main__":
    here = Path(__file__).parent
    exp = Path(EXPORT_DIR) / EXPORT_FILE
    if not exp.is_absolute():
        exp = (here / EXPORT_DIR / EXPORT_FILE).resolve()
    out = Path(OUTPUT_DIR) / OUTPUT_CSV
    if not out.is_absolute():
        out = (here / OUTPUT_DIR / OUTPUT_CSV).resolve()
    # Anchor VERSION_DIR to the script location too (same as exp/out), so relative
    # paths like "../versions_output" resolve against the script, not the
    # working directory DataSpell happened to launch from.
    vdir = Path(VERSION_DIR)
    if not vdir.is_absolute():
        vdir = (here / VERSION_DIR).resolve()
    if not exp.exists():
        print(f"Export not found: {exp}")
        # list what IS in that folder so a filename mismatch is easy to spot
        parent = exp.parent
        if parent.exists():
            contents = sorted(p.name for p in parent.iterdir())
            print(f"Contents of {parent}:")
            for name in contents:
                print(f"    {name}")
            print("Set EXPORT_FILE to match the exact name above (including spaces,")
            print("month spelling, and date format -- Qualtrics names vary).")
        else:
            print(f"That folder does not exist: {parent}")
            print("Set EXPORT_DIR to the folder that actually holds your export.")
    elif not vdir.exists():
        print(f"Version dir not found: {vdir}")
        print("Set VERSION_DIR at the top to the folder holding version_1.csv .. version_6.csv.")
    else:
        reconstruct(exp, vdir, out)