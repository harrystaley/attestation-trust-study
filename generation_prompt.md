You are generating survey stimuli for an academic experiment on how source
attestation affects trust in AI-generated answers. This is legitimate research;
the incorrect answers are controlled stimuli that will be corrected in a debrief.

Generate 12 question stems as a JSON array. Each object must have exactly:
  {schema_fields}

Definitions:
- high stakes = an item where acting on the wrong answer causes a substantial, concrete negative consequence — a significant financial loss, legal penalty, or forfeited benefit or right — ideally one that is hard to reverse. The consequence may be financial, legal, or benefit-related. The fact must apply uniformly to all US adults at the federal level (not state-specific). This may also include significant health, safety, financial, or security consequence.
  - Financial penalty/loss — tax penalties, excise taxes, lost deposits
  - Health conditions or medical medical conditions
  - Food safety
  - Benefit/coverage forfeiture — Medicare, COBRA, marketplace/Part D enrollment, missed windows
  - Legal-right or claim forfeiture — statute of limitations, appeal deadlines, contest/petition windows
  - Eligibility/status loss — federal program eligibility (choose federally-uniform ones)
  - Time-limited opportunity loss — federal student aid, loan forgiveness, one-time enrollment
  - Consumer-protection deadlines — fraud-reporting windows, dispute/rescission rights
- Low stakes = an item of factual interest where acting on the wrong answer produces minor, real, recoverable, non-physical consequence.
  - Consumer/retail facts — standard return windows, restocking-fee norms, warranty basics, receipt requirements. Wrong → lose a small refund or pay a minor fee.
  - Everyday financial-convenience facts — how long a check hold typically lasts, standard grace periods on routine bills, ATM/foreign-transaction fee norms. Wrong → small fee or minor delay.
  - Shipping/postal facts — standard delivery timeframes, what postage a standard item needs, package-insurance basics. Wrong → minor delay or a few dollars.
  - Travel-logistics facts — typical check-in/baggage cutoffs, standard cancellation windows for routine bookings, passport-processing timeframes (not requirements). Wrong → minor inconvenience or rebooking hassle.
  - Everyday-tech/subscription facts — standard free-trial lengths, typical cancellation-notice norms, data-cap basics. Wrong → a small unwanted charge, recoverable.
  - Cooking/household practical facts — standard substitution ratios, typical storage timeframes for convenience (not safety), appliance-setting norms. Wrong → a dish turns out worse, wasted ingredients — minor.
  - Restaurant reviews
  - Movie/Book reviews

Constraints:
- Exactly 12 objects: 6 low stakes, 6 high stakes.
- Question prompts MUST be phrased as a plain user question and must NOT name or cite the source within the stem (e.g., not 'According to NASA...'). The source belongs only in the source fields. However, the stem must retain enough information that the correct answer is unambiguous, preserve scoping qualifiers (e.g., 'in general,' 'at the federal level') even while removing source attribution.
- require diversity along three independent axes at once:
  - Axis A - category.
  - Axis B - consequence-type.
  - Axis C — fact-structure: not all "you have N days to X." Require a mix of deadlines, thresholds/amounts, eligibility rules, rights/entitlements, obligations. This breaks the "everything is a deadline" sameness.
- Verifiable ground truth from a real, authoritative source.
- No lengthy calculations, no trick questions, no insider/private knowledge.
- correct_answer and incorrect_answer should be MATCHED in length, tone,
  specificity, and sentence count, differing only in truth value.
- incorrect_answer must be PLAUSIBLE (not absurd) and must contradict the source.
- correct_answer must be directly supported by the source.
- Neutral, non-emotional language. No markdown.

Additional constraints on difficulty and plausibility:
- Choose questions where an educated non-expert would plausibly NOT already
  know the answer with confidence. Avoid widely known facts, common school
  knowledge, and well-known "trick" questions (e.g., tomato fruit/vegetable).
- The correct and incorrect answers must be EQUALLY plausible on their face:
  matched in confidence, specificity, and form, so that a reader who does not
  know the topic could not identify which is correct from the answer text alone.
- Prefer incorrect answers that reflect a believable common misconception or a
  plausible alternative value, not an obvious or absurd error.
- Avoid questions whose incorrect answer would be immediately recognized as
  wrong or dangerous by most adults (e.g., delaying 911 for stroke symptoms).

If you cannot produce a plausible incorrect answer for a sensitive (e.g. medical)
item, still return the object but set incorrect_answer to the string
"REFUSED_NEEDS_MANUAL" so it can be flagged for manual construction.

Return ONLY the valid JSON array. No prose, no markdown fences.