# Design Log — Attestation Trust Study

**Working document.** This is a running record of design decisions and their
rationale, kept so the reasoning can be lifted into the project report (and
defended in review). It is not a deliverable and is not a substitute for the
report; it is scratch/reference. Each entry notes the decision, the reasoning,
the tradeoff accepted, and where it lands in the paper.

---

## Stakes: defined by consequence, not domain

**Decision.** High vs. low stakes is operationalized by the *consequence of
being wrong*, not by topic domain. An item is high-stakes if acting on the wrong
answer produces a real, tangible negative outcome (financial loss, legal
penalty, health/safety risk, forfeited right or benefit of real value);
low-stakes if being wrong has no meaningful consequence (at most a trivial
inconvenience or a corrected misconception). Stakes is treated holistically
(bundling magnitude, domain, and relevance); the per-trial Perceived Consequence
measure validates the manipulation empirically.

**Why.** An earlier draft defined high-stakes by domain (financial, legal,
health, etc.). That leaked: a trivial financial fact (how often you can pull a
free credit report) pattern-matched the domain but carried no real consequence,
muddying the manipulation. Defining by consequence closes the leak.

**Test applied to each item.** "If a participant believed the wrong answer and
acted on it, what specifically goes wrong, and how bad is it?" Items where the
answer is "nothing, really" are low-stakes regardless of topic.

**Status.** Settled. Documented in README ("Stakes, defined"); reflected in the
generation prompt.

**Paper location.** Experiment Design (operationalization of the stakes IV).

---

## Stakes manipulated via consequence, not physical danger

**Decision.** Stakes is manipulated through how consequential the decision is,
not through physically dangerous content. Stimuli avoid topics where briefly
believing the wrong answer could cause physical harm.

**Why.** Generating plausible, source-backed false answers in physically
dangerous domains (e.g., medical dosing, emergency response) creates a harmful
artifact independent of the study, is not reliably undone by debrief, and is not
IRB-exempt-approvable. The trust mechanism under study does not require dangerous
content; perceived consequence (the measured mediator) captures the construct
regardless of content danger. (Consistent with prior reliance literature, which
uses non-dangerous stimuli.)

**Tradeoff.** None of substance for the construct; some loss of "maximally
visceral" high-stakes framing, which is not needed.

**Status.** Settled. Reflected in the generation prompt's safety constraints.

**Paper location.** Experiment Design (stimulus construction), Ethics/Limitations.

---

## Sampling: US-only

**Decision.** Recruit US residents only (Prolific prescreen).

**Why.** High-stakes stimuli are US-federal facts (IRS, SSA, Medicare, FAFSA,
State Department). For non-US participants those items carry no real stakes, so
an international sample would dilute the stakes manipulation with participants
for whom it does not apply. US-only matches sample to stimuli and removes that
noise. (Note: US-only is also internally cleaner — it removes within-sample
variation in whether federal facts apply.)

**Tradeoff.** Limited external validity. The global LLM user population is
majority non-US and growing fastest in lower- and middle-income countries, so a
US sample with US-specific stimuli captures a large but unrepresentative slice.
The US is the largest single market (~17% of users) but not the majority.
(Directional adoption figures to be cited from a primary/academic source, not
SEO aggregators.)

**Mitigation.** Stated explicitly in Limitations; cross-cultural replication
framed as motivated future work (the population where AI-trust behavior is
forming fastest is the one least sampled here).

**Status.** Settled. Documented in README recruitment line ("US residents
only").

**Paper location.** Experiment Design (recruitment), Limitations, Conclusion
(future work).

---

## Stimuli: US-federal, not sub-national

**Decision.** High-stakes facts must apply uniformly to the US sample at the
federal level, not vary by state or locality.

**Why.** A state-specific item (e.g., Texas voter-registration deadline) varies
in stakes even within a US sample — a non-Texan cannot be consequentially wrong
about it — which reintroduces the same dilution US-only sampling was meant to
remove. Federal facts apply uniformly to all US participants.

**Action (OPEN).** Replace the one sub-national item (Texas voter registration)
with a federal-level high-stakes fact that passes the consequence test.

**Status.** Decided; one item swap pending.

**Paper location.** Experiment Design (stimulus construction).

---

## Attestation strength defined in code, not in the generation prompt

**Decision.** The LLM prompt generates content and source fields only. The three
attestation levels (none / weak / strong) are applied downstream in code
(`attestation_text()`), with fixed wording.

**Why.** The attestation display is the experimental manipulation and must be
*identical in form* across items at a given strength level — only the source name
varies. Letting the model generate attestation text would introduce uncontrolled
per-item variation and confound the manipulation. Verification language is
source-scoped (it vouches for the source, never the answer's truth), so it holds
even on incorrect-answer items.

**Status.** Settled. Implemented in `survey_generator.ipynb`.

**Paper location.** Experiment Design (attestation manipulation).

---

## Stimulus generation: LLM-generated, author-curated

**Decision.** Candidate stimuli are LLM-generated, then author-curated before
use. Generation is logged (model, run date) for reproducibility; final stimuli
are committed to the repo.

**Why.** Reproducible, transparent method; the committed set is the actual
curated instrument (not cleanly regenerable, given non-deterministic generation
plus hand curation).

**Curation steps.** (1) Verify each correct answer matches its real source —
especially high-consequence, date-sensitive items (FAFSA deadline, SS full
retirement age, Medicare IEP, passport DS-82 window, IRS extension rule).
(2) Confirm correct/incorrect distinct and topics non-duplicate (verified
mechanically — clean). (3) Flag any items for the debrief.

**Status.** Generation pipeline complete and working; curation pass OPEN.

**Paper location.** Experiment Design (materials/stimulus construction), Methods.

---

## Verified facts (ground-truth spot-checks)

Confirmed against live sources during curation:
- **FTC free weekly credit reports** — confirmed permanent (was the basis of an
  earlier item; that item later cut as low-consequence).
- **2024 gift-tax annual exclusion = $18,000** — confirmed ($17,000 was the 2023
  value, which is why it is a plausible wrong answer).

Still to verify before locking the current set: FAFSA 2025-26 deadline, SS full
retirement age (1960+), Medicare IEP length, passport DS-82 15-year window, IRS
Form 4868 (extension to file != extension to pay), OSHA ladder 4:1 ratio citation.

---

## Open items

- [ ] Replace the Texas voter-registration item with a federal equivalent
      (consequence test + distinctness check).
- [ ] Ground-truth verification pass on high-consequence date-sensitive items
      (FAFSA, SS, Medicare, passport, IRS 4868, OSHA citation).
- [ ] Add a run timestamp to generation_metadata.json at final locked generation.
- [ ] Reconcile Python version (environment.yaml 3.13 vs. runtime 3.14).
- [ ] Confirm stale survey_genrator_example.py removed from repo.
- [ ] PI designation (course vs. advisor) - gates IRB submission.
- [ ] Power analysis / target N (pilot-driven).
- [ ] Debrief screen (must correct the false answers shown).