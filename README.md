# Attestation Trust Study

Companion repository for **“Source Attestation Decouples Trust Formation from Trust Calibration in AI-Assisted Decisions”** by Harry A. Staley and Vijay K. Madisetti.

This repository contains the experimental materials, survey instrument, de-identified trial-level data, preprocessing pipeline, statistical analysis code, power simulations, and reproducibility materials associated with the study.

The study examines whether source provenance helps people **calibrate** their trust in AI-generated information to its objective correctness, or instead acts as a heuristic cue that increases trust irrespective of accuracy.

> **Study status:** Data collection is complete. The final analytic sample consists of **97 participants and 1,164 participant-trials**. This repository serves as the computational and materials companion to the associated publication.

---

## Key findings

Source attestation increased participants' reported trust and intended behavioral reliance on AI-generated information, but did **not** improve their ability to distinguish correct from incorrect responses.

In the final analyses:

* Trust increased monotonically with attestation strength.
* Intended behavioral reliance also increased with attestation strength.
* Stronger attestation did **not** significantly improve trust calibration, operationalized through the interaction between attestation strength and objective correctness.
* Higher decision stakes reduced both trust and intended reliance.
* The stakes manipulation was strongly reflected in participants' perceived-consequence ratings.
* Exploratory analyses suggest that state trust may help explain the relationship between source attestation and intended reliance.

Together, the results suggest that source provenance can influence **trust formation** without necessarily improving **trust calibration**.

---

## Study design

The experiment used a **3 × 2 × 2 repeated-measures factorial design**:

* **Source attestation** — None / Weak / Strong
* **Objective correctness** — Correct / Incorrect
* **Decision stakes** — Low / High

Each participant completed **12 experimental trials**, providing one observation from each factorial condition.

Stimulus-to-condition assignment was counterbalanced across six survey versions using a cyclic Latin-square procedure separately within the low- and high-stakes stimulus pools. Trial order was randomized within participant.

### Measures

Three trial-level outcomes were collected:

| Measure                   | Scale                                                                   |
| ------------------------- | ----------------------------------------------------------------------- |
| **Trust**                 | 1 (Strongly Distrust) to 7 (Strongly Trust)                             |
| **Behavioral reliance**   | Reject / Verify Before Acting / Use Without Verification                |
| **Perceived consequence** | Five-point rating of the consequences of relying on an incorrect answer |

Perceived consequence served as a manipulation check for the decision-stakes manipulation.

---

## Research questions and hypotheses

The central research question was:

> **Does graded source attestation enhance users' capacity to discriminate between correct and incorrect AI-generated information, or does it primarily increase trust irrespective of objective correctness?**

The study evaluated four hypotheses:

* **H1 — Source Attestation Increases Trust and Reliance.** Trust and intended behavioral reliance increase monotonically with source-attestation strength (None < Weak < Strong).

* **H2 — Source Attestation Improves Trust Calibration.** Stronger source attestation improves calibration such that trust in objectively correct responses increases more than trust in objectively incorrect responses.

* **H3 — Trust Mediates Behavioral Reliance.** State trust mediates the association between source attestation and intended behavioral reliance.

* **H4 — Decision Stakes Moderate Trust and Reliance.** High-stakes scenarios produce more conservative trust and reliance judgments and may moderate the influence of source attestation.

The final results supported H1, did not support H2, provided preliminary exploratory evidence relevant to H3, and showed lower trust and reliance under high stakes without evidence that stakes moderated the attestation effect.

---

## Participants

The study was conducted from **June 22 through July 20, 2026**.

Participants were recruited through in-person contacts, targeted LinkedIn recruitment messages, and the SurveyCircle survey exchange platform. Eligibility required participants to:

* be at least 18 years old; and
* reside in the United States.

The resulting sample should be considered a **convenience sample** rather than a probability-based sample.

Following preprocessing and application of the study's exclusion criteria, the final analytic dataset contained:

* **97 participants**
* **12 trials per participant**
* **1,164 participant-trials**

---

## Experimental materials

The study used twelve information-seeking scenarios spanning everyday factual domains including taxation, health, cooking, and cybersecurity.

For each scenario, correct and incorrect responses were constructed and matched on surface characteristics such as length, detail, and writing style. Ground truth was established using authoritative sources.

Candidate experimental stimuli were generated with assistance from a large language model and subsequently reviewed and curated by the researchers before use. The exact experimental materials used in the study are retained in this repository; reproducing the statistical analyses does not require regenerating the stimuli.

---

## Repository structure

### Survey construction and experimental materials

| File / directory                 | Description                                                                                                    |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `survey_generator.ipynb`         | Generates and validates candidate stimuli and constructs the master Qualtrics Loop & Merge table.              |
| `generation_prompt.md`           | Prompt and constraints used to generate candidate experimental stimuli.                                        |
| `make_qualtrics_block.py`        | Generates Qualtrics advanced-format trial-block markup with Loop & Merge fields.                               |
| `latin_square_versions.py`       | Constructs the six counterbalanced experimental versions from the master stimulus table.                       |
| `AI_Attestation_Trust_Study.qsf` | Qualtrics survey definition used for the experiment.                                                           |
| `survey/`                        | Participant-facing consent, instructions, debriefing materials, corrections, and generated trial-block markup. |
| `output/`                        | Generated and curated stimulus materials and intermediate survey-construction outputs.                         |
| `versions_output/`               | Six counterbalanced 12-trial stimulus sets used by the Qualtrics trial blocks.                                 |

### Analysis pipeline

The preprocessing pipeline runs in numbered order, with each stage consuming the output of the preceding stage.

| File                                                 | Description                                                                                                                                                               |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `analysis_pipeline/0-1_reconstruct_data.py`          | Reconstructs trial-level conditions from the Qualtrics export and converts responses to long format.                                                                      |
| `analysis_pipeline/0-1b_clean_data.py`               | Applies participant-level data-quality and exclusion rules before statistical analysis.                                                                                   |
| `analysis_pipeline/0-2_prep_data.py`                 | Converts survey labels to numeric analysis variables and applies the experimental condition codings.                                                                      |
| `analysis_pipeline/0-3_fit_pilot_model.py`           | Estimates mixed-effects model parameters for use as candidate inputs to simulation-based power analysis.                                                                  |
| `analysis_pipeline/attestation_trust_analysis.ipynb` | Primary analysis notebook containing descriptives, mixed-effects models, calibration analyses, exploratory mediation, robustness checks, diagnostics, and visualizations. |
| `analysis_pipeline/power_analysis_simulation.ipynb`  | Monte Carlo power analysis for the factorial mixed-effects design.                                                                                                        |
| `analysis_pipeline/analysis_results.csv`             | Tidy output of fitted statistical models.                                                                                                                                 |
| `analysis_pipeline/power_results_detailed.csv`       | Detailed simulation-based power estimates.                                                                                                                                |
| `analysis_pipeline/images/`                          | Generated analysis figures and model diagnostics.                                                                                                                         |

### Data

| File                                        | Description                                                                      |
| ------------------------------------------- | -------------------------------------------------------------------------------- |
| `prepped_data/long_reconstructed.csv`       | Trial-level dataset reconstructed from the Qualtrics export.                     |
| `prepped_data/long_coded.csv`               | De-identified, analysis-ready trial-level dataset used for the primary analyses. |
| `prepped_data/pilot_long_reconstructed.csv` | Reconstructed pilot dataset.                                                     |
| `prepped_data/pilot_long_coded.csv`         | Analysis-ready pilot dataset.                                                    |

The public research dataset contains no personally identifying information, authentication credentials, or API keys.

### Reproducibility and documentation

| File                       | Description                                                                   |
| -------------------------- | ----------------------------------------------------------------------------- |
| `environment.yaml`         | Conda environment definition.                                                 |
| `requirements.txt`         | Python package dependencies.                                                  |
| `setup_env.py`             | Creates the local `.env` template required for API-based stimulus generation. |
| `generation_metadata.json` | Records stimulus-generation metadata for reproducibility.                     |
| `LICENSE`                  | Licensing and reuse terms for repository contents.                            |
| `NOTICE.md`                | Copyright and AI-assistance disclosures.                                      |
| `DESIGN_LOG.md`            | Working record of study-design decisions and rationale.                       |

---

## Reproducing the computational environment

Python 3.13+ is required.

### Conda

```bash
conda env create -f environment.yaml
conda activate attestation-trust
```

### pip

```bash
pip install -r requirements.txt
```

Stimulus generation additionally requires access to the OpenAI API:

```bash
python setup_env.py
```

Then add the required API credential to `.env`.

The `.env` file is excluded from version control and should **never** be committed to the repository.

> API access is required only to reproduce the **stimulus-generation procedure**. It is not required to reproduce the statistical analyses using the retained experimental materials and data.

---

## Reproducing the experimental materials

### Stimulus generation

Run:

```text
survey_generator.ipynb
```

The notebook generates candidate stimuli, evaluates them against the experimental design constraints, identifies items requiring manual review, and constructs a Qualtrics-compatible Loop & Merge table.

LLM-generated candidates were **not automatically accepted as experimental stimuli**. Candidate items were reviewed and curated before inclusion in the study.

Generated artifacts include:

* `generated_stems.json`
* `generated_stems.csv`
* `qualtrics_loop_table.csv`
* `generation_metadata.json`

Because LLM outputs may vary across model versions and API runs, rerunning the generation notebook is not expected to reproduce candidate text byte-for-byte. The exact curated materials presented to participants are retained as study artifacts.

### Counterbalancing

The master stimulus table is divided into six experimental versions using:

```bash
python latin_square_versions.py
```

The procedure applies the cyclic Latin square separately to the low- and high-stakes stimulus pools. Each resulting version contains 12 trials.

### Qualtrics implementation

Trial-block markup is generated with:

```bash
python make_qualtrics_block.py
```

The six counterbalanced version files are assigned to six corresponding Qualtrics trial blocks. A Survey Flow Randomizer assigns each participant to one counterbalancing version, and trial order is randomized within the selected version.

The participant flow was:

**Consent → Instructions → Baseline Trust → Experimental Trials → Demographics → Debrief → End**

---

## Reproducing the analysis

The analysis pipeline is designed to run sequentially.

### 1. Reconstruct the Qualtrics export

```bash
python analysis_pipeline/0-1_reconstruct_data.py
```

This reconstructs the experimental condition associated with each participant-trial and converts the Qualtrics export into long format.

### 2. Apply data-quality rules

```bash
python analysis_pipeline/0-1b_clean_data.py
```

This stage applies the study's participant-level exclusion and data-quality rules.

### 3. Prepare analysis variables

```bash
python analysis_pipeline/0-2_prep_data.py
```

This converts survey response labels to numeric variables and applies the analysis codings.

For the mixed-effects analyses:

* source attestation is coded `0 / 1 / 2` for None / Weak / Strong;
* objective correctness is centered at `−0.5 / +0.5`; and
* decision stakes is centered at `−0.5 / +0.5`.

### 4. Run the primary analyses

Open and execute:

```text
analysis_pipeline/attestation_trust_analysis.ipynb
```

with `DATA_PATH` pointing to the analysis-ready dataset.

The primary analyses use linear mixed-effects models with crossed random effects for participant and question stem.

The primary trust model is conceptually:

```text
Trust ~ Attestation + Correctness + Stakes
        + (1 | Participant) + (1 | Stem)
```

Trust calibration is evaluated using:

```text
Trust ~ Attestation * Correctness + Stakes
        + (1 | Participant) + (1 | Stem)
```

Behavioral reliance is analyzed using an analogous mixed-effects model. Because reliance is an ordinal outcome, ordinal logistic regression and generalized estimating equations are also used as robustness analyses.

### 5. Power analysis

Run:

```text
analysis_pipeline/power_analysis_simulation.ipynb
```

The notebook uses Monte Carlo simulation to estimate power for the interaction effects under the repeated-measures design.

---

## Main statistical results

### Trust

Mean trust increased across attestation conditions:

| Attestation | Mean trust |
| ----------- | ---------: |
| None        |       3.92 |
| Weak        |       4.34 |
| Strong      |       4.76 |

The mixed-effects model estimated a significant positive effect of source attestation on trust:

**b = 0.42, SE = 0.05, z = 8.80, p < .001**

Decision stakes reduced reported trust:

**b = −0.40, SE = 0.08, z = −5.12, p < .001**

### Trust calibration

The attestation × correctness interaction did not provide evidence that stronger attestation improved calibration:

**b = −0.05, SE = 0.10, z = −0.57, p = .57**

Thus, stronger attestation increased overall trust but did not significantly increase participants' ability to distinguish correct from incorrect AI-generated responses.

### Behavioral reliance

Stronger attestation also increased intended behavioral reliance:

**b = 0.105, SE = 0.018, z = 5.89, p < .001**

Mean intended reliance increased from **2.03** without attestation to **2.24** with strong attestation.

Higher decision stakes reduced intended reliance:

**b = −0.248, SE = 0.029, z = −8.52, p < .001**

Ordinal logistic and generalized estimating equation robustness analyses produced substantively similar results.

### Stakes manipulation check

Participants rated the consequences of being wrong substantially higher in high-stakes scenarios:

* Low stakes: **M = 2.50**
* High stakes: **M = 3.96**

The corresponding mixed-effects estimate was:

**b = 1.46, SE = 0.06, z = 24.42, p < .001**

---

## Statistical power

Monte Carlo simulations were used to characterize the sensitivity of the design to attestation × correctness interaction effects.

At a sample size near the realized **N = 97**, the design achieved approximately 80% power for interaction effects around **β = 0.25–0.30 or larger**, but had low power for small interactions.

Accordingly, the nonsignificant calibration result provides evidence against medium or larger calibration effects but does **not** rule out very small effects.

The three-way interaction involving decision stakes was substantially underpowered and should be interpreted descriptively rather than as a well-powered confirmatory test.

---

## Reproducibility notes

Several distinctions are important when reproducing or extending this work:

1. **Exact experimental materials are preserved.** Regenerating candidate stimuli with an LLM is not necessary to reproduce the experiment or statistical analyses.

2. **LLM generation is nondeterministic.** Rerunning the stimulus-generation pipeline may not reproduce candidate text byte-for-byte because models and API behavior can change.

3. **Generated and curated materials are distinct.** Automated generation and validation supported stimulus development, but researchers reviewed and curated the final experimental materials.

4. **Pilot estimates are not confirmatory evidence.** Pilot analyses were used for pipeline validation and as candidate inputs to power simulations.

5. **API access is not required for statistical reproduction.** Analysis is performed against retained experimental materials and the de-identified dataset.

6. **Ordinal-outcome robustness checks are included.** Although the principal reliance analysis uses the same mixed-effects framework as the trust analysis, ordinal logistic and GEE models are provided to assess robustness to the treatment of the reliance scale.

---

## Research ethics and data availability

The study involved human participants and was conducted under the applicable Institutional Review Board requirements.

The public repository contains the **de-identified trial-level dataset** used for the reported analyses. Personally identifying information, authentication credentials, and API keys are not included.

The experimental materials, survey instrument, preprocessing code, analysis notebooks, and reproducibility artifacts necessary to inspect and reproduce the reported analyses are provided in this repository.

---

## Generative AI disclosure

Generative AI was used in two roles during this research.

First, a large language model assisted with literature organization, reference formatting, and minor technical debugging. Analytical and interpretive conclusions were reviewed and written by the authors.

Second, a large language model was used as part of the experimental stimulus-generation process. Candidate stimuli generated through this process were subsequently reviewed and curated by the researchers before inclusion in the experiment.

See [`NOTICE.md`](NOTICE.md) for additional disclosures concerning AI assistance and repository materials.

---

## Associated publication

**Harry A. Staley and Vijay K. Madisetti**
*Source Attestation Decouples Trust Formation from Trust Calibration in AI-Assisted Decisions*

Publication venue, DOI, and archival citation will be added when available.

Once the publication record is finalized, users of this repository should cite the associated paper rather than the repository alone.

---

## Citation

Citation information for the associated publication will be added when available.

A machine-readable `CITATION.cff` file can be used to provide citation metadata for GitHub and archival services.

---

## Versioning and archival record

The version of this repository corresponding to the published study should be preserved as a **tagged release**.

Where possible, the publication-associated release should also be deposited in a persistent research archive such as Zenodo to obtain an immutable DOI.

The publication should reference the archived release or DOI rather than relying solely on the repository's moving default branch.

---

## License

This repository is distributed under the terms specified in [`LICENSE`](LICENSE).

Human-subjects data are additionally subject to the applicable research protocol, participant consent, and data-sharing requirements.

See [`NOTICE.md`](NOTICE.md) for additional copyright and AI-assistance disclosures.

---

## Authors

**Harry A. Staley**
College of Computing
Georgia Institute of Technology

**Vijay K. Madisetti**
College of Computing
Georgia Institute of Technology
