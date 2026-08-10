# Attestation Trust Study

A user-facing empirical study measuring how people calibrate trust in LLM-generated answers under different levels of source attestation (none/weak/strong) and decision stakes (low/high consequence). Part of **CS 6795** (Summer 2026, Georgia Tech).

## Overview

This study tests whether and how source attestation affects trust and behavioral reliance on LLM responses. The design crosses three attestation levels (none, weak, strong) with two stakes conditions (low-consequence facts, high-stakes federal decisions), using a within-subjects Latin square with 12 trials per participant. We measure:

- **State trust** (1–7 point scale, fully labeled)
- **Behavioral reliance** (reject / verify / act)
- **Perceived consequence** (mediator for stakes effect)

Key hypotheses:
- **H1:** Attestation strength increases trust.
- **H2:** Attestation strength increases reliance.
- **H3:** Stakes increase reliance (boundary conditions).
- **H4:** Perceived consequence mediates the stakes effect.

## Repository Structure

```
survey/                       Qualtrics instrument and consent/debrief
├── AI_Attestation_Trust_Study.qsf      Live survey (6-version counterbalanced)
├── consent_text.md, debrief_text.md    Ethics & disclosure
├── debrief_corrections.html            Corrections for false answers shown
└── *_versions/                         Stimulus sets (per Latin square version)

analysis_pipeline/            Data handling and statistical modeling
├── 0-1_reconstruct_data.py   Parse raw Qualtrics CSV export
├── 0-1b_clean_data.py        Attention checks, bot detection, exclusions
├── 0-2_prep_data.py          Reshape to long format for analysis
├── attestation_trust_analysis.ipynb    Mixed-effects modeling (LMM)
├── power_analysis_simulation.ipynb     Sample-size planning
└── analysis_results.csv, power_results_detailed.csv

prepped_data/                 Cleaned/reshaped CSVs (intermediate outputs)
output/                       Figures and results summaries

survey_generator.ipynb        LLM-based stimulus generation & curation
latin_square_versions.py      6-version counterbalancing (3 attestation × 2 stakes × 2 correctness)
make_qualtrics_block.py       Convert stimulus CSV to Qualtrics block format

DESIGN_LOG.md                 Decision record: rationale for all design choices
generation_prompt.md          LLM instruction template for stimulus generation
environment.yaml, requirements.txt    Conda & pip dependencies
```

## Design Highlights

- **Stimuli:** LLM-generated (OpenAI API), author-curated US-federal facts with verifiable ground truth
- **Counterbalancing:** 6-version Latin square, randomly assigned via Qualtrics Randomizer (Evenly Present)
- **Trial randomization:** 12 trials per version, shuffled within version
- **Manipulation:** Attestation strength applied downstream in code (fixed wording, source name only varies)
- **Stakes operationalization:** Defined by *consequence*, not physical danger. High-stakes = substantial, hard-to-reverse federal outcome (FAFSA deadline, Social Security, etc.). Low-stakes = minor recoverable consequence.
- **Sample:** US residents only (federal facts do not apply uniformly internationally)
- **Privacy:** Qualtrics anonymization enabled; no IP/location stored; age in ranges

## Quick Start

### Environment setup
```bash
git clone https://github.com/harrystaley/attestation-trust-study.git
cd attestation-trust-study
conda env create -f environment.yaml
conda activate attestation-trust
```

### Stimulus generation (if re-running)
```bash
# Requires OPENAI_API_KEY in .env
jupyter notebook survey_generator.ipynb
# Review outputs, curate; then:
python make_qualtrics_block.py
```

### Analysis pipeline (post-data)
```bash
# Export raw responses from Qualtrics → prepped_data/
cd analysis_pipeline
python 0-1_reconstruct_data.py    # Parse Qualtrics format
python 0-1b_clean_data.py         # Exclusions
python 0-2_prep_data.py           # Reshape
jupyter notebook attestation_trust_analysis.ipynb  # LMM & hypotheses
```

### Power analysis
```bash
cd analysis_pipeline
jupyter notebook power_analysis_simulation.ipynb
```

## Key References & Decisions

See **[DESIGN_LOG.md](DESIGN_LOG.md)** for detailed justification of major design choices:
- 7-point state-trust scale (all points labeled)
- Single-item dispositional trust (covariate only)
- Three-option behavioral reliance (reject/verify/act)
- High/low stakes binary (continuous Perceived Consequence captures variation)
- Attestation-strength wording fixed in code (not per-item LLM generation)
- No physical-harm stimuli (financial/legal/benefit consequences only)

## Contributing & Attribution

This study was developed iteratively with discussion of an AI assistant (Claude), which helped surface tradeoffs, structure reasoning, and record decisions. **All research design choices, justification, and analytical content are the author's** (Harry Staley). Use of generative AI follows the **CS 6795 course policy**.

PI: Dr. Keith McGreggor (course professor), Georgia Tech  
Course: CS 6795, Summer 2026

## License

MIT License. See [LICENSE](LICENSE) file for details.

---

**Status:** Pilot phase in progress. Data collection pending Prolific integration. Stimulus curation and power analysis underway.
