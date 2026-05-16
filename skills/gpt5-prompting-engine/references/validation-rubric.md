# GPT-5 Prompt Validation Rubric

Score each category 0-2 for a total of 10.

## Technical Correctness
- 2: Techniques match the selected prompt type and target usage.
- 1: Mostly correct but some techniques are generic.
- 0: Techniques are mismatched or unsupported.

## Contradiction Cleanup
- 2: No unresolved contradictions, weak polite commands, or mixed priorities.
- 1: Minor ambiguity remains.
- 0: Contradictions remain.

## GPT-5 Specificity
- 2: `reasoning_effort`, `verbosity`, persistence, tool preambles, or coding rules are selected when relevant.
- 1: GPT-5 guidance is present but generic.
- 0: No GPT-5 adaptation.

## Brief Alignment
- 2: All brief requirements are represented in the final prompt and output format.
- 1: Minor requirement missing or weakly represented.
- 0: Major requirement missing.

## Production Readiness
- 2: Prompt has clear goal, role, workflow, constraints, output format, validation, and safe failure behavior.
- 1: Usable but needs polishing.
- 0: Not production-ready.

## Pass Rule
- 9-10: Excellent.
- 7-8: Good, but revise if production-critical.
- 5-6: Medium; create v2.
- 0-4: Rewrite.
