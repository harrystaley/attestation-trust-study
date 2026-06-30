# Attestation Trust Study

Materials and analysis code for a cognitive-science experiment on source
attestation and trust calibration in AI-generated answers, conducted for
Georgia Tech CS 6795 (Introduction to Cognitive Science), Summer 2026.

This README covers the code and how to run it. **For the full experimental
design, hypotheses, theoretical framing, and analysis, see the project report.**

---

## Design at a glance

A 3 × 2 × 2 within-subjects factorial:

- **Attestation** (none / weak / strong) — the provenance display attached to an answer
- **Correctness** (correct / incorrect) — whether the answer is factually accurate
- **Stakes** (low / high) — how consequential it would be to act on a wrong answer

**Stakes, defined.** Stakes is operationalized as the overall consequentiality of
being wrong about the item:

- **high stakes:** An item where acting on the wrong answer causes a substantial, concrete negative consequence — a significant financial loss, legal penalty, or forfeited benefit or right — ideally one that is hard to reverse. The consequence may be financial, legal, or benefit-related. The fact must apply uniformly to all US adults at the federal level (not state-specific). This may also include significant health, safety, financial, or security consequence.
- **Low stakes:** An item of factual interest where acting on the wrong answer  produces no meaningful consequence: at most a trivial inconvenience or a  corrected misconception.

Stakes is treated holistically (bundling magnitude, domain, and relevance) rather
than isolating a single dimension; the per-trial Perceived Consequence measure is
used to validate the manipulation. See the project report for the full rationale.

Each participant sees 12 trials (one per cell). Counterbalancing uses a
six-version Latin square; trial order is randomized. Recruitment is via Prolific
(US residents, 18+) and approved social-media outreach; target N is determined by
the power-analysis notebook. Data collection is **in progress**: a 16-participant
pilot validated the pipeline, and main collection is underway.

(See the project report for hypotheses, measures, and full rationale.)

---

## Repository contents

### Survey construction
| File | Purpose |
|------|---------|
| `survey_generator.ipynb` | Generates and validates candidate survey stimuli via an LLM, then expands them into a Qualtrics loop table. |
| `generation_prompt.md` | The LLM prompt used to generate candidate stimuli (the study's authored instrument). |
| `make_qualtrics_block.py` | Emits paste-ready Qualtrics advanced-format text for the trial block (stimulus display + per-trial measures), with Loop & Merge piped fields pre-wired. |
| `latin_square_versions.py` | Splits the master loop table into the six counterbalanced version files (`version_1.csv` … `version_6.csv`), applying the cyclic Latin square independently to the low- and high-stakes pools. Each version is one participant's 12-trial set. |
| `AI_Attestation_Trust_Study.qsf` | The Qualtrics survey export (importable survey definition). |
| `output/` | Generated and curated stimuli, and the Qualtrics loop table. |
| `versions_output/` | The six counterbalanced version files (`version_1.csv` … `version_6.csv`), one loaded into each Qualtrics Trial block. |
| `survey/` | Participant-facing survey text: `consent_text.md`, `instruction_text.md`, `debrief_text.md`, `debrief_corrections.md/html`, and `qualtrics_block.txt` (the generated trial-block markup). |

### Analysis pipeline (`analysis_pipeline/`)
The data pipeline runs in numbered order; each script is path-safe and modular,
and reads the output of the previous step.

| File | Purpose |
|------|---------|
| `0-1_reconstruct_data.py` | Reconstructs per-trial condition codes (stem, attestation, correctness, stakes) from the Qualtrics export by block signature and loop position, and folds the per-participant intake/demographic columns (age, gender, education, AI use, AI expertise, baseline trust, consent) into the long-format output. |
| `0-2_prep_data.py` | Codes Qualtrics text labels to numeric: trust (1–7), reliance (1–3), consequence (1–5), and the analysis codings (`att_code` 0/1/2; `corr_code`, `stakes_code` ±0.5). Preserves all input columns, so intake data carries through. |
| `0-3_fit_pilot_model.py` | Fits the crossed random-effects model to coded data and prints fixed-effect and variance-component estimates as **candidate** inputs for the power simulation. Estimation only; does not interpret. |
| `attestation_trust_analysis.ipynb` | Main analysis notebook: descriptives, crossed mixed-effects models (participant + stem) for the three outcomes, the H4 interaction and stakes-moderation models, an H3 mediation scaffold, exploratory visualizations, and the intake/demographic figures. |
| `power_analysis_simulation.ipynb` | Monte-Carlo power analysis for the 3×2×2 mixed-effects design; determines target sample size. |
| `analysis_results.csv`, `power_results_detailed.csv` | Tidy model-estimate and power-curve outputs. |
| `images/` | Generated analysis figures (`fig1`–`fig8`, diagnostics). |

### Data (`prepped_data/`)
| File | Purpose |
|------|---------|
| `long_reconstructed.csv` / `long_coded.csv` | Current main dataset: reconstructed long format, then coded for analysis (one row per participant-trial, with intake columns). |
| `pilot_long_reconstructed.csv` / `pilot_long_coded.csv` | The 16-participant pilot dataset (pipeline validation; no intake columns). |

### Environment & meta
| File | Purpose |
|------|---------|
| `setup_env.py` | One-time bootstrap that creates a git-ignored `.env` for the OpenAI API key. |
| `environment.yaml` | Conda environment definition (Python 3.13; delegates Python deps to `requirements.txt`). |
| `requirements.txt` | Python package dependencies. |
| `NOTICE.md` | Copyright, license status, and AI-assistance disclosure. |
| `DESIGN_LOG.md` | Running record of design decisions and rationale (working document; not a deliverable). |

## Generated outputs

Running `survey_generator.ipynb` writes to `output/`:
- `generated_stems.json` / `.csv` — the 12 question stems with answers and sources
- `qualtrics_loop_table.csv` — the table for Qualtrics loop & merge import
- `versions_output/version_1.csv` … `version_6.csv` — the six counterbalanced version files produced by `latin_square_versions.py` (12 rows each); one is loaded into each of the six Trial blocks in Qualtrics
- `generation_metadata.json` — model, run date, and curation flags (for reproducibility)

---

## Setup

Requires Python 3.13+ and either conda or pip.

**Conda (recommended):**

```bash
conda env create -f environment.yaml
conda activate attestation-trust
```

**Pip:**

```bash
pip install -r requirements.txt
```

**API key (for stimulus generation only):**

```bash
python setup_env.py            # creates a .env template
# then edit .env and paste your OpenAI API key
```

The `.env` file is git-ignored and never committed. The stimulus generator
loads it automatically via `python-dotenv`.

---

## Usage

**Power analysis.** Open `power_analysis_simulation.ipynb`, set the assumed
effect sizes in the parameters block (ideally from pilot data), and run. Output
is a power curve indicating the sample size needed for the target power.

**Stimulus generation.** Open `survey_generator.ipynb` and run the cells in
order. It calls the OpenAI API to generate candidate stimuli, validates them
against the design constraints, flags items needing manual curation, and writes
a Qualtrics-ready loop table. Generated stimuli are curated by the author before
use.

**Survey build (Qualtrics).** The 72-row loop table is split into six
counterbalanced versions with `latin_square_versions.py` (set `INPUT_CSV` to the
loop table, run). The trial-block text is generated with `make_qualtrics_block.py`
and imported via Qualtrics advanced-format import. In Qualtrics, each version file
is loaded into one of six Trial blocks, and a Survey Flow Randomizer
("Evenly Present Elements," present 1 of 6) assigns each participant to one
version; loop order is randomized within the assigned version. Survey flow:
Consent (gate) → Instructions → Baseline Trust → Trial (one version) →
Demographics → Debrief → End.

**Analysis.** The data pipeline in `analysis_pipeline/` runs in numbered order:

```bash
python analysis_pipeline/0-1_reconstruct_data.py   # Qualtrics export -> long_reconstructed.csv (+ intake columns)
python analysis_pipeline/0-2_prep_data.py          # -> long_coded.csv (numeric codings)
python analysis_pipeline/0-3_fit_pilot_model.py    # candidate effect-size estimates for the power sim
```

Each script has an editable path block at the top (`INPUT_DIR` / `OUTPUT_DIR`)
and prints a validation report. Then open `attestation_trust_analysis.ipynb` and
run it against `long_coded.csv` for the full models, robustness checks, and
figures. Set `DATA_PATH` at the top of the notebook to the coded CSV.

---

## License and copyright

This repository is part of an ongoing research project intended for future
publication. **No open-source license is granted at this time** — all rights are
reserved by default, and licensing will be determined at publication. See
[`NOTICE.md`](NOTICE.md) for the full copyright, license-status, and
AI-assistance disclosure.

Human-subjects data, if collected, is governed separately by the study's IRB
protocol and participant consent.

---

## Author

Harry Staley — Georgia Institute of Technology, OMSCS
CS 6795 (Introduction to Cognitive Science), Summer 2026