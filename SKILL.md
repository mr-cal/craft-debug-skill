---
name: craft-debug
description: Use when debugging failing builds of craft applications (snapcraft, charmcraft, rockcraft, debcraft, imagecraft), when a pack/build command errors, or when iterating on a project file to fix build failures.
---

# Debugging Craft App Builds

## Overview

Craft apps (snapcraft, charmcraft, rockcraft, debcraft, imagecraft) share a common build framework. Use this skill to diagnose failures, iterate efficiently, and get to a successful pack.

**Core principle:** Work through the build lifecycle step-by-step, using craft's built-in debug flags to narrow down the failing step, then fix and re-run.

## Quick Reference

Log paths follow `~/.local/state/<app>/log/`. Project files follow `<app>.yaml`, except snapcraft which also checks `snap/snapcraft.yaml`, `.snapcraft.yaml`, and `build-aux/snap/snapcraft.yaml`.

## Build Provider

By default, craft apps launch builds inside an **LXD container** or **Multipass VM**. Users may override this. If the default provider fails or the user mentions a specific provider, ask which one they are using.

**Set the build provider:**
```bash
CRAFT_BUILD_ENVIRONMENT=lxd snapcraft pack
CRAFT_BUILD_ENVIRONMENT=multipass snapcraft pack
```

**Build directly on the host (destructive mode):**
```bash
snapcraft pack --destructive-mode
```

> ⚠️ **Never use `--destructive-mode` unless the user explicitly asks for it.** It modifies the host system directly and bypasses build isolation.

## Project File Schema

Project file schemas are published on [SchemaStore](https://www.schemastore.org/). Use them to validate the project file and check required/optional keys.

| App | Schema URL |
|-----|-----------|
| snapcraft | `https://raw.githubusercontent.com/canonical/snapcraft/main/schema/snapcraft.json` |
| charmcraft | `https://raw.githubusercontent.com/canonical/charmcraft/main/schema/charmcraft.json` |
| rockcraft | `https://raw.githubusercontent.com/canonical/rockcraft/main/schema/rockcraft.json` |

When a YAML validation error is unclear, fetch the schema and check the key's definition.

## Build Lifecycle

All craft apps share this lifecycle (in order):

```
pull → [overlay] → build → stage → prime → pack
```

The **overlay** step (between pull and build) is optional and only present in some apps (e.g. rockcraft). It modifies the base filesystem layer before the build step.

Each step command runs all prior steps automatically:
- `<app> pull [part-name]` — fetch sources
- `<app> overlay [part-name]` — modify base filesystem layer (where supported)
- `<app> build [part-name]` — compile/build
- `<app> stage [part-name]` — collect into staging area
- `<app> prime [part-name]` — prepare final contents
- `<app> pack` — create final artifact

## Debugging Workflow

### 1. Identify the failing step

Run the full pack and read the error carefully:

```bash
snapcraft pack 2>&1 | tee /tmp/craft-build.log
```

The error message names the **step** (pull/build/stage/prime/pack) and **part** that failed.

### 2. Read the detailed log

The last log file contains full output including environment details:

```bash
ls -t ~/.local/state/snapcraft/log/ | head -1 | xargs -I{} cat ~/.local/state/snapcraft/log/{}
```

(Replace `snapcraft` with your app name.)

### 3. Inspect the project file

```bash
cat snapcraft.yaml        # or rockcraft.yaml, charmcraft.yaml, etc.
```

Check:
- `parts:` — names, plugins, source, build-packages, stage-packages
- `base:` — Ubuntu version used for build environment
- `platforms:` — target architectures

### 4. Use debug flags to iterate faster

These flags are available on all lifecycle step commands:

| Flag | When to use |
|------|-------------|
| `--shell` | Drop into a shell BEFORE the failing step |
| `--shell-after` | Drop into a shell AFTER a step completes |
| `--debug` | Drop into a shell automatically ON failure |

**Examples:**

```bash
# Drop into shell before prime (after stage), inspect staging area
snapcraft prime --shell

# Run build and then inspect the build environment
snapcraft build my-part --shell-after

# Run pack; if it fails, drops into a shell at the failure point
snapcraft pack --debug
```

Inside the shell you can:
- Inspect file layout (`ls`, `find`)
- Check environment variables (see below)
- Test missing binaries or libraries
- Edit the project file outside the shell and re-run `snapcraft` inside it

**Key environment variables inside the debug shell:**

| Variable | Points to |
|----------|-----------|
| `$CRAFT_PART_SRC` | Pulled source code |
| `$CRAFT_PART_BUILD` | Build working directory |
| `$CRAFT_PART_INSTALL` | Where built files are installed (staged from here) |
| `$CRAFT_STAGE` | The staging area (all parts combined) |
| `$CRAFT_PRIME` | The prime area (final artifact contents) |

### 5. Build or clean specific parts

To speed up iteration, target specific parts instead of rebuilding everything:

```bash
# Rebuild only the failing part
snapcraft build my-part

# Clean only a specific part and rebuild it
snapcraft clean my-part
snapcraft build my-part

# Clean everything and start fresh
snapcraft clean
```

### 6. Fix and re-run

After editing `snapcraft.yaml` (or equivalent), re-run from the failing step:

```bash
snapcraft pack   # or the specific failing step
```

### 7. Final verification

Once the build succeeds, do a clean rebuild to catch any state left over from debugging iterations:

```bash
snapcraft clean
snapcraft pack
```

> ⚠️ **Only do this when confident the build is working.** On large projects, a full clean can take hours to re-download dependencies and recompile from scratch. For quick iteration, target specific parts instead.

### YAML validation errors (before any build)

```
Issues while validating snapcraft.yaml: 'version' is a required property
```

**Fix:** Check required keys. `version` is required unless using `adopt-info`. Validate YAML syntax.

### Missing build dependency (build step)

```
Package libfoo-dev was not found in the pkg-config search path
```

**Fix:** Add to `build-packages` in the failing part:
```yaml
parts:
  my-part:
    build-packages:
      - libfoo-dev
```

### Missing runtime library (stage/prime step)

```
Unable to find library: libfoo.so.1
```

**Fix:** Add to `stage-packages` in the failing part:
```yaml
parts:
  my-part:
    stage-packages:
      - libfoo1
```

### `override-build` / scriptlet command failure

```
+ not-a-real-command
not-a-real-command: command not found
```

**Fix:** Check the `override-build`, `override-pull`, or `override-prime` scriptlet in the part. The failing command must be installed (add it to `build-packages`) or corrected.

### adopt-info missing parse-info (prime step)

```
Failed to generate snap metadata: 'adopt-info' refers to part 'mypart', but that part is lacking the 'parse-info' property
```

**Fix:** Add `parse-info` to the part, or use `craftctl set-version` in an override scriptlet.

### Linter warnings (prime step)

Some apps run linters at the prime step. Warnings look like:

```
Lint warnings:
- <linter>: <file>: <issue>
```

**Fix options:**
- Address the underlying issue (e.g. add missing package, remove unused library)
- Suppress a false positive with `lint.ignore`:
```yaml
lint:
  ignore:
    - library: libfoo.so.1
```

### Parts lifecycle ordering

If part A needs files from part B during build, use `after`:
```yaml
parts:
  part-a:
    after:
      - part-b
```

## Speeding Up Iterations

1. **Target the failing part:** `snapcraft build failing-part` not `snapcraft pack`
2. **Use `--shell`/`--debug`** to inspect environment without full rebuilds
3. **Clean only what changed:** `snapcraft clean failing-part` to invalidate just one part
4. **Fix YAML errors first** — the app validates the project file before any build steps

## App-Specific Notes

| App | Output artifact |
|-----|----------------|
| snapcraft | `.snap` |
| charmcraft | `.charm` |
| rockcraft | `.rock` (OCI image archive) |
| debcraft | `.deb` |
| imagecraft | Ubuntu image |

## Example Iteration Session

```bash
# 1. See what's failing
snapcraft pack --debug
# (shell opens at failure point)

# 2. Inside the shell: inspect
ls $CRAFT_PART_BUILD
find $CRAFT_STAGE -name "*.so*"

# 3. Exit shell, fix snapcraft.yaml
# (edit in another terminal)

# 4. Clean just the failing part
snapcraft clean my-part

# 5. Re-run
snapcraft pack
```
