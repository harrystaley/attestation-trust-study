"""Fit the mixed-effects model to the coded pilot data and report estimates.

AI assistance disclosure: this analysis-mechanics/plumbing utility was written
with the assistance of an AI assistant (Claude) and reviewed by the author. It
fits the specified mixed model and prints the estimated fixed effects and
variance components; it does NOT interpret results, choose which estimates to
trust, draw conclusions, or decide power-analysis inputs. Those are author-owned
judgments. This is tooling, not graded analytical content. Use of generative AI
follows the CS 6795 course policy.

PURPOSE
-------
This is "Step 1" of the power workflow. The Monte Carlo power simulation does NOT
read data; it generates synthetic data from assumed parameters. This script
estimates candidate values for those parameters by fitting the model to the
coded pilot data and printing:

  * fixed-effect coefficients (the BETA candidates), with std errors and p-values,
  * the participant random-intercept SD, and
  * the residual SD.

You then DECIDE -- with judgment, not mechanically -- which of these to carry
into the power simulation's BETA / SD_* block.

*** CRITICAL CAVEAT (read before using any number this prints) ***
This pilot is tiny (n=16). The estimates here -- ESPECIALLY the interaction
terms that drive your power (attestation:correctness, the three-way) -- are very
noisy and unreliable. Recommended use:
  - The residual SD and participant SD are the most stable; reasonable to use.
  - Main effects: rough sense only.
  - Interaction effect sizes: do NOT calibrate power to these noisy values.
    Set the interaction effect sizes you power for from a defensible
    smallest-effect-of-interest or the literature, not from 16 participants.
This script PRINTS estimates; it does not endorse using them. That judgment is
yours.

MODEL
-----
Mirrors the power simulation and the report's planned analysis:
    trust_num ~ att_code * corr_code * stakes_code
with a participant random intercept and an item (stem) variance component
(crossed random effects). att_code is 0/1/2 (linear trend); corr_code and
stakes_code are centered +/-0.5, matching prep_pilot_data.py and the sim.

REQUIRES
--------
statsmodels, pandas (your analysis environment). Not run in the build sandbox.
"""

from __future__ import annotations
from pathlib import Path

# ---- editor-run config ------------------------------------------------------
INPUT_DIR = "../prepped_data"
INPUT_FILE = "long_coded.csv"
OUTCOME = "trust_num"   # primary DV; set to "consequence_num" to inspect that scale
# ----------------------------------------------------------------------------


def fit_report(in_csv, outcome: str = OUTCOME) -> None:
    """Fit the crossed-random-effects model and print estimates.

    Args:
        in_csv: Path to the coded long-format pilot CSV (from prep_pilot_data.py).
        outcome: Numeric outcome column to model (default trust_num).

    Prints the fixed-effect table (coef, SE, p), the participant random-intercept
    SD, and the residual SD -- the candidate inputs for the power simulation.
    Does not return or interpret; the author decides what to use.
    """
    import pandas as pd
    import numpy as np
    import statsmodels.formula.api as smf

    df = pd.read_csv(in_csv)

    # Coerce the columns we model to numeric; drop rows missing any of them.
    needed = [outcome, "att_code", "corr_code", "stakes_code",
              "response_id", "stem_id"]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise KeyError(f"coded CSV missing columns: {missing}")

    for c in (outcome, "att_code", "corr_code", "stakes_code"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    before = len(df)
    df = df.dropna(subset=[outcome, "att_code", "corr_code", "stakes_code"])
    dropped = before - len(df)

    df["response_id"] = df["response_id"].astype("category")
    df["stem_id"] = df["stem_id"].astype("category")

    n_part = df["response_id"].nunique()
    n_item = df["stem_id"].nunique()
    print("=" * 70)
    print("PILOT MODEL FIT -- estimates as CANDIDATE power-sim inputs")
    print("=" * 70)
    print(f"Outcome: {outcome}")
    print(f"Rows used: {len(df)} (dropped {dropped} with missing values)")
    print(f"Participants: {n_part}   Items (stems): {n_item}")
    print(f"\n*** n={n_part} is a TINY pilot. Interaction estimates below are")
    print("    very noisy -- do NOT calibrate power to them. See header. ***\n")

    # Crossed random effects: participant random intercept + item variance comp.
    vc = {"stem": "0 + C(stem_id)"}
    model = smf.mixedlm(
        f"{outcome} ~ att_code * corr_code * stakes_code",
        data=df,
        groups=df["response_id"],
        vc_formula=vc,
        re_formula="1",
    )
    try:
        res = model.fit(reml=False, method="lbfgs", maxiter=500)
    except Exception as e:  # noqa: BLE001 -- report any convergence failure plainly
        print(f"MODEL DID NOT CONVERGE: {e}")
        print("With n=16 the crossed structure may not fit cleanly in statsmodels.")
        print("Consider a simpler random structure, or cross-check in R/lme4.")
        return

    print("-" * 70)
    print("FIXED EFFECTS (candidate BETA values):")
    print("-" * 70)
    summary = res.summary().tables[1]
    print(summary)

    # Pull out residual and participant SDs as power-sim SD candidates.
    try:
        resid_sd = float(np.sqrt(res.scale))
    except Exception:
        resid_sd = float("nan")
    # participant random-intercept variance is in cov_re (the 'groups' RE)
    try:
        part_var = float(res.cov_re.iloc[0, 0])
        part_sd = float(np.sqrt(part_var))
    except Exception:
        part_sd = float("nan")

    print("\n" + "-" * 70)
    print("VARIANCE COMPONENTS (candidate SD_* values for the power sim):")
    print("-" * 70)
    print(f"  participant random-intercept SD : {part_sd:.3f}  -> SD_PARTICIPANT")
    print(f"  residual SD                     : {resid_sd:.3f}  -> SD_RESIDUAL")
    print("  (item/stem SD is a variance component; if you need it explicitly,")
    print("   inspect res.vcomp. The participant and residual SDs are the most")
    print("   stable pilot quantities and the safest to reuse.)")

    print("\n" + "=" * 70)
    print("HOW TO USE THIS (author judgment required):")
    print("=" * 70)
    print("""
- The fixed-effect coefficients above are in the SAME coding as the power sim
  (att 0/1/2, corr/stakes +/-0.5), so a coefficient maps directly to the matching
  BETA key (e.g. the att_code:corr_code estimate -> BETA['att_x_corr']).
- BUT with n=16 the interaction estimates are noisy. Recommended:
    * Reuse SD_PARTICIPANT and SD_RESIDUAL from above (most stable).
    * For the interaction effect sizes you POWER for (att_x_corr, three_way),
      use a defensible smallest-effect-of-interest or literature value, not the
      noisy pilot number.
- Then put your chosen values into the power sim's BETA / SD_* block and run it
  to get N. The choice of which numbers to trust is YOURS.
""")


if __name__ == "__main__":
    here = Path(__file__).parent
    inp = Path(INPUT_DIR) / INPUT_FILE
    if not inp.is_absolute():
        inp = here / INPUT_DIR / INPUT_FILE
    if not inp.exists():
        print(f"Input not found: {inp}")
        print("Run prep_pilot_data.py first to produce the coded CSV.")
    else:
        fit_report(inp)