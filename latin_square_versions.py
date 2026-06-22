"""Generate the 6 counterbalanced version CSVs for the within-subjects design.

AI assistance disclosure: this counterbalancing/plumbing utility was written with
the assistance of an AI assistant (Claude) and reviewed by the author. It applies
a cyclic Latin square over stem INDICES and condition CODES; it does not inspect,
judge, or author any stimulus content. The stimulus rows themselves are the
author's research materials. This is tooling, not graded analytical content. Use
of generative AI follows the CS 6795 course policy.

What it does
------------
Implements the report's counterbalancing: within each stakes pool, the six stems
are crossed with the six attestation x correctness conditions across six survey
versions, by the rule

    version v, stem i  ->  condition (i + v) mod 6

This guarantees (verified in tests below):
  * each version presents all six conditions exactly once,
  * each stem appears in every condition exactly once across the six versions,
  * each condition appears exactly six times across all 36 (version x stem) cells.

The same rule is applied independently to the low-stakes pool and the high-stakes
pool, so each generated version_N.csv contains 12 rows (6 low + 6 high), one per
design cell, for a participant assigned to version N.

INPUT CONTRACT (item-agnostic)
------------------------------
A "long" stem CSV where, for each stem, all six attestation x correctness rows
are present, with at least these columns:
    stem_id, stakes, question_text, answer_text, att_level, correctness,
    attestation_text   (and optionally attestation_qualtrics)
`stakes` must be 'low' or 'high'. Within each stakes pool there must be exactly
6 distinct stem_ids, each with all 6 (att_level x correctness) rows present.

This script does NOT create stimulus content; it only SELECTS, per version, which
existing row represents each stem, according to the Latin square. Supplying the
stem CSV and running it on real data is the author's step.
"""

from __future__ import annotations
from pathlib import Path
import csv
from collections import defaultdict

# Canonical ordering of the 6 attestation x correctness conditions, indices 0..5.
# This order must be stable so the (i+v) mod 6 mapping is reproducible.
CONDITIONS = [
    ("none", "correct"),
    ("none", "incorrect"),
    ("weak", "correct"),
    ("weak", "incorrect"),
    ("strong", "correct"),
    ("strong", "incorrect"),
]
COND_INDEX = {pair: idx for idx, pair in enumerate(CONDITIONS)}
N = 6  # stems per pool, conditions, and versions


def _load_rows(in_csv: Path) -> list[dict]:
    with in_csv.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _index_rows(rows: list[dict]) -> dict:
    """Index rows by (stakes, stem_id, (att_level, correctness)) -> row.

    Validates that each stakes pool has exactly 6 stems, each with all 6
    condition rows. Raises on any structural problem so a malformed stem set
    fails loudly rather than producing a silently-wrong counterbalance.
    """
    table: dict = defaultdict(dict)
    stems_by_pool: dict = defaultdict(set)
    for r in rows:
        stakes = r["stakes"].strip().lower()
        stem = r["stem_id"].strip()
        cond = (r["att_level"].strip().lower(), r["correctness"].strip().lower())
        if cond not in COND_INDEX:
            raise ValueError(f"unknown condition {cond} for stem {stem}")
        table[(stakes, stem)][cond] = r
        stems_by_pool[stakes].add(stem)

    for pool in ("low", "high"):
        stems = sorted(stems_by_pool.get(pool, []))
        if len(stems) != N:
            raise ValueError(
                f"{pool}-stakes pool has {len(stems)} stems; expected {N}: {stems}"
            )
        for stem in stems:
            present = set(table[(pool, stem)].keys())
            missing = set(COND_INDEX) - present
            if missing:
                raise ValueError(
                    f"stem {stem} ({pool}) missing condition rows: {sorted(missing)}"
                )
    return table


def _pool_stem_order(rows: list[dict], pool: str) -> list[str]:
    """Deterministic stem ordering within a pool: by first appearance in the CSV.

    Stem i in the Latin square is the i-th stem in this order. Using file order
    (not sorted) lets the author control which stem is index 0..5 by arranging
    the CSV; documented so the mapping is reproducible.
    """
    seen: list[str] = []
    for r in rows:
        if r["stakes"].strip().lower() == pool:
            s = r["stem_id"].strip()
            if s not in seen:
                seen.append(s)
    return seen


def build_versions(in_csv: str | Path, out_dir: str | Path) -> list[Path]:
    """Emit version_1.csv ... version_6.csv into out_dir. Returns the paths."""
    in_path, out_path = Path(in_csv), Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rows = _load_rows(in_path)
    table = _index_rows(rows)
    fieldnames = list(rows[0].keys())
    if "version" not in fieldnames:
        fieldnames = ["version"] + fieldnames

    order = {pool: _pool_stem_order(rows, pool) for pool in ("low", "high")}
    written: list[Path] = []

    for v in range(N):  # versions 0..5 -> files version_1..6
        out_rows: list[dict] = []
        for pool in ("low", "high"):
            for i, stem in enumerate(order[pool]):
                cond_idx = (i + v) % N
                cond = CONDITIONS[cond_idx]
                row = dict(table[(pool, stem)][cond])
                row["version"] = v + 1
                out_rows.append(row)
        vpath = out_path / f"version_{v + 1}.csv"
        with vpath.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(out_rows)
        written.append(vpath)
    return written


# ---- self-test on a synthetic (content-free) stem set -----------------------
def _self_test() -> None:
    """Verify counterbalance properties on placeholder data (no real stimuli)."""
    import io
    synthetic: list[dict] = []
    for pool in ("low", "high"):
        for stem_i in range(N):
            for (att, corr) in CONDITIONS:
                synthetic.append({
                    "stem_id": f"{pool}{stem_i}",
                    "stakes": pool,
                    "question_text": f"Q-{pool}{stem_i}",
                    "answer_text": f"A-{pool}{stem_i}-{att}-{corr}",
                    "att_level": att,
                    "correctness": corr,
                    "attestation_text": "",
                })
    tmp = Path("/tmp/_lsq_selftest")
    tmp.mkdir(exist_ok=True)
    src = tmp / "stems.csv"
    with src.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(synthetic[0].keys()))
        w.writeheader(); w.writerows(synthetic)

    paths = build_versions(src, tmp / "versions")
    assert len(paths) == N

    # Every version: 12 rows, all 6 conditions present once per pool.
    for p in paths:
        with p.open(newline="", encoding="utf-8") as f:
            vr = list(csv.DictReader(f))
        assert len(vr) == 2 * N, f"{p.name}: expected 12 rows, got {len(vr)}"
        for pool in ("low", "high"):
            conds = sorted(
                COND_INDEX[(r["att_level"], r["correctness"])]
                for r in vr if r["stakes"] == pool
            )
            assert conds == list(range(N)), f"{p.name} {pool}: conditions not complete"

    # Each stem across the 6 versions sees all 6 conditions exactly once.
    seen = defaultdict(list)
    for p in paths:
        with p.open(newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                key = (r["stakes"], r["stem_id"])
                seen[key].append(COND_INDEX[(r["att_level"], r["correctness"])])
    for key, conds in seen.items():
        assert sorted(conds) == list(range(N)), f"{key}: stem doesn't cover all conditions"

    print("SELF-TEST PASSED: 6 versions, 12 rows each, fully balanced counterbalance.")


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3:
        out = build_versions(sys.argv[1], sys.argv[2])
        print(f"Wrote {len(out)} version files:")
        for p in out:
            print(f"  {p}")
        print("\nEach version_N.csv has 12 rows (6 low + 6 high), one per design cell.")
        print("Assign participants evenly across the 6 versions via a Survey Flow Randomizer.")
    else:
        print("Usage: python latin_square_versions.py <stems.csv> <out_dir>")
        print("Running self-test on synthetic data instead...\n")
        _self_test()∂