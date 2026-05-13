# Test Cases for craft-debug Skills

This file defines the standard test suite used by the `refine-debug` skill.
Run every test case in order. Do not skip any.

---

## How to Run a Test Case

For each test case:
1. Read the **Scenario** (the user query).
2. Walk through the craft-debug skill as if you are the agent responding.
3. Identify which section(s) of the skill you used.
4. Check whether the skill provided enough guidance to reach the **Expected Outcome**.
5. Score using the evaluation rubric in `references/evaluation-rubric.md`.

---

## TC-01: Missing build-package (baseline)

**Scenario:** A user runs `snapcraft pack` and sees:

```
Package libssl-dev was not found in the pkg-config search path
```

**Expected Outcome:**
- Agent identifies this as a build-step failure.
- Agent instructs user to add `libssl-dev` to `build-packages` in the failing part.
- Agent provides the corrected YAML snippet.

**Pass Criteria:** Skill's "Missing build dependency" error pattern covers this exactly.

---

## TC-02: CI / non-interactive environment

**Scenario:** A user says:

> My snapcraft pack fails in GitHub Actions. The build log just shows the error but I
> can't drop into a shell. How do I debug without an interactive terminal?

**Expected Outcome:**
- Agent does NOT recommend `--shell`, `--shell-after`, or `--debug` (those require a TTY).
- Agent recommends `--verbosity debug` to get verbose log output without a shell.
- Agent shows how to read the log file written to `~/.local/state/snapcraft/log/`.

**Pass Criteria:** Skill has explicit CI/non-interactive guidance and mentions `--verbosity debug`.

---

## TC-03: Build provider not configured

**Scenario:** A user runs `snapcraft pack` and sees:

```
error: LXD is not installed
```

or:

```
Failed to start Multipass instance
```

**Expected Outcome:**
- Agent explains that snapcraft uses LXD or Multipass by default as the build provider.
- Agent provides at least one of: how to install LXD, how to switch to `--destructive-mode`,
  or how to set `SNAPCRAFT_BUILD_ENVIRONMENT`.

**Pass Criteria:** Skill has a build-provider troubleshooting section.

---

## TC-04: Rockcraft chisel slice not found

**Scenario:** A user runs `rockcraft pack` and sees:

```
chisel: cannot find any package providing /usr/bin/python3
```

**Expected Outcome:**
- Agent identifies this as a rockcraft-specific chisel/slice error.
- Agent explains that rockcraft uses chisel for fine-grained package slices.
- Agent instructs user to add the correct chisel slice (e.g. `python3_bins`) instead of a
  full package name in the `stage-packages` list.

**Pass Criteria:** Skill has rockcraft-specific chisel/slice guidance.

---

## TC-05: Stale build state persists after YAML edit

**Scenario:** A user edited their `snapcraft.yaml` to fix an error, but re-running
`snapcraft pack` produces exactly the same error as before.

**Expected Outcome:**
- Agent identifies this as a cached/stale build state issue.
- Agent instructs user to run `snapcraft clean <part-name>` or `snapcraft clean` to
  invalidate the cache.
- Agent mentions `snapcraft clean --purge` or removing the `.snapcraft/` directory as a
  last resort for a full reset.

**Pass Criteria:** Skill explains both targeted clean (`clean <part>`) and full purge.

---

## TC-06: Charmcraft Python venv failure

**Scenario:** A user runs `charmcraft pack` and sees:

```
Failed to create the target venv: ...
```

or:

```
ERROR - Cannot fetch libs: <dependency conflict>
```

**Expected Outcome:**
- Agent recognises this as a charmcraft-specific Python dependency or venv issue.
- Agent provides at least one concrete remediation step (e.g. check `requirements.txt`,
  check `charmcraft.yaml` `parts.charm.python-packages`, clean and rebuild).

**Pass Criteria:** Skill has a charmcraft-specific Python/venv error section.

---

## TC-07: YAML validation error (spec compliance)

**Scenario:** A user sees:

```
Issues while validating snapcraft.yaml: 'version' is a required property
```

**Expected Outcome:**
- Agent identifies this as a YAML validation error (before any build step runs).
- Agent explains that `version` is required unless using `adopt-info`.
- Agent shows the minimal fix.

**Pass Criteria:** Skill's "YAML validation errors" section covers this exactly.

---

## TC-08: Library linter false positive (prime step)

**Scenario:** The build fails (or produces warnings treated as errors) at the prime step:

```
Lint warnings:
- library: libfoo.so.1: unused library
```

**Expected Outcome:**
- Agent explains unused-library linter warnings.
- Agent provides both fix options: remove from `stage-packages` or suppress with `lint.ignore`.

**Pass Criteria:** Skill's "Library linter warnings" section covers both options.
