# Design Log — Attestation Trust Study

**Working document.** This is a running research tool for tracking design
decisions and their rationale as the study develops, kept so the reasoning can be
lifted into the project report (and defended in review). It is not a deliverable
and is not a substitute for the report; it is scratch/reference. Each entry notes
the decision, the reasoning, the tradeoff accepted, and where it lands in the
paper.

**Acknowledgment.** The decisions recorded here are the author's own (Harry
Staley). This log was developed iteratively through discussion with an AI
assistant (Claude), which helped surface tradeoffs, structure the reasoning, and
record decisions as they were made. The research design choices, their
justification, and all analytical content are the author's. Use of generative AI
follows the CS 6795 course policy.

---

## Counterbalancing implemented as six Qualtrics blocks + even Randomizer (not embedded-data)

**Decision.** The six-version Latin square is implemented in Qualtrics as **six
separate Trial blocks**, one per version (each loaded with that version's 12-row
file from `latin_square_versions.py`), wrapped in a Survey Flow **Randomizer set
to "Evenly Present Elements," presenting 1 of 6**. The alternative — a single
Trial block with version assigned via embedded data — was not used.

**Why.** [[YOUR RATIONALE — e.g., verifiability: each version's stem→condition
assignment can be inspected directly in its own block; the Randomizer logic is
simple and auditable; embedded-data version-switching is harder to verify and
more error-prone. State your actual reasoning.]]

**Tradeoff.** [[YOUR RATIONALE — e.g., six near-duplicate blocks instead of one;
more blocks to maintain, but each is trivially checkable. "Evenly Present
Elements" balances assignment counts across versions over the sample.]]

**Status.** Built in the Qualtrics survey; QSF structurally validated (flow order,
gate, randomizer even=true, 6 blocks × 12 loop rows).

**Paper location.** Experiment Design (Randomization and Counterbalancing).

---

## Trial order randomized within version; loop presents all 12 (no subset)

**Decision.** Within each participant's assigned version, the 12 trials are
presented in a **randomized order** (Loop & Merge "randomize loop order"), and
**all 12 are presented** (no random-subset selection).

**Why.** [[YOUR RATIONALE — randomized order reduces order/carryover effects per
the design; all 12 must be shown because each participant must cover every cell
once. State your reasoning.]]

**Tradeoff.** [[YOUR RATIONALE if any.]]

**Status.** [[CONFIRM: the QSF initially exported with loop Randomization='All'
(fixed order). Verify the "randomize loop order" toggle is enabled and saved on
all six Trial blocks, then re-export to confirm. Until confirmed, this is set in
intent but not verified in the exported file.]]

**Paper location.** Experiment Design (Randomization and Counterbalancing).

---

## Privacy/anonymity implemented in Qualtrics settings (Anonymize Responses ON)

**Decision.** Responses are collected with Qualtrics **"Anonymize Responses" ON**
(no IP/location stored) and **SecureResponseFiles** enabled. Age is collected in
ranges; demographics reported in aggregate; no name collected.

**Why.** [[YOUR RATIONALE — these settings make the consent/debrief privacy claims
(IP stripped, anonymous) actually true rather than merely asserted; minimal-risk
exempt design. State your reasoning.]]

**Tradeoff / open item.** [[YOUR RATIONALE — and note the Prolific-ID reconciliation:
once recruitment runs on Prolific, the Prolific ID is a persistent identifier, so
data is *pseudonymous* until the ID is stripped/separated. "Anonymous" in the
consent/debrief must be reconciled with this (or changed to "confidential"), and
the withdrawal mechanism depends on the ID-handling choice. Currently testing
WITHOUT Prolific, so the anonymity claim holds for the test phase.]]

**Status.** Anonymize Responses confirmed ON in the exported QSF. Prolific
integration (ID capture + completion redirect) intentionally deferred to after the
test phase.

**Paper location.** Ethics/Procedure; Attention Checks and Exclusion Criteria
(bot/fraud screening); Limitations (anonymity vs. pseudonymity).

---

## Dispositional trust switched to a single author-written item (reverses Merritt 6-item)

**Decision.** Dispositional (baseline) trust is now measured with a *single*
author-written item -- general trust in AI on the 5-point scale (Strongly Distrust
-> Strongly Trust) -- replacing the previously adopted six-item Merritt et al.
(2013) Propensity to Trust scale. This *reverses* the earlier "RESOLVED: use Merritt
6-item" decision recorded below.

**Why.** Lower participant burden and a simpler Qualtrics build; avoids reproducing
a published scale's copyrighted item text in the instrument. Dispositional trust is
only a *covariate* in this design (not a primary outcome), so a single-item measure
is a defensible trade -- the measurement-quality cost falls on a non-critical
variable rather than the dependent variable.

**Tradeoff.** A single item is noisier and less reliable than a validated
multi-item scale; the trait estimate has more measurement error. Accepted because
the construct is a covariate, not a DV. To record as a limitation.

**Downstream edits required (report must match the instrument).**
- Dispositional AI variables subsection: replace "six-item Propensity to Trust
  scale, a validated trait-level measure" with an accurate single-item description.
- tab:trust-levels "Instrument" row: update the dispositional cell (currently cites
  Merritt) to the single-item measure.
- tab:disposition-scale caption: remove the Merritt citation.
- References: dropping Merritt removes one citation (it had been helping move from
  7 toward the >=10 requirement); make it up elsewhere.
- Limitations: note single-item dispositional measure (reduced reliability),
  acceptable for a covariate.

**Paper location.** Procedure (measures), Demographic/Individual-Difference
Variables, Limitations, References.

---

## Low stakes redefined: minor-real consequence, not zero (Option B)

**Decision.** Low-stakes items carry a *minor, real, recoverable, non-physical*
consequence (lose a small refund, a few dollars, some time/convenience) rather than
*zero* consequence. Low-stakes categories were shifted from zero-consequence
encyclopedia trivia (astronomy, art, literature) to everyday-decision domains
(consumer/retail, financial-convenience, shipping, travel-logistics, everyday-tech,
household-quality).

**Why.** The cost-benefit account underlying H4 concerns *weighing* a real
consequence against verification cost; a literally-zero low pole gives nothing to
weigh (verification is never justified, trivially), so the theory fits better with a
small-but-real low consequence. Zero-consequence trivia also risked disengagement
(participants skim/rate without reading), adding noise to the baseline condition.

**Tradeoff.** Raising the low pole above zero *narrows* the low/high gap, slightly
reducing power for the H4 stakes-moderation test. Mitigated by keeping the high pole
severe (preserve maximum gap) and by the Perceived Consequence measure, which
quantifies the realized separation. Note: "stakes" now contrasts *minor* vs. *severe*
consequence rather than *no* vs. *severe* -- H4 tests whether severity (not mere
presence of stakes) moderates reliance.

**Boundary.** Low-consequence items must be minor *financial/time/convenience*
consequences, never *physical* (no "minor health/food-safety" items); body stays out
at both poles.

**Status.** Definition + categories updated in the generation prompt; output register
still being verified across runs.

**Paper location.** Experiment Design (operationalization of the stakes IV), Power,
Limitations.

---

## Source attribution removed from question stems

**Decision.** Question stems are phrased as plain user questions and must not name
the authoritative source inside the stem (e.g., not "According to NASA, how fast
is the Moon receding?" but "How fast is the Moon moving away from Earth?"). Source
information appears only in the attestation display, where it is manipulated across
the none/weak/strong levels.

**Why.** Naming the source in the stem leaks provenance into every condition,
including the no-attestation condition, partially collapsing the manipulation. If
"According to NASA..." is in the question itself, a participant in the none
condition still receives source information even though the provenance region is
empty, weakening the contrast between attestation levels. Source must be carried
by the attestation layer (which the study controls), not pre-loaded into the stem
(where it is constant across conditions). Removing it also improves ecological
validity: real users typically ask a bare question rather than prefacing it with
the source.

**Wrinkle / constraint on the fix.** Some stems use source framing to *scope* the
question so ground truth is well-defined (e.g., "Under the general IRS limitations
rule..." fixes which rule applies). The rephrasing must remove source *attribution*
while preserving enough *scope* that the answer retains a definite, verifiable
ground truth -- e.g., "In general, how long do you have to claim a federal tax
refund?" keeps the federal/general scope but drops the "IRS says" attribution.

**Status.** Decision made; stem rephrasing OPEN (must rewrite existing stems before
locking). Generation prompt to be updated with a constraint forbidding
source-naming in stems so future generation does not reintroduce it.

**Paper location.** Experiment Design (stimulus construction), Limitations (if any
residual scoping compromises remain).

---

## High-stakes diversity: two-axis spread to break clustering

**Decision.** High-stakes items are required to spread across two independent
axes, not just distinct topic domains: (A) consequence-type (financial /
benefit-loss / legal-right forfeiture / rights-or-status / legal-obligation) and
(B) fact-structure (deadline / threshold-amount / eligibility rule /
right-entitlement / obligation). The intent is no more than ~two items sharing a
consequence-type and no more than ~two sharing a fact-structure.

**Why.** Across runs the high-stakes items clustered into "a federal
financial/benefits deadline" even when agencies differed — the sameness was on
consequence-type (financial/benefits) and fact-structure (deadlines), not agency.
Constraining only topic/agency did not break it. Requiring spread on the two
underlying axes forces variety the topic-level rule could not (e.g., a
rights-entitlement or an obligation rather than another N-day filing window).

**Tradeoff.** Tighter constraints reduce run-to-run variety somewhat; mitigated by
the candidate-pool curation workflow (generate several runs, select best-in-breed).
Rights/civic items must still pass the federal-uniform and uncontested-ground-truth
filters (avoid state-specific or interpretive facts).

**Status.** Two-axis constraint added to the generation prompt; effect on output
still being evaluated across runs.

**Paper location.** Experiment Design (stimulus construction / materials).

---

## Per-trial measure set reduced to three (dropped topic knowledge)

**Decision.** The per-trial measure set is trust (1-7), behavioral reliance
(reject / verify / act), and perceived consequence ("how serious if wrong"). The
topic-knowledge item was removed, reducing per-trial responses from 4x12=48 to
3x12=36.

**Why.** 48 per-trial responses risked fatigue and dropout. Topic knowledge was
the only exploratory item (not testing a core hypothesis), so it was the
lowest-cost cut: trust and reliance are the primary outcomes and perceived
consequence is the H4 mediator, so all three were kept.

**Tradeoff.** Per-trial prior knowledge is no longer measured as a control; to be
noted in Limitations. Confirm the reduced burden is acceptable in the pilot.

**Status.** Applied. Report edits open: remove the Topic Knowledge subsection and
its scale table.

**Paper location.** Procedure (measures), Limitations.

---

## Behavioral reliance: finalized wording (three ordered options)

**Decision.** Reliance uses three ordered options, coded 1->3 as increasing
reliance:
1. Reject/don't use the information or take the recommended action.
2. Verify before taking action or using the information.
3. Use the information or take the recommended action (do not double-check).

**Why.** Reliance is kept distinct from the state-trust scale by the verify-cost
middle option: trust is an attitude (1-7), whereas reject/verify/act captures
whether the participant will pay a verification cost -- a behavioral choice
(Vasconcelos). The "use/act" pole is phrased to read coherently for both a
real-world decision (high-stakes) and using a fact (low-stakes).

**Note.** Measured on all 12 trials; interpretation spotlights the high-stakes
cells. Residual check: option 1's "do not" should clearly govern both "use" and
"take the action."

**Status.** Wording finalized by author.

**Paper location.** Procedure (behavioral reliance measure), Analysis.

---

## Stakes: kept binary (low/high), gradation captured by measure

**Decision.** Stakes remains a 2-level manipulated factor (low / high). It is NOT
expanded into more levels (e.g., very-low / low / high / very-high). The
*gradation* of severity within the high condition is captured by the continuous
per-trial Perceived Consequence measure, not by adding factor levels.

**Why.** Adding stakes levels would break the clean 3x2x2 = 12-cell design (one
trial per cell, 12 trials per participant). Going to 4 levels = 3x2x4 = 24 cells,
which would either double survey length, break the one-per-cell within-subjects
structure, or force a different design — and would reduce power per cell for the
already-secondary stakes-moderation test. The continuous Perceived Consequence
measure already records how consequential each item felt, so "very high vs. high"
is captured as measured data without multiplying cells. A sharp binary contrast
with well-separated items is more powerful than a muddy multi-level one.

**Status.** Settled. Design stays 3x2x2.

**Paper location.** Experiment Design (factor structure), Methods (measures).

---

## High-stakes definition strengthened (severity + non-physical + federal)

**Decision.** The high-stakes criteria are tightened so high items are strong and
cleanly separated from low. A high-stakes item now requires:
- **Substantial** consequence (significant financial loss, legal penalty, or
  forfeited benefit/right), not a minor one;
- **Hard to reverse** where possible (permanent benefit reduction, missed
  one-time deadline, forfeited right) — favored over recoverable outcomes;
- **Non-physical harm vector** — financial / legal / benefit-related, NOT
  physical injury (this is the safe-design line, stated explicitly);
- **Federal / nationally uniform** — applies to all US adults equally, not
  state-specific.
High items may *range* from serious to very serious; that variety is captured by
Perceived Consequence, not by factor levels.

**Why.** Earlier high items varied in strength; some were only moderate (passport
mail-renewal — recoverable) and one was physical-harm-adjacent (OSHA ladder ratio
-> fall risk), which sits on the wrong side of the consequence-not-danger rule.
Strengthening the criteria raises the floor of the high condition and keeps the
whole set on the non-physical side.

**Item review (current set).** Keep (strong, non-physical, federal): Social
Security full retirement age, FAFSA deadline, Medicare IEP, federal tax extension
(file != pay). Reconsider/replace: passport DS-82 (moderate, recoverable), OSHA
ladder 4:1 (physical-harm-adjacent). Already flagged for replacement: Texas voter
registration (sub-national).

**Status.** Criteria decided; prompt wording + item swaps OPEN.

**Paper location.** Experiment Design (stimulus construction).

---

## Stakes: defined by consequence, not domain

**Decision.** High vs. low stakes is operationalized by the *consequence of
being wrong*, not by topic domain. High = acting on the wrong answer produces a
real, tangible negative outcome; low = no meaningful consequence (at most a
trivial inconvenience or a corrected misconception). Stakes is treated
holistically (magnitude, domain, relevance); Perceived Consequence validates the
manipulation empirically.

**Why.** An earlier draft defined high-stakes by domain, which leaked: a trivial
financial fact (free-credit-report frequency) matched the domain but carried no
real consequence. Defining by consequence closes the leak.

**Test applied to each item.** "If a participant believed the wrong answer and
acted on it, what specifically goes wrong, and how bad is it?" If the answer is
"nothing, really," it is low-stakes regardless of topic.

**Status.** Settled. In README ("Stakes, defined") and the generation prompt.

**Paper location.** Experiment Design (operationalization of the stakes IV).

---

## Stakes manipulated via consequence, not physical danger

**Decision.** Stakes is manipulated through how consequential the decision is,
not through physically dangerous content. Stimuli avoid topics where briefly
believing the wrong answer could cause physical harm — including not adding even
a single physical-harm "anchor" item.

**Why.** A plausible, source-backed, physically-dangerous false answer is a
harmful artifact independent of the study (one item or many): it can lodge in
memory, is not reliably undone by debrief, reaches skimmers/dropouts, and is not
IRB-exempt-approvable. It also reintroduces a confound (that item would differ on
BOTH consequence and danger). Felt consequence — the measured construct —
saturates near ceiling on severe non-physical items (lose federal aid; permanent
benefit cut), so a danger item adds risk without adding measurement on the scale
the study uses. Consistent with prior reliance literature (Vasconcelos, Bansal),
which uses non-dangerous stimuli.

**Status.** Settled and firm.

**Paper location.** Experiment Design (stimulus construction), Ethics/Limitations.

---

## Sampling: US-only

**Decision.** Recruit US residents only (Prolific prescreen).

**Why.** High-stakes stimuli are US-federal facts. For non-US participants those
items carry no real stakes, so an international sample would dilute the stakes
manipulation. US-only matches sample to stimuli and is internally cleaner
(removes within-sample variation in whether federal facts apply).

**Tradeoff.** Limited external validity. The global LLM user population is
majority non-US and growing fastest in lower-/middle-income countries; the US is
the largest single market (~17%) but not the majority. (Cite adoption figures
from a primary/academic source, not SEO aggregators.)

**Mitigation.** Stated in Limitations; cross-cultural replication framed as
motivated future work.

**Status.** Settled. In README recruitment line ("US residents only").

**Paper location.** Experiment Design (recruitment), Limitations, Conclusion.

---

## Stimuli: US-federal, not sub-national

**Decision.** High-stakes facts must apply uniformly to the US sample at the
federal level, not vary by state or locality.

**Why.** A state-specific item varies in stakes even within a US sample (a
non-Texan cannot be consequentially wrong about Texas registration),
reintroducing the dilution US-only sampling removes.

**Action (OPEN).** Replace the sub-national item (Texas voter registration) with
a federal high-stakes fact passing the consequence test.

**Paper location.** Experiment Design (stimulus construction).

---

## Attestation strength defined in code, not in the generation prompt

**Decision.** The LLM prompt generates content and source fields only. The three
attestation levels (none / weak / strong) are applied downstream in code
(`attestation_text()`), with fixed wording.

**Why.** The attestation display is the manipulation and must be identical in
form across items at a given strength (only the source name varies). Generating
it per-item would introduce uncontrolled variation. Verification language is
source-scoped (vouches for the source, never the answer's truth), so it holds on
incorrect-answer items.

**Status.** Settled. Implemented in `survey_generator.ipynb`.

**Paper location.** Experiment Design (attestation manipulation).

---

## Stimulus generation: LLM-generated, author-curated

**Decision.** Candidate stimuli are LLM-generated, then author-curated. Generation
is logged (model, run date); final stimuli committed to the repo.

**Why.** Reproducible, transparent; committed set is the actual curated instrument
(not cleanly regenerable given non-deterministic generation + hand curation).

**Curation steps.** (1) Verify each correct answer matches its real source —
especially high-consequence, date-sensitive items. (2) Confirm correct/incorrect
distinct and topics non-duplicate (verified mechanically — clean). (3) Flag items
for the debrief.

**Status.** Pipeline complete; curation pass OPEN.

**Paper location.** Experiment Design (materials), Methods.

---

## Verified facts (ground-truth spot-checks)

Confirmed against live sources:
- **FTC free weekly credit reports** — permanent (item later cut as low-consequence).
- **2024 gift-tax annual exclusion = $18,000** — confirmed ($17,000 was 2023,
  which is why it is a plausible wrong answer).

Still to verify before locking: FAFSA 2025-26 deadline, SS full retirement age
(1960+), Medicare IEP length, passport DS-82 15-year window, IRS Form 4868
(file != pay), OSHA ladder 4:1 citation.

---

## Open items

- [x] Finalize tightened high-stakes prompt wording (substantial / hard-to-reverse
      / non-physical / federal); keep stakes binary.
- [x] Replace passport (moderate) and OSHA ladder (physical-adjacent) high items
      with stronger non-physical federal items.
- [x] Replace Texas voter-registration item with a federal equivalent.
- [ ] Ground-truth verification pass on high-consequence date-sensitive items.
- [x] Source attribution removed from stems: "no source-naming in stems"
      constraint added to the generation prompt; confirmed working (run
      2026-06-21T172759: 1/12 stems named a source, down from 12/12 in an
      unconstrained run -- the one remaining names the law being asked about,
      not a source authority).
- [x] Run timestamp added to generation outputs: generator now writes
      timestamped filenames and a timestamp field in generation_metadata.json
      (e.g., 2026-06-21T172759).
- [ ] Reconcile Python version (environment.yaml 3.13 vs. runtime 3.14).
- [x] PI designation resolved: Dr. Keith McGreggor (course professor) is PI for
      the course exempt-consent submission. Source: TA Robert J. Forwerck, Ed
      Discussion #310 ("IRB Waiver for Surveys"), CS 6795 Summer 2026, answering
      that the course professor (Dr. Keith McGreggor) should be listed as PI on
      the GT Exempt Consent Template. Note: a separate PI arrangement (Madisetti)
      may apply if this is later pursued as a CS 8903 publication — track
      separately.
- [ ] Power analysis / target N (pilot-driven).
- [x] Debrief screen (must correct the false answers shown).
- [ ] Abstract: required for the final report and counts toward the word-count
      limit (per Ed #323, citing TA guidance in thread 8109047). Write last,
      ~150-250 words, no citations; budget within the ~4000-word total, not on
      top of it.