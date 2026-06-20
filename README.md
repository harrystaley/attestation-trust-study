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

- **Low stakes** — questions of factual curiosity, where acting on a wrong answer
  has little or no practical consequence (e.g., the length of a day on Mars, the
  year a painting was made).
- **High stakes** — questions where being wrong carries a real practical
  consequence, for example a financial, legal, health, safety, or security
  consequence (e.g., a deposit-insurance limit, a recommended ladder setup ratio).

Stakes is treated holistically (bundling magnitude, domain, and relevance) rather
than isolating a single dimension; the per-trial Perceived Consequence measure is
used to validate the manipulation. See the project report for the full rationale.

Each participant sees 12 trials (one per cell). Counterbalancing uses a
six-version Latin square; trial order is randomized. Recruitment is planned via
Prolific; target N is determined by the power-analysis notebook.

(See the project report for hypotheses, measures, and full rationale.)

---

## Repository contents

| File | Purpose |
|------|---------|
| `survey_generator.ipynb` | Generates and validates candidate survey stimuli via an LLM, then expands them into a Qualtrics loop table. |
| `power_analysis_simulation.ipynb` | Monte-Carlo power analysis for the 3×2×2 mixed-effects design; determines target sample size. |
| `analysis.ipynb` | Analysis of collected data (mixed-effects models). *Pending data collection.* |
| `setup_env.py` | One-time bootstrap that creates a git-ignored `.env` for the OpenAI API key. |
| `environment.yaml` | Conda environment definition (delegates Python deps to `requirements.txt`). |
| `requirements.txt` | Python package dependencies. |
| `NOTICE.md` | Copyright, license status, and AI-assistance disclosure. |
| `generation_prompt.md` | The LLM prompt used to generate candidate stimuli (the study's authored instrument). |
| `output/` | Generated and curated stimuli, and the Qualtrics loop table. |

## Generated outputs

Running `survey_generator.ipynb` writes to `output/`:
- `generated_stems.json` / `.csv` — the 12 question stems with answers and sources
- `qualtrics_loop_table.csv` — the 72-row table for Qualtrics loop & merge import
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

**Analysis.** `analysis.ipynb` fits the mixed-effects models to collected data.
*Pending data collection.*

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