---
name: feedback-review-quality-not-existence
description: review pass/fail must judge quality, not mere presence
metadata:
  node_type: memory
  type: feedback
---

# Review Quality, Not Existence

Use this as a quick self-check when doing reviews, scoring, GDD review, numeric review, or design analysis.
The active execution rule lives in `.agents/rules/quality-gates.md`; this memory keeps the user correction and short heuristic.

## Rule of thumb

Do not mark a criterion as `达标`, `通过`, or `合格` merely because the design exists.
A positive review must judge quality:

- Within-criterion quality: is this specific design coherent, sufficient, and reasonable?
- Cross-criterion quality: do scale, rhythm, burden, and long-term control work together globally?
- Stage boundary: if exact numeric data is missing, judge structure/direction, not numeric balance.

## Self-check

Before writing a positive conclusion, ask: `Is my basis just "X exists"?`
If yes, add the quality judgment or downgrade the conclusion.

## Archive

Full original feedback and failure example were archived at:

`archived/feedback_review_quality_not_existence_full_2026-07-01.md`
