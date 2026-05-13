---
name: refine-debug
description: >
  Refines an existing craft-debug skill by running it against a structured test suite,
  evaluating the results, identifying gaps, and producing a new versioned skill file
  (craft-debug-vX). Applies an iterative evaluation loop: test → score → identify gaps →
  improve → re-test. Produces only a new versioned skill, never overwrites the previous one.
  WHEN: refine craft-debug skill, improve craft-debug, iterate on debug skill, test skill quality,
  evaluate skill against test cases, create craft-debug-v2, create next version of craft-debug,
  skill regression testing, skill iteration, debug skill improvement.
license: Apache-2.0
metadata:
  author: some-bot-e
  version: "1.0.0"
  summary: Evaluates a craft-debug skill version against test cases and produces a refined craft-debug-vX skill.
  tags:
    - craft
    - debugging
    - skill-refinement
    - meta
---

# Refine Debug

## Overview

Refines an existing `craft-debug` skill version by running it against a structured set of
test scenarios, scoring the results, identifying gaps, and writing a new versioned
`craft-debug-vN` skill that addresses those gaps. **Never overwrites a previous version.**

## Workflow

### Step 1 — Identify the current skill version

All skill versions live as sibling directories next to `refine-debug/` in the same repo:

```
craft-debug-skill/
├── SKILL.md              ← v1 (the original)
├── refine-debug/         ← this skill
├── craft-debug-v2/       ← refined versions
└── …
```

To find the latest version, list sibling directories:

```bash
ls "$(dirname "$PWD")"
```

### Step 2 — Run the test suite

Simulate the agent using the skill for each test case in `references/test-cases.md`.
For each test case:

1. Read the scenario and expected behaviour.
2. Walk through the skill's instructions as if you were the agent responding to that query.
3. Score the response using `references/evaluation-rubric.md`.
4. Record the result (PASS / PARTIAL / FAIL) and any gap found.

**Do not skip test cases.** Run every test in the suite.

### Step 3 — Compile gaps

After all test cases, list every gap found:

| Gap ID | Test case | Symptom | Category |
|--------|-----------|---------|----------|
| G1     | …         | …       | missing-content / unclear-steps / bad-trigger / spec |

Categories:
- `missing-content` — a common scenario has no matching guidance
- `unclear-steps` — instructions exist but are ambiguous or incomplete
- `bad-trigger` — the skill description wouldn't route to this scenario
- `spec` — frontmatter is non-compliant (missing fields, bad format)

### Step 4 — Plan the improvements

For each gap, determine the fix:

- `missing-content` → add a new section or extend an existing one
- `unclear-steps` → rewrite the affected step with concrete commands/examples
- `bad-trigger` → update the `description` WHEN clause to add the missing trigger phrase
- `spec` → fix the frontmatter field

### Step 5 — Scaffold the new version

Determine the next version number (e.g., if current is `craft-debug-v2`, create `craft-debug-v3`).

All versions live as subdirectories **alongside this skill** in the same repository root:

```
craft-debug-skill/
├── SKILL.md              ← original v1 skill
├── refine-debug/         ← this skill
├── craft-debug-v2/       ← first refined version
├── craft-debug-v3/       ← next refined version
└── …
```

Scaffold into that directory:

```bash
python3 /root/.agents/skills/generate-agent-skills/scripts/scaffold_skill.py \
  --name craft-debug-vN \
  --output-dir "$(dirname "$(dirname "$0")")"
```

If the scaffold script is not available, create the directory and SKILL.md directly at
`<repo-root>/craft-debug-vN/SKILL.md`.

**Never place the new version inside the `refine-debug/` directory itself.**

### Step 6 — Write the refined skill

Copy the previous version's SKILL.md as a starting point, then apply every planned fix.
Follow these rules:
- Preserve all passing content from the previous version.
- Add new sections immediately after the most relevant existing section.
- Keep SKILL.md under 500 lines; move large tables or examples to `references/`.
- Update `metadata.version` to the new version number.

### Step 7 — Validate and re-test

Run the validator:

```bash
python3 /root/.agents/skills/generate-agent-skills/scripts/validate_skill.py \
  --path <path-to-new-skill>
```

Fix any reported errors. Then re-run the full test suite against the new skill and confirm
every previously failing test now passes (or is explicitly deferred with a rationale).

### Step 8 — Summarise the changes

Output a brief changelog:

```
craft-debug-vN — Changes from vN-1
-----------------------------------
Fixed:
  - G1: <description>
  - G2: <description>

Still known gaps (deferred):
  - <description> — reason: <rationale>
```

## References

### references/test-cases.md

Standard test case suite for craft-debug skills. Read this file before Step 2.

### references/evaluation-rubric.md

Scoring criteria for each test case response. Read this before Step 2.
