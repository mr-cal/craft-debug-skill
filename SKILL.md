---
name: craft-debug
description: Use when debugging failing builds of craft applications (snapcraft, charmcraft, rockcraft, debcraft, imagecraft), when a pack/build command errors, or when iterating on a project file to fix build failures.
metadata:
  author: "@canonical/starcraft"
  version: "0.1"
---

# Debugging Craft App Builds

## Overview

Craft apps (snapcraft, charmcraft, rockcraft, debcraft, imagecraft) share a common build framework. Work through the build lifecycle step-by-step, using craft's built-in debug flags to narrow down the failing step, then fix and re-run.

## Quick Reference

Log paths follow `~/.local/state/<app>/log/`. Project files follow `<app>.yaml`, except snapcraft which also checks `snap/snapcraft.yaml`, `.snapcraft.yaml`, and `build-aux/snap/snapcraft.yaml`.

| App | Output artifact |
|-----|----------------|
| snapcraft | `.snap` |
| charmcraft | `.charm` |
| rockcraft | `.rock` (OCI image archive) |
| debcraft | `.deb` |
| imagecraft | Ubuntu image |

## Gotchas

- **The debug shell is inside the build environment**, not on the host. `--shell`, `--shell-after`, and `--debug` open a shell inside the LXD container or Multipass VM. Edit the project YAML on the host in a separate terminal, then re-run the craft app from inside the shell.
- **`<app> clean` with no arguments cleans ALL parts.** On large projects this can mean hours to re-download and recompile. Always prefer `<app> clean <part-name>` during iteration.
- **Build state is cached between runs.** A part that succeeded previously won't re-run unless cleaned. This is usually good but can leave stale state during debugging. Do a final `clean` + `pack` once the build is confirmed working.
- **The overlay step is only present in some apps** (e.g. rockcraft). Running `snapcraft overlay` will error.
- **Never use `--destructive-mode` unless the user explicitly asks.** It modifies the host system directly and bypasses build isolation.

## Build Provider

By default, craft apps launch builds inside an **LXD container** or **Multipass VM**. If the default provider fails or the build environment won't start, ask the user which provider they are using.

Override with:
```bash
CRAFT_BUILD_ENVIRONMENT=lxd snapcraft pack
CRAFT_BUILD_ENVIRONMENT=multipass snapcraft pack
```

## Build Lifecycle

```
pull → [overlay] → build → stage → prime → pack
```

Each step command runs all prior steps automatically. You can target a specific part:

```bash
<app> pull [part-name]
<app> overlay [part-name]   # rockcraft only
<app> build [part-name]
<app> stage [part-name]
<app> prime [part-name]
<app> pack
```

## Debugging Workflow

### 1. Identify the failing step

```bash
<app> pack 2>&1 | tee /tmp/craft-build.log
```

The error names the **step** and **part** that failed.

### 2. Read the detailed log

```bash
ls -t ~/.local/state/<app>/log/ | head -1 | xargs -I{} cat ~/.local/state/<app>/log/{}
```

### 3. Use debug flags to inspect the environment

| Flag | Effect |
|------|--------|
| `--shell` | Shell BEFORE the failing step |
| `--shell-after` | Shell AFTER a step completes |
| `--debug` | Shell automatically ON failure |

```bash
# Shell opens at failure point — inspect from inside the build environment
<app> pack --debug

# Shell before prime — inspect the staging area
<app> prime --shell

# Shell after build — check what was installed
<app> build my-part --shell-after
```

**Inside the shell:**

| Variable | Points to |
|----------|-----------|
| `$CRAFT_PART_SRC` | Pulled source code |
| `$CRAFT_PART_BUILD` | Build working directory |
| `$CRAFT_PART_INSTALL` | Files installed by this part |
| `$CRAFT_STAGE` | Staging area (all parts combined) |
| `$CRAFT_PRIME` | Prime area (final artifact contents) |

### 4. Iterate on a specific part

```bash
<app> clean my-part
<app> build my-part      # or stage/prime as needed
```

### 5. Final verification

Once the build succeeds, do a clean rebuild to flush any stale state from debugging:

```bash
<app> clean && <app> pack
```

> Only do this when confident the build is working — on large projects a full clean can take hours.

## Common Error Patterns

### YAML validation error

```
Issues while validating snapcraft.yaml: 'version' is a required property
```

`version` is required unless using `adopt-info`. If the key/value is unclear, fetch the schema:
- snapcraft: `https://raw.githubusercontent.com/canonical/snapcraft/main/schema/snapcraft.json`
- charmcraft: `https://raw.githubusercontent.com/canonical/charmcraft/main/schema/charmcraft.json`
- rockcraft: `https://raw.githubusercontent.com/canonical/rockcraft/main/schema/rockcraft.json`

### Missing build dependency

```
Package libfoo-dev was not found in the pkg-config search path
```

Add to `build-packages` in the failing part:
```yaml
parts:
  my-part:
    build-packages:
      - libfoo-dev
```

### Missing runtime library

```
Unable to find library: libfoo.so.1
```

Add to `stage-packages` in the failing part:
```yaml
parts:
  my-part:
    stage-packages:
      - libfoo1
```

### Scriptlet command not found

```
+ not-a-real-command
not-a-real-command: command not found
```

The command in `override-build`, `override-pull`, or `override-prime` is missing. Add it to `build-packages` or fix the scriptlet.

### adopt-info missing parse-info

```
Failed to generate snap metadata: 'adopt-info' refers to part 'mypart', but that part is lacking the 'parse-info' property
```

Add `parse-info` to the part, or set version explicitly with `craftctl set-version` in an override scriptlet.

### Linter warnings (prime step)

```
Lint warnings:
- <linter>: <file>: <issue>
```

Either fix the underlying issue or suppress a false positive:
```yaml
lint:
  ignore:
    - library: libfoo.so.1
```

### Part ordering — file not found at build time

If a part needs files from another part during build, use `after`:
```yaml
parts:
  part-a:
    after:
      - part-b
```

## Example Session

```bash
# 1. Run with --debug so a shell opens on failure
snapcraft pack --debug

# 2. Inside the shell (you are now inside LXD/VM):
ls $CRAFT_PART_BUILD
find $CRAFT_STAGE -name "*.so*"

# 3. Exit shell; edit snapcraft.yaml on the HOST in another terminal

# 4. Clean only the failing part and re-run
snapcraft clean my-part && snapcraft pack

# 5. When working: final clean verification
snapcraft clean && snapcraft pack
```
