# Craft Build Debugger

An [agent skill](https://agentskills.io) for diagnosing and fixing failing snapcraft, charmcraft, and rockcraft builds.

## What it does

When a craft build fails, this skill guides the agent to:

- Find and read the relevant log file
- Use craft's built-in debug flags (`--shell`, `--shell-after`, `--debug`) to drop into the build environment and inspect state
- Iterate efficiently by targeting specific parts instead of rebuilding everything
- Diagnose common error patterns (missing packages, scriptlet failures, linter warnings, YAML validation errors)
- Understand the build provider (LXD/Multipass) and how to override it

## Installation

Copy `SKILL.md` to your agent's skills directory:

```bash
# For Claude Code
cp SKILL.md ~/.claude/skills/craft-debug/SKILL.md

# For Codex / GitHub Copilot CLI
cp SKILL.md ~/.agents/skills/craft-debug/SKILL.md
```

## Contents

```
SKILL.md          # The skill
eval/
  train_queries.json   # Training eval queries for description testing
  val_queries.json     # Validation eval queries
```

## Eval queries

The `eval/` directory contains trigger eval queries following the [optimizing descriptions](https://agentskills.io/skill-creation/optimizing-descriptions) methodology. Use them to verify the skill's description triggers correctly after any edits.

All 7 sampled queries passed at time of writing (4 train, 3 validation).
