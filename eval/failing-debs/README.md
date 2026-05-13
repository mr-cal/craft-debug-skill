# Debcraft Failing Test Cases

Test cases for evaluating the craft-debug skill against debcraft failures.

## Test Cases

### Schema/Validation Errors (Obvious)
- **missing-maintainer**: Missing required maintainer field
- **missing-parts**: Missing required parts field
- **invalid-package-name**: Package name with uppercase letters
- **bad-priority**: Invalid priority value
- **multi-arch-invalid**: Invalid multi-arch value
- **section-invalid**: Unknown section value

### Build Errors
- **scriptlet-fail**: Override scriptlet with exit 1
- **depends-syntax**: Malformed depends syntax

### Platform/Architecture
- **arch-mismatch**: Build-for architecture not available
- **platform-arm-only**: Only arm64 platform specified

### Debcraft-Specific (Less Obvious)
- **adopt-info-missing-part**: adopt-info references non-existent part
- **passthrough-bad-field**: passthrough overrides managed field
- **multiarch-arch-conflict**: multi_arch: same with architectures: all
- **depends-bad-version**: pip/npm version syntax instead of Debian syntax
- **package-name-case**: Uppercase in packages dict key
