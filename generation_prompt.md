You are generating survey stimuli for an academic experiment on how source
attestation affects trust in AI-generated answers. This is legitimate research;
the incorrect answers are controlled stimuli that will be corrected in a debrief.

Generate 12 question stems as a JSON array. Each object must have exactly:
  {schema_fields}

Definitions:
- low stakes = Questions of factual curiosity, where acting on a wrong answer
  has little or no practical consequence (e.g., the length of a day on Mars, the
  year a painting was made).
- high stakes = questions where being wrong carries a real practical
  consequence, for example a financial, legal, health, safety, or security
  consequence (e.g., a deposit-insurance limit, a recommended ladder setup ratio).

Constraints:
- Exactly 12 objects: 6 low stakes, 6 high stakes.
- Diverse, non-duplicate topics; understandable by educated non-experts.
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