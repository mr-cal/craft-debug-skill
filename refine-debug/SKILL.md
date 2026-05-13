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
  author: mr-cal
  version: "1.1.0"
  summary: Evaluates a craft-debug skill version against failing snaps and query examples, then produces a refined craft-debug-vX skill.
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
├── eval/                 ← test data
├── craft-debug-v2/       ← refined versions
└── …
```

To find the latest version, list sibling directories:

```bash
ls "$(dirname "$PWD")"
```

Determine the current version number (from `metadata.version` in the latest skill's
frontmatter). The output of this run will be `craft-debug-v(N+1)`.

### Step 2 — Load the test cases

If the user specifies a test case directory, use that. Otherwise default to
`eval/failing-snaps/` in the repo root.

**Directory structure:**

```
eval/failing-snaps/
├── README.md
├── <snap-name>/
│   ├── snap/
│   │   └── snapcraft.yaml   ← project file under test
│   └── src/                 ← optional local source
└── …
```

1. List entries:
   ```bash
   ls eval/failing-snaps/
   ```
2. For each entry (skip `README.md`), read `<entry>/snap/snapcraft.yaml`.
3. Inspect the YAML to infer the **intended failure mode** — look for:
   - Missing required fields (e.g. no `version`, no `base`)
   - Scriptlets designed to fail (`override-pull: exit 1`, `craftctl` misuse)
   - Invalid field values (e.g. `license: boo-license`)
   - Packages, plugins, or sources that would fail at a specific lifecycle step
   - Platform/architecture constraints that cannot be satisfied
4. Write a one-line failure summary per snap:
   ```
   <snap-name>: <lifecycle step that fails> — <root cause>
   ```

### Step 3 — Evaluate routing with query examples

The repo includes example queries at `eval/train_queries.json` and `eval/val_queries.json`.
Each entry has a `query` string and a `should_trigger` boolean.

For each query, check whether the skill's `description` WHEN clause would route to this
skill:
- **True positive:** `should_trigger: true` and the WHEN clause matches → correct
- **False negative:** `should_trigger: true` but the WHEN clause misses it → gap (`bad-trigger`)
- **True negative:** `should_trigger: false` and the WHEN clause does not match → correct
- **False positive:** `should_trigger: false` but the WHEN clause would match → over-triggering

Record all false negatives and false positives as routing gaps.

### Step 4 — Score the failing snaps

For each snap from Step 2, simulate the agent response:

1. Construct the user query: *"I'm running `snapcraft pack` on `<snap-name>` and it fails with `<inferred error>`. Help me debug it."*
2. Walk through the skill's instructions as if you are the agent responding, using the YAML as context.
3. Score using `references/evaluation-rubric.md`.
4. Record the result (PASS / PARTIAL / FAIL) and any gap found.

**Do not skip any snaps.**

### Step 5 — Compile gaps

After all test cases, list every gap found:

| Gap ID | Source | Symptom | Category |
|--------|--------|---------|----------|
| G1     | `exit1` snap | override-pull scriptlet failure not covered | `missing-content` |
| G2     | train query #8 | "CI pipeline failing" not routed | `bad-trigger` |

Categories:
- `missing-content` — a common scenario has no matching guidance
- `unclear-steps` — instructions exist but are ambiguous or incomplete
- `bad-trigger` — the skill description wouldn't route to this scenario
- `spec` — frontmatter is non-compliant (missing fields, bad format)

### Step 6 — Plan the improvements

For each gap, determine the fix:

- `missing-content` → add a new section or extend an existing one
- `unclear-steps` → rewrite the affected step with concrete commands/examples
- `bad-trigger` → update the `description` WHEN clause to add the missing trigger phrase
- `spec` → fix the frontmatter field

### Step 7 — Scaffold the new version

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
  --output-dir "$(dirname "$PWD")"
```

If the scaffold script is not available, create the directory and SKILL.md directly at
`<repo-root>/craft-debug-vN/SKILL.md`.

**Never place the new version inside the `refine-debug/` directory itself.**

### Step 8 — Write the refined skill

Copy the previous version's SKILL.md as a starting point, then apply every planned fix.
Follow these rules:
- Preserve all passing content from the previous version.
- Add new sections immediately after the most relevant existing section.
- Keep SKILL.md under 500 lines; move large tables or examples to `references/`.
- Update `metadata.version` to the new version number.

### Step 9 — Validate and re-test

Run the validator:

```bash
python3 /root/.agents/skills/generate-agent-skills/scripts/validate_skill.py \
  --path <path-to-new-skill>
```

Fix any reported errors. Then re-run the full test suite (Steps 3–4) against the new
skill and confirm every previously failing test now passes (or is explicitly deferred
with a rationale).

### Step 10 — Summarise the changes

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

### references/evaluation-rubric.md

Scoring criteria for each test case response. Read this before Step 4.


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

### Step 2 — Load the test cases

If the user specifies a test case directory, use that. Otherwise default to the
`failing-snaps/` directory that lives alongside this skill in the repo root.

**Directory structure of `failing-snaps/`:**

```
failing-snaps/
├── README.md
├── <snap-name>/
│   └── snap/
│       └── snapcraft.yaml   ← the project file under test
│   └── src/                 ← optional local source
└── …
```

**To load the test cases:**

1. List all entries in the test case directory:
   ```bash
   ls failing-snaps/
   ```
2. For each entry (skip `README.md`), read `<entry>/snap/snapcraft.yaml`.
3. Inspect the YAML to infer the **intended failure mode** — look for:
   - Missing required fields (e.g. no `version`, no `base`)
   - Scriptlets that are designed to fail (`override-pull: exit 1`, `craftctl` misuse)
   - Packages, plugins, or source references that would fail at a specific lifecycle step
   - Platform/architecture constraints that can't be satisfied
   - Invalid field values (e.g. `license: boo-license`)
4. For each snap, write a one-line failure summary:
   ```
   <snap-name>: <step that fails> — <root cause>
   ```

**Do not skip any entries.** Use all snaps in the directory as test cases.

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
