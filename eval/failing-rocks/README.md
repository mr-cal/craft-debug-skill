# Rockcraft Failing Test Cases

Test cases for evaluating the craft-debug skill against rockcraft failures.

## Test Cases

### Schema/Validation Errors (Obvious)
- **missing-base**: Missing required base field
- **invalid-base**: Invalid base value (not ubuntu@XX.XX or bare)

### Build Errors
- **overlay-scriptlet-fail**: Overlay scriptlet with exit 1
- **craftctl-overlay**: Using craftctl in overlay step incorrectly
- **legacy-env-vars**: Using deprecated SNAPCRAFT_* instead of CRAFT_*

### Platform/Architecture
- **platform-arm-only**: Only arm64 platform, building on amd64

### Pebble Services (Rockcraft-Specific)
- **pebble-no-command**: Pebble service missing required command
- **pebble-bad-startup**: Invalid startup value (not enabled/disabled)

### Chisel/Run-User (Rockcraft-Specific)
- **chisel-bad-slice**: Invalid chisel slice syntax
- **run-user-conflict**: run-user can't access root-owned files

### Non-Obvious Failures
- **bare-with-overlay**: base: bare cannot use overlay-packages (no filesystem to overlay)
- **entrypoint-service-missing**: entrypoint-service references non-existent service
- **entrypoint-no-args**: entrypoint-service command lacks [ optional args ]
- **env-interpolation**: environment field doesn't support $VAR interpolation
- **check-multiple-types**: Pebble check with both http and tcp types
