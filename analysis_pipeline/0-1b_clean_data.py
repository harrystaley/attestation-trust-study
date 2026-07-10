"""Apply participant- and trial-level exclusions to the long-format study data.

AI assistance disclosure: this data-cleaning/plumbing utility was written with
the assistance of an AI assistant (Claude) and reviewed by the author. It applies
the author's pre-specified exclusion rules and attaches ground-truth condition
codes read directly from the survey's QSF definition. It does not fit models,
interpret results, or author any analytical conclusions. This is tooling, not
graded analytical content. Use of generative AI follows the CS 6795 course policy.

WHERE THIS SITS IN THE PIPELINE
-------------------------------
    0-1_reconstruct_data.py  ->  [THIS: 0-1b_clean_data.py]  ->  0-2_prep_data.py
                                         |
                                         +-- reads condition codes from the QSF
                                             (LoopingOptions.Static), which is the
                                             authoritative survey definition, rather
                                             than inferring them by loop position.

WHY CODES COME FROM THE QSF
---------------------------
The survey's six Trial blocks use Qualtrics *Static* looping (Looping="Static",
RandomizeQuestions="false"), verified in the exported QSF. Each Static loop row
carries its own condition fields:

    field 1 = version      field 5 = answer text
    field 2 = stem_id      field 6 = att_level   (none/weak/strong)
    field 3 = stakes       field 7 = correctness (correct/incorrect)
    field 4 = question     field 8 = attestation text

So (version, loop_num) -> {stem_id, stakes, att_level, correctness} is defined
exactly by the QSF. This module builds that table from the QSF and can attach it
to the response rows, removing any dependence on version-file row order.

EXCLUSION RULES (exactly as specified by the author; each toggleable below)
---------------------------------------------------------------------------
Participant-level (drop the whole respondent):
  R1 CONSENT      : drop if consent != "Agree".
  R2 DUPLICATE    : drop rows flagged Q_DuplicateRespondent == "true"
                    (Qualtrics RelevantID; keeps whichever response Qualtrics
                    retained -- the export carries no group key to compare
                    completeness within a duplicate set).
  R3 BALLOT       : drop rows flagged Q_BallotBoxStuffing.
  R4 SPEED        : drop if Duration (in seconds) < 10.
Trial-level (drop the single trial row, not the respondent):
  R5 BLANK_TRIAL  : drop a trial row where trust AND reliance AND consequence
                    are all blank (an unseen/unanswered loop iteration).

NOT applied (by author's decision):
  - Q_PrivateBrowserDetected is NOT an exclusion criterion.
  - No strict Finished==True filter: a response that clears R1-R5 and still has
    >=1 non-blank trial is retained even if Qualtrics marked Finished=False.
    (Set REQUIRE_FINISHED=True to change this.)

Each rule prints how many rows/trials it removed so the numbers are auditable and
can be reported in the methods section.

INPUT
-----
The long-format CSV from 0-1_reconstruct_data.py, plus the raw Qualtrics export
(for the participant-level flags: consent, duplicate, ballot, duration) and the
QSF (for condition codes). The long file is keyed to the export by response_id.

OUTPUT
------
A cleaned long-format CSV with the same columns as the input, with condition
codes (stem_id/stakes/att_level/correctness) overwritten from the QSF table, and
excluded rows/trials removed. Feed this straight into 0-2_prep_data.py.
"""

from __future__ import annotations
from pathlib import Path
import csv
import json
import re
import zipfile
import tempfile

# ---- editor-run config ------------------------------------------------------
LONG_DIR = "../prepped_data"
LONG_FILE = "long_reconstructed.csv"          # output of 0-1_reconstruct_data.py

EXPORT_DIR = "../qdata"
# EXPORT_FILE: set to a specific filename to pin a wave (reproducibility), or
# leave as None to auto-select the LATEST timestamped export in EXPORT_DIR.
# Auto-selection keeps 0-1 and 0-1b on the same wave (identical inline logic).
EXPORT_FILE = None  # e.g. "AI_Attestation_Trust_Study_07-10-2026T1807.zip" to pin

QSF_DIR = "../survey"   # sibling of analytics_pipeline/ (holds the .qsf)
QSF_FILE = "AI_Attestation_Trust_Study.qsf"   # survey definition (condition codes)

OUTPUT_DIR = "../prepped_data"
OUTPUT_FILE = "long_cleaned.csv"

# Rule toggles (all True = apply every specified exclusion).
APPLY_CONSENT     = True   # R1
APPLY_DUPLICATE   = True   # R2
APPLY_BALLOT      = True   # R3
APPLY_SPEED       = True   # R4
APPLY_BLANK_TRIAL = True   # R5
REQUIRE_FINISHED  = False  # author's decision: keep fully-answered non-finished

SPEED_FLOOR_SECONDS = 10   # R4 threshold: drop duration < this
CONSENT_ACCEPT = "agree"   # R1: keep only consent whose text starts with this

# Raw-export column headers used for participant-level flags. Edit LEFT side if
# your export headers differ.
COL_RESPONSE_ID = "ResponseId"
COL_CONSENT     = "Consent"
COL_DUPLICATE   = "Q_DuplicateRespondent"
COL_BALLOT      = "Q_BallotBoxStuffing"
COL_DURATION    = "Duration (in seconds)"
COL_FINISHED    = "Finished"
# ----------------------------------------------------------------------------


def resolve_export_csv(export_path: str | Path) -> tuple[Path, tempfile.TemporaryDirectory | None]:
    """Return a path to the response CSV, extracting from a .zip if needed.

    Accepts either a Qualtrics ``.zip`` export or the ``.csv`` directly. For a
    zip, extracts to a temporary directory (kept alive by the returned handle)
    and locates the single CSV inside by extension.

    Returns:
        ``(csv_path, tmpdir)``; ``tmpdir`` is ``None`` when the input was a CSV
        and otherwise must be kept alive while the CSV is read.

    Raises:
        FileNotFoundError: if the path does not exist.
        ValueError: if a zip contains zero or multiple CSVs, or the suffix is
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
                raise ValueError(f"expected one CSV in zip, found {len(csv_names)}: {csv_names}")
            zf.extract(csv_names[0], tmp.name)
        return Path(tmp.name) / csv_names[0], tmp
    raise ValueError(f"export must be .zip or .csv, got: {p.suffix!r}")


def build_qsf_code_table(qsf_path: str | Path) -> dict[tuple[str, int], dict]:
    """Read ground-truth condition codes from the QSF Static loop definitions.

    Parses each Trial block's ``Options.LoopingOptions.Static`` mapping. Each loop
    row is a field dict whose positions are fixed (1=version, 2=stem_id,
    3=stakes, 6=att_level, 7=correctness). The function verifies that looping is
    Static (not randomized) for every trial block and raises if any block is not,
    since the position->code mapping is only valid under Static looping.

    Returns:
        ``{(version, loop_num): {"stem_id","stakes","att_level","correctness"}}``
        with ``version`` a string and ``loop_num`` an int.

    Raises:
        ValueError: if a trial block uses non-Static looping, or a field dict is
            missing an expected position.
    """
    q = json.loads(Path(qsf_path).read_text(encoding="utf-8"))
    table: dict[tuple[str, int], dict] = {}
    non_static: list[str] = []
    for e in q.get("SurveyElements", []):
        if e.get("Element") != "BL":
            continue
        payload = e.get("Payload")
        blocks = payload.values() if isinstance(payload, dict) else payload
        for b in blocks:
            if not isinstance(b, dict):
                continue
            desc = str(b.get("Description", ""))
            if not desc.lower().startswith("trial"):
                continue
            opts = b.get("Options", {}) or {}
            if opts.get("Looping") != "Static":
                non_static.append(f"{desc} (Looping={opts.get('Looping')!r})")
                continue
            static = (opts.get("LoopingOptions", {}) or {}).get("Static", {}) or {}
            for loopnum, fields in static.items():
                try:
                    version = fields["1"]
                    codes = {
                        "stem_id": fields["2"],
                        "stakes": fields["3"],
                        "att_level": fields["6"],
                        "correctness": fields["7"],
                    }
                except KeyError as ke:
                    raise ValueError(
                        f"{desc} loop {loopnum}: missing field {ke} in QSF"
                    ) from ke
                table[(version, int(loopnum))] = codes
    if non_static:
        raise ValueError(
            "QSF has non-Static trial blocks; position->code mapping is invalid "
            "for: " + "; ".join(non_static)
        )
    if not table:
        raise ValueError("no Static trial loops found in QSF")
    return table


def load_participant_flags(export_csv: str | Path) -> dict[str, dict]:
    """Return per-respondent flag values keyed by response_id.

    Reads the raw Qualtrics export (3 header rows) and pulls the participant-level
    columns used by the exclusion rules: consent, duplicate, ballot, duration,
    finished. Missing columns yield empty strings (the corresponding rule then
    excludes nobody, and a note is printed by the caller).

    Returns:
        ``{response_id: {"consent","duplicate","ballot","duration","finished"}}``.
    """
    resolved, tmp = resolve_export_csv(export_csv)
    try:
        rows = list(csv.reader(open(resolved, encoding="utf-8")))
    finally:
        if tmp is not None:
            tmp.cleanup()
    hdr = rows[0]
    data = rows[3:]
    idx = {name: i for i, name in enumerate(hdr)}

    def get(row, col):
        i = idx.get(col)
        return row[i].strip() if (i is not None and i < len(row)) else ""

    rid_col = COL_RESPONSE_ID if COL_RESPONSE_ID in idx else None
    flags: dict[str, dict] = {}
    for row in data:
        rid = get(row, rid_col) if rid_col else ""
        if not rid:
            continue
        flags[rid] = {
            "consent": get(row, COL_CONSENT),
            "duplicate": get(row, COL_DUPLICATE),
            "ballot": get(row, COL_BALLOT),
            "duration": get(row, COL_DURATION),
            "finished": get(row, COL_FINISHED),
        }
    missing = [c for c in (COL_CONSENT, COL_DUPLICATE, COL_BALLOT, COL_DURATION,
                           COL_FINISHED) if c not in idx]
    if missing:
        print(f"  NOTE: export missing flag columns (their rule excludes nobody): {missing}")
    return flags


def _is_blank(v) -> bool:
    return v is None or str(v).strip() == ""


def clean(long_csv: str | Path, export_csv: str | Path, qsf_path: str | Path,
          out_csv: str | Path) -> None:
    """Apply exclusions and attach QSF condition codes; write the cleaned file.

    Order of operations:
      1. Attach ground-truth condition codes from the QSF by (version, loop_num).
      2. Apply participant-level rules R1-R4 (drop whole respondents).
      3. Apply trial-level rule R5 (drop all-blank trial rows).
      4. Optionally require Finished==True (off by default).
      5. Drop any respondent left with zero trials.

    Prints a per-rule exclusion count (respondents and trials) for the methods
    section, then writes the cleaned long CSV with the same columns as the input.

    Raises:
        KeyError: if the long file lacks response_id / version / loop_num.
    """
    code_table = build_qsf_code_table(qsf_path)
    flags = load_participant_flags(export_csv)

    with Path(long_csv).open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        for req in ("response_id", "version", "loop_num"):
            if req not in fieldnames:
                raise KeyError(f"long file missing required column: {req!r}")
        rows = list(reader)

    n_rows_in = len(rows)
    resp_in = {r["response_id"] for r in rows}

    # --- step 1: attach authoritative condition codes from the QSF ----------
    code_miss = 0
    for r in rows:
        key = (str(r.get("version", "")).strip(), _safe_int(r.get("loop_num")))
        codes = code_table.get(key)
        if codes is None:
            code_miss += 1
            continue
        r["stem_id"] = codes["stem_id"]
        r["stakes"] = codes["stakes"]
        r["att_level"] = codes["att_level"]
        r["correctness"] = codes["correctness"]
    if code_miss:
        print(f"  NOTE: {code_miss} trial rows had no matching QSF (version,loop) "
              f"key; their codes were left as-is.")

    # --- step 2: participant-level exclusions (R1-R4) -----------------------
    drop_resp: dict[str, str] = {}   # response_id -> first rule that dropped it
    for rid in resp_in:
        fl = flags.get(rid, {})
        if APPLY_CONSENT and fl.get("consent", "").strip().lower() != CONSENT_ACCEPT:
            # treat missing/blank consent as failing the accept condition
            if fl.get("consent", "").strip().lower() != CONSENT_ACCEPT:
                drop_resp.setdefault(rid, "R1_consent")
        if APPLY_DUPLICATE and fl.get("duplicate", "").strip().lower() == "true":
            drop_resp.setdefault(rid, "R2_duplicate")
        if APPLY_BALLOT and fl.get("ballot", "").strip() not in ("", ):
            # any non-empty ballot-stuffing flag = drop
            drop_resp.setdefault(rid, "R3_ballot")
        if APPLY_SPEED:
            dur = _safe_float(fl.get("duration"))
            if dur is not None and dur < SPEED_FLOOR_SECONDS:
                drop_resp.setdefault(rid, "R4_speed")
        if REQUIRE_FINISHED and fl.get("finished", "").strip().lower() != "true":
            drop_resp.setdefault(rid, "R0_not_finished")

    # per-rule respondent counts
    from collections import Counter
    rule_counts = Counter(drop_resp.values())

    kept_rows = [r for r in rows if r["response_id"] not in drop_resp]

    # --- step 3: trial-level exclusion (R5) ---------------------------------
    n_blank_trials = 0
    final_rows = []
    for r in kept_rows:
        if APPLY_BLANK_TRIAL and _is_blank(r.get("trust")) and \
           _is_blank(r.get("reliance")) and _is_blank(r.get("consequence")):
            n_blank_trials += 1
            continue
        final_rows.append(r)

    # --- step 4: drop respondents left with zero trials ---------------------
    from collections import defaultdict
    per_resp = defaultdict(int)
    for r in final_rows:
        per_resp[r["response_id"]] += 1
    empty_resp = {rid for rid in {r["response_id"] for r in kept_rows}
                  if per_resp[rid] == 0}
    if empty_resp:
        final_rows = [r for r in final_rows if r["response_id"] not in empty_resp]

    # --- write --------------------------------------------------------------
    out_path = Path(out_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(final_rows)

    # --- report -------------------------------------------------------------
    resp_out = {r["response_id"] for r in final_rows}
    print(f"\nCleaned {n_rows_in} -> {len(final_rows)} trial rows -> {out_path}")
    print(f"  respondents: {len(resp_in)} -> {len(resp_out)}")
    print("  participant-level exclusions (respondents dropped):")
    for rule in ("R1_consent", "R2_duplicate", "R3_ballot", "R4_speed",
                 "R0_not_finished"):
        if rule_counts.get(rule):
            print(f"    {rule:16s}: {rule_counts[rule]}")
    if not rule_counts:
        print("    (none)")
    print(f"  trial-level exclusions:")
    print(f"    R5_blank_trial  : {n_blank_trials} trial rows dropped")
    if empty_resp:
        print(f"    respondents left with 0 trials after R5: {len(empty_resp)}")
    print("\nNOTE: Q_PrivateBrowserDetected was NOT used as an exclusion.")
    if not REQUIRE_FINISHED:
        print("      Finished==False responses retained when they pass R1-R5.")


def _safe_int(v):
    try:
        return int(str(v).strip())
    except (TypeError, ValueError):
        return None


def _safe_float(v):
    try:
        return float(str(v).strip())
    except (TypeError, ValueError):
        return None


if __name__ == "__main__":
    here = Path(__file__).parent

    def resolve(d, fn):
        p = Path(d) / fn
        return p if p.is_absolute() else (here / d / fn).resolve()

    long_csv = resolve(LONG_DIR, LONG_FILE)
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
        export = Path(max(matches, key=_stamp))
        print(f"Auto-selected latest export: {export.name}")
    else:
        export = resolve(EXPORT_DIR, EXPORT_FILE)
    qsf = resolve(QSF_DIR, QSF_FILE)
    out = resolve(OUTPUT_DIR, OUTPUT_FILE)

    problems = []
    if not long_csv.exists():
        problems.append(f"long file not found: {long_csv}\n  (run 0-1_reconstruct_data.py first)")
    if not export.exists():
        problems.append(f"export not found: {export}")
    if not qsf.exists():
        problems.append(f"QSF not found: {qsf}")
    if problems:
        print("Cannot run:")
        for p in problems:
            print("  - " + p)
    else:
        clean(long_csv, export, qsf, out)