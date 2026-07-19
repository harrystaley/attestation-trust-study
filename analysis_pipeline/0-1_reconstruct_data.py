"""Reconstruct per-trial condition codes for the Qualtrics export.

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
(Qualtrics Loop & Merge Looping='Static' in the exported QSF), loop POSITION
i (1..12) corresponds to ROW i of that block's version file. So:

    respondent -> block signature -> version file -> row i -> condition codes

*** ASSUMPTION: loop order was NOT randomized at collection. ***
Verified in the exported QSF: all six Trial blocks show Looping="Static" and
RandomizeQuestions="false". Under Static looping this positional mapping is
valid. (0-1b_clean_data.py additionally re-attaches condition codes directly
from the QSF LoopingOptions.Static table, so the codes this script writes are
subsequently overwritten from the authoritative survey definition; this script's
output is still needed for the trial responses and loop_num keys.)

WHAT YOU MUST SUPPLY
--------------------
BLOCK_TO_VERSION below maps each block's question-ID signature to the version
file number you loaded into that block. The default assumes Trial blocks were
built in order (block 1 <- version_1 ... block 6 <- version_6), inferred from the
loop-number ordering. CONFIRM THIS against how you actually assigned versions to
blocks; a wrong mapping silently mislabels every condition. (Note: if the codes
are overwritten downstream by 0-1b from the QSF, that step corrects a wrong
mapping here for stem/stakes/att/correctness -- but keep this correct anyway so
the intermediate file is self-consistent.)

OUTPUT
------
A long-format CSV: one row per participant-trial, with columns
    response_id, version, trial_position, loop_num, stem_id, stakes, att_level,
    correctness, trust, reliance, consequence,
    age, gender, education, ai_frequency, ai_expertise, baseline_trust, consent
suitable for the cleaning stage (0-1b) and the mixed-effects analysis.
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

EXPORT_DIR = "../qdata"
EXPORT_FILE = "AI_Attestation_Trust_Study_07-18-2026T0304.zip"  # PINNED wave. To use a newer export, change this filename (same in 0-1 and 0-1b).
VERSION_DIR = "../versions_output"   # folder holding version_1.csv .. version_6.csv
OUTPUT_DIR = "../prepped_data"
OUTPUT_CSV = "long_reconstructed.csv"

# Map each block's question-ID signature -> version file number.
# DEFAULT inferred from loop-number order (block creation order). CONFIRM!
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
# plain Qualtrics columns named by their DataExportTag. Each is attached to every
# trial row for that respondent, keyed on ResponseId.
# LEFT = the export column header; RIGHT = the output column name.
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

    Returns:
        A tuple ``(csv_path, tmpdir)``. ``tmpdir`` is a TemporaryDirectory that
        must be kept alive while the CSV is read; it is ``None`` when the input
        was already a CSV.

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
    print("  2. Loop order was FIXED (QSF Looping='Static') -- confirmed for this survey.")
    print("  3. Spot-check a couple of rows against what you remember a participant saw.")
    print("  4. Next run 0-1b_clean_data.py (applies exclusions + re-attaches QSF codes),")
    print("     then 0-2_prep_data.py on the cleaned file.")


if __name__ == "__main__":
    here = Path(__file__).parent
    if EXPORT_FILE is None:
        # Auto-select the newest export by the MM-DD-YYYYThhmm stamp in its name
        # (so 0-1 and 0-1b read the same wave). Sort key reorders to YYYYMMDDhhmm.
        import glob, re
        edir = (here / EXPORT_DIR).resolve() if not Path(EXPORT_DIR).is_absolute() else Path(EXPORT_DIR)
        def _stamp(f):
            m = re.search(r"(\d{2})-(\d{2})-(\d{4})T(\d{4})", Path(f).name)
            mm, dd, yyyy, hhmm = m.groups()
            return yyyy + mm + dd + hhmm
        matches = glob.glob(f"{edir}/AI_Attestation_Trust_Study_*.zip") + \
                  glob.glob(f"{edir}/AI_Attestation_Trust_Study_*.csv")
        if not matches:
            print(f"Cannot run: no timestamped export found in {edir}")
            raise SystemExit(1)
        exp = Path(max(matches, key=_stamp))
        print(f"Auto-selected latest export: {exp.name}")
    else:
        exp = Path(EXPORT_DIR) / EXPORT_FILE
        if not exp.is_absolute():
            exp = (here / EXPORT_DIR / EXPORT_FILE).resolve()
    out = Path(OUTPUT_DIR) / OUTPUT_CSV
    if not out.is_absolute():
        out = (here / OUTPUT_DIR / OUTPUT_CSV).resolve()
    vdir = Path(VERSION_DIR)
    if not vdir.is_absolute():
        vdir = (here / VERSION_DIR).resolve()
    if not exp.exists():
        print(f"Export not found: {exp}")
        parent = exp.parent
        if parent.exists():
            contents = sorted(p.name for p in parent.iterdir())
            print(f"Contents of {parent}:")
            for name in contents:
                print(f"    {name}")
            print("Set EXPORT_FILE to match the exact name above.")
        else:
            print(f"That folder does not exist: {parent}")
            print("Set EXPORT_DIR to the folder that actually holds your export.")
    elif not vdir.exists():
        print(f"Version dir not found: {vdir}")
        print("Set VERSION_DIR to the folder holding version_1.csv .. version_6.csv.")
    else:
        reconstruct(exp, vdir, out)