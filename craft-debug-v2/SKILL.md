---
name: craft-debug-v2
description: >
  Use when debugging failing builds of craft applications (snapcraft, charmcraft, rockcraft,
  debcraft, imagecraft), when a pack/build command errors, when iterating on a project file
  to fix build failures, when a scriptlet fails or exits non-zero, when snapcraftctl or
  craftctl errors appear, or when architecture/platform constraints are not met.
  WHEN: snapcraft failing, charmcraft build error, rockcraft pack error, debcraft build
  failing, imagecraft error, snap build debug, override-build failing, override-pull
  failing, scriptlet exit 1, snapcraftctl error, craftctl error, platform mismatch,
  architecture mismatch, build-on no match, build-for no match, YAML validation error,
  invalid license field, missing build dependency, missing runtime library, LXD failing,
  Multipass failing, linter warnings, adopt-info parse-info, content interface provider
  not found, invalid UTF-8 build output, python2 unavailable.
license: "Apache-2.0"
metadata:
  author: "@canonical/starcraft"
  version: "2.0.0"
  summary: "Debug failing snapcraft/charmcraft/rockcraft/debcraft/imagecraft builds: YAML errors, scriptlet failures, platform mismatches, missing dependencies, and more."
  tags:
    - craft
    - snapcraft
    - debugging
    - build
---

# Debugging Craft App Builds

## Overview

Craft apps (snapcraft, charmcraft, rockcraft, debcraft, imagecraft) share a common build
framework. Work through the build lifecycle step-by-step, using craft's built-in debug
flags to narrow down the failing step, then fix and re-run.

## Quick Reference

Log paths follow `~/.local/state/<app>/log/`. Project files follow `<app>.yaml`, except
snapcraft which also checks `snap/snapcraft.yaml`, `.snapcraft.yaml`, and
`build-aux/snap/snapcraft.yaml`.

| App | Output artifact |
|-----|----------------|
| snapcraft | `.snap` |
| charmcraft | `.charm` |
| rockcraft | `.rock` (OCI image archive) |
| debcraft | `.deb` |
| imagecraft | Ubuntu image |

## Gotchas

- **The debug shell is inside the build environment**, not on the host. `--shell`,
  `--shell-after`, and `--debug` open a shell inside the LXD container or Multipass VM.
  Edit the project YAML on the host in a separate terminal, then re-run from inside the shell.
- **`<app> clean` with no arguments cleans ALL parts.** Always prefer
  `<app> clean <part-name>` during iteration.
- **Build state is cached between runs.** Do a final `clean` + `pack` once confirmed working.
- **The overlay step is only present in some apps** (e.g. rockcraft). Running
  `snapcraft overlay` will error.
- **Never use `--destructive-mode` unless the user explicitly asks.** It modifies the host
  system directly and bypasses build isolation.

## Build Provider

By default, craft apps launch builds inside an **LXD container** or **Multipass VM**. If
the provider fails or won't start, ask the user which provider they are using.

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
<app> pack --debug
<app> prime --shell
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
<app> build my-part
```

### 5. Final verification

```bash
<app> clean && <app> pack
```

> Only do this when confident the build is working — on large projects a full clean can
> take hours.

## Common Error Patterns

### YAML validation error

```
Issues while validating snapcraft.yaml: 'version' is a required property
```

`version` is required unless using `adopt-info`. If the key/value is unclear, fetch the
schema:
- snapcraft: `https://raw.githubusercontent.com/canonical/snapcraft/main/schema/snapcraft.json`
- charmcraft: `https://raw.githubusercontent.com/canonical/charmcraft/main/schema/charmcraft.json`
- rockcraft: `https://raw.githubusercontent.com/canonical/rockcraft/main/schema/rockcraft.json`

#### Invalid SPDX license identifier

```
Issues while validating snapcraft.yaml: 'boo-license' is not a valid SPDX license
```

The `license` field must be a valid [SPDX expression](https://spdx.org/licenses/). Common
examples: `Apache-2.0`, `MIT`, `GPL-2.0-only`, `GPL-3.0-or-later`, `AGPL-3.0-only`.

```yaml
license: Apache-2.0   # correct
license: boo-license  # wrong — not a valid SPDX identifier
```

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

The command in `override-build`, `override-pull`, or `override-prime` is missing. Add it
to `build-packages` or fix the scriptlet.

### Scriptlet exits with non-zero code

```
Failed to run 'override-pull' for part 'test': Exit code was 1.
```

A scriptlet such as `override-pull`, `override-build`, or `override-prime` explicitly
called `exit <N>` or a command in it returned a non-zero exit code. Debug steps:

1. Add `set -x` at the top of the scriptlet to trace every command:
   ```yaml
   override-pull: |
     set -x
     craftctl default
     my-command
   ```
2. Run the part with `--debug` to get a shell on failure:
   ```bash
   snapcraft pull my-part --debug
   ```
3. Inside the shell, reproduce the failing command manually to see the full error.
4. If the scriptlet intentionally calls `exit 1` (e.g., a placeholder), replace it with
   the real commands or `craftctl default`.

### Legacy scriptlet API: snapcraftctl vs craftctl

Craft apps migrated their scriptlet helper from `snapcraftctl` (core18/core20) to
`craftctl` (core22+). Using the wrong helper causes a build failure.

| Base | Correct helper | Wrong helper |
|------|---------------|--------------|
| core18, core20 | `snapcraftctl` | `craftctl` |
| core22, core24+ | `craftctl` | `snapcraftctl` |

**Migration examples:**

```yaml
# core18/core20 (old)
override-build: |
  snapcraftctl build
  snapcraftctl set-version "1.0"

# core22/core24+ (new)
override-build: |
  craftctl default
  craftctl set version 1.0
```

Key command differences:

| Old (snapcraftctl) | New (craftctl) |
|--------------------|----------------|
| `snapcraftctl build` | `craftctl default` |
| `snapcraftctl pull` | `craftctl default` |
| `snapcraftctl set-version "1.0"` | `craftctl set version 1.0` |
| `snapcraftctl set-grade "stable"` | `craftctl set grade stable` |

> **Note:** `craftctl set version` takes the value as a positional argument with no
> equals sign, and requires a value — `craftctl set version` with no value will error.
> Use `craftctl set version "$(git describe --tags)"` for dynamic versions.

### adopt-info missing parse-info

```
Failed to generate snap metadata: 'adopt-info' refers to part 'mypart',
but that part is lacking the 'parse-info' property
```

Add `parse-info` to the part, or set version explicitly with `craftctl set version` in
an override scriptlet:

```yaml
parts:
  mypart:
    parse-info: [usr/share/metainfo/myapp.appdata.xml]
```

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

### Platform / architecture mismatch

```
No build matches the current host architecture 'amd64'.
```

or

```
build-on value 'arm64' does not match the current host architecture 'amd64'.
```

This error means the `platforms` (or `architectures`) block in the project file does not
include the current host architecture as a `build-on` value.

**Diagnosis:**
1. Check your project's platform definitions:
   ```yaml
   platforms:
     amd64:
       build-on: amd64
       build-for: amd64
     arm64:
       build-on: [amd64, arm64]
       build-for: arm64
   ```
2. Confirm the host architecture: `dpkg --print-architecture`
3. Verify the host architecture appears in at least one `build-on` list.

**Common causes and fixes:**

| Cause | Fix |
|-------|-----|
| `build-on` lists only remote arches (e.g., `arm64`) but host is `amd64` | Add `amd64` to `build-on` for local development, or cross-compile from the correct host |
| `build-for` has no entry matching current host and `--build-for` flag not supplied | Pass `snapcraft pack --build-for=<arch>` to override |
| Two platforms share the same `build-on` arch | Each arch may only appear in one `build-on` per project; split or merge platform entries |

**Conflicting platform build-on entries** (multiple platforms claim the same `build-on`
architecture) will fail with a validation error at startup. Remove the duplicate:

```yaml
# Wrong — amd64 appears in build-on for both platform1 and platform2
platforms:
  platform1:
    build-on: [amd64]
    build-for: [amd64]
  platform2:
    build-on: [amd64, arm64]   # amd64 conflicts with platform1
    build-for: [arm64]

# Fix — each build-on arch must be unique across all platforms
platforms:
  amd64:
    build-on: [amd64]
    build-for: [amd64]
  arm64:
    build-on: [arm64]
    build-for: [arm64]
```

### Plugin / base compatibility

Some plugin options or Python versions are unavailable in newer bases.

#### Python 2 unavailable

```
python-version: python2 is not supported in core22 or core24
```

Python 2 reached end-of-life and is not available in `core22` or `core24`. Fix options:
- Port the application to Python 3.
- Use `base: core20` if Python 2 is unavoidable (core20 still provides Python 2 packages).
- Use a `nil` plugin with a custom `override-build` that downloads and installs a Python 2
  binary manually (not recommended).

#### Deprecated npm plugin option

`npm-node-version` was removed from the npm plugin in snapcraft 7+. Use the `node`
plugin instead, or rely on the npm plugin's automatic Node.js detection:

```yaml
# Old (snapcraft <7)
parts:
  ui:
    plugin: npm
    npm-node-version: "14.13.0"

# New
parts:
  ui:
    plugin: npm
    source: .
    # snapcraft downloads the LTS node automatically
```

### Invalid UTF-8 in build output

```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0x96
```

or the build silently produces garbled output. A scriptlet or command is emitting bytes
that are not valid UTF-8 (e.g., legacy Latin-1 strings, Windows-1252 characters).

**Fix options:**
1. Identify the offending command with `--debug` and inspect its output.
2. Force UTF-8 output if the tool respects `LANG` / `LC_ALL`:
   ```yaml
   override-build: |
     export LANG=C.UTF-8
     export LC_ALL=C.UTF-8
     craftctl default
   ```
3. If the tool always outputs legacy encodings, pipe through `iconv`:
   ```yaml
   override-build: |
     my-tool | iconv -f latin1 -t utf-8
   ```

### Content interface provider not found

```
Provider snap 'unknown-content-snap' is not installed.
```

A `plugs` entry uses `interface: content` with a `default-provider` that is not installed
on the build or test host. This error usually surfaces at `snap install` or runtime, not
during `snapcraft pack`.

**Fix options:**
1. Install the provider snap: `snap install <default-provider-snap>`
2. If the provider is unavailable or the snap is in development, temporarily switch to
   `confinement: devmode` to skip content interface enforcement during testing.
3. If the content interface is not actually needed, remove the plug from `plugs`.

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
