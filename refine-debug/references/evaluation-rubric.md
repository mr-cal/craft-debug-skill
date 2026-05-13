# Evaluation Rubric for craft-debug Skills

Use this rubric when scoring each test case response during Step 2 of the `refine-debug` workflow.

---

## Scoring Scale

| Score | Label   | Meaning |
|-------|---------|---------|
| 2     | PASS    | Skill fully covers the scenario. Agent can resolve the issue without needing external information. |
| 1     | PARTIAL | Skill partially covers the scenario. Agent can make progress but is missing one key step or detail. |
| 0     | FAIL    | Skill does not cover the scenario. Agent cannot help, or actively gives wrong guidance. |

---

## Per-Dimension Criteria

Score each test case on **three dimensions**, then take the minimum as the overall score.

### Dimension 1: Routing (Does the skill trigger?)

- **2 (PASS):** The skill's `description` WHEN clause contains a keyword that matches the scenario's query language.
- **1 (PARTIAL):** The skill body covers the scenario but the WHEN clause is missing the trigger phrase; a human would find it by reading carefully.
- **0 (FAIL):** The skill would not be routed to this scenario at all.

### Dimension 2: Diagnosis (Does the skill identify the problem?)

- **2 (PASS):** Skill explicitly names the error type, the lifecycle step it occurs in, and the root cause.
- **1 (PARTIAL):** Skill identifies the lifecycle step but not the root cause, or vice versa.
- **0 (FAIL):** Skill provides no diagnosis path for this error.

### Dimension 3: Remediation (Does the skill fix the problem?)

- **2 (PASS):** Skill provides a concrete, actionable fix with exact commands or YAML snippets.
- **1 (PARTIAL):** Skill points in the right direction but the agent would need to guess at specifics.
- **0 (FAIL):** Skill provides no remediation, or the remediation is incorrect/inapplicable.

---

## Overall Score per Test Case

```
overall = min(routing_score, diagnosis_score, remediation_score)
```

| Overall | Verdict  |
|---------|----------|
| 2       | PASS     |
| 1       | PARTIAL  |
| 0       | FAIL     |

---

## Suite-Level Thresholds

After scoring all test cases, compute the suite summary:

| Metric                    | Definition |
|---------------------------|------------|
| Pass rate                 | (PASS count) / (total test cases) |
| Partial-or-better rate    | (PASS + PARTIAL count) / (total test cases) |

**Acceptance criteria for a new version:**

- Pass rate ≥ 75% (at least 6 of 8 standard test cases are PASS)
- Partial-or-better rate = 100% (no FAILs remain)
- Every gap found in the previous version that was planned as fixed scores PASS in the new version

If these thresholds are not met, iterate further before finalising the new version.

---

## Gap Classification

When a test case scores PARTIAL or FAIL, classify the gap:

| Category         | When to use |
|------------------|-------------|
| `missing-content` | The scenario has no matching section in the skill |
| `unclear-steps`   | A section exists but commands/YAML are missing or vague |
| `bad-trigger`     | The scenario should route to this skill but the WHEN clause lacks the trigger phrase |
| `spec`            | Frontmatter is missing required fields (`license`, `metadata.version`, WHEN clause, etc.) |

One test case may produce multiple gaps in different categories.
