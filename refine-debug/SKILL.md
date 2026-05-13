---
name: refine-debug
description: >
  Refines the craft-debug skill by running it against a structured test suite,
  evaluating the results, identifying gaps, improving the skill content, and overwriting
  the original craft-debug skill (SKILL.md) with the improved version. Applies an
  iterative evaluation loop: test → score → identify gaps → improve → re-test.
  WHEN: refine craft-debug skill, improve craft-debug, iterate on debug skill, test skill quality,
  evaluate skill against test cases, fix failing craft-debug tests, update craft-debug skill,
  skill regression testing, skill iteration, debug skill improvement.
license: Apache-2.0
metadata:
  author: some-bot-e
  version: "1.2.0"
  summary: Evaluates the craft-debug skill against failing snaps and query examples, then overwrites the original craft-debug SKILL.md with the improved version.
  tags:
    - craft
    - debugging
    - skill-refinement
    - meta
---

# Refine Debug

## Overview

Refines the `craft-debug` skill by running it against a structured set of test scenarios,
scoring the results, identifying gaps, and **overwriting the original `craft-debug` skill**
(`SKILL.md` at the repository root) with an improved version that addresses those gaps.

## Workflow

### Step 1 — Load the current skill

Read the current `craft-debug` skill from the repository root:

```
craft-debug-skill/
├── SKILL.md              ← craft-debug skill (will be overwritten)
├── refine-debug/         ← this skill
└── eval/                 ← test data
```

```bash
cat SKILL.md
```

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

**Do not skip any snaps.**

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

### Step 7 — Write the improved skill

Use the current `SKILL.md` content as the starting point. Apply every planned fix and
**overwrite** the original `craft-debug` skill at the repository root (`SKILL.md`).

Follow these rules:
- Preserve all passing content from the current skill.
- Add new sections immediately after the most relevant existing section.
- Keep SKILL.md under 500 lines; move large tables or examples to `references/`.
- Increment `metadata.version` in the frontmatter.

**Do not create a new versioned directory.** Write the result directly to `SKILL.md`.

### Step 8 — Validate and re-test

Run the validator:

```bash
python3 /root/.agents/skills/generate-agent-skills/scripts/validate_skill.py \
  --path .
```

Fix any reported errors. Then re-run the full test suite (Steps 3–4) against the updated
skill and confirm every previously failing test now passes (or is explicitly deferred
with a rationale).

### Step 9 — Summarise the changes

Output a brief changelog:

```
craft-debug — Changes in this refinement
-----------------------------------------
Fixed:
  - G1: <description>
  - G2: <description>

Still known gaps (deferred):
  - <description> — reason: <rationale>
```

## References

### references/evaluation-rubric.md

Scoring criteria for each test case response. Read this before Step 4.
