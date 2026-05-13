---
name: craft-debug
description: Use when debugging failing builds of craft applications (snapcraft, charmcraft, rockcraft, debcraft, imagecraft), when a pack/build command errors, or when iterating on a project file to fix build failures.
metadata:
  author: "@canonical/starcraft"
  version: "0.2"
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

Each app's full documentation is at:
- snapcraft: `https://documentation.ubuntu.com/snapcraft`
- rockcraft: `https://documentation.ubuntu.com/rockcraft`
- charmcraft: `https://documentation.ubuntu.com/charmcraft`

For other apps, try `https://documentation.ubuntu.com/<app>`. Fetch pages from the docs site when you need deeper detail on a behaviour, option, or plugin.

## Gotchas

- **The debug shell is inside the build environment**, not on the host. `--shell`, `--shell-after`, and `--debug` open a shell inside the LXD container or Multipass VM. Edit the project YAML on the host in a separate terminal, then re-run the craft app from inside the shell.
- **`<app> clean` with no arguments cleans ALL parts.** On large projects this can mean hours to re-download and recompile. Always prefer `<app> clean <part-name>` during iteration.
- **Build state is cached between runs.** A part that succeeded previously won't re-run unless cleaned. This is usually good but can leave stale state during debugging. Do a final `clean` + `pack` once the build is confirmed working.
- **The overlay step is only present in some apps** (e.g. rockcraft). Running `snapcraft overlay` will error.
- **Never use `--destructive-mode` unless the user explicitly asks.** It modifies the host system directly and bypasses build isolation.
- **Fix craft config, not source code.** Resolve failures by editing the craft YAML or craft-specific assets (e.g. `snap/hooks/`). Do **not** modify source files — this includes application source, build system files (e.g. `CMakeLists.txt`, `Makefile`, `setup.py`, `pyproject.toml`), and any file committed to the upstream repo. If the only path forward is a source change (i.e. the project is genuinely broken outside any craft context), tell the user what you found and **ask before making any edits**.
- **Exhaust craft YAML options before considering source changes.** The craft YAML has many levers — `build-packages`, `stage-packages`, `build-snaps`, additional parts (which can pull from any source type), `cmake-parameters`, `override-pull`/`override-build`/`override-prime` scriptlets, and `after` for ordering. When a build fails, work through these options systematically before concluding that a source file must change.
- **Prep the build environment** If you need to build or add dependencies to get a part to work, consider using the `build-environment` key, other part keys, and plugin-specific keys that let the a part consume things that were built by the dependency parts. Parts should install to `$CRAFT_PART_INSTALL`, such that subsequent parts can consume their output.

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

Validation errors are raised for missing required fields (e.g. `version`, `base`) and for invalid field values (e.g. a license string that is not a valid SPDX identifier). If the expected format is unclear, look up the project YAML reference for the app:
- snapcraft: `https://documentation.ubuntu.com/snapcraft/stable/reference/snapcraft-yaml/`
- rockcraft: `https://documentation.ubuntu.com/rockcraft/stable/reference/rockcraft-yaml/`
- charmcraft: `https://documentation.ubuntu.com/charmcraft/stable/reference/files/charmcraft-yaml-file/`

For other apps, look for a similar reference page under the app's documentation site — the slug may differ.

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
