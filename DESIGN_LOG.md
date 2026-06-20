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

- [ ] Finalize tightened high-stakes prompt wording (substantial / hard-to-reverse
      / non-physical / federal); keep stakes binary.
- [ ] Replace passport (moderate) and OSHA ladder (physical-adjacent) high items
      with stronger non-physical federal items.
- [ ] Replace Texas voter-registration item with a federal equivalent.
- [ ] Ground-truth verification pass on high-consequence date-sensitive items.
- [ ] Add a run timestamp to generation_metadata.json at final locked generation.
- [ ] Reconcile Python version (environment.yaml 3.13 vs. runtime 3.14).
- [ ] Confirm stale survey_genrator_example.py removed from repo.
- [ ] PI designation (course vs. advisor) - gates IRB submission.
- [ ] Power analysis / target N (pilot-driven).
- [ ] Debrief screen (must correct the false answers shown).