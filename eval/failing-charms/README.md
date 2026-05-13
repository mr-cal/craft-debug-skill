# Charmcraft Failing Test Cases

Test cases for evaluating the craft-debug skill against charmcraft failures.

## Test Cases

### Schema/Validation Errors (Obvious)
- **missing-summary**: Missing required summary field
- **invalid-type**: Invalid type value (must be charm or bundle)
- **config-bad-type**: Invalid config option type

### Build/Runtime Errors
- **scriptlet-exit**: Override scriptlet with explicit exit 1
- **ops-import-fail**: Missing ops dependency
- **bases-deprecated**: Using deprecated bases syntax

### Platform/Architecture
- **platform-mismatch**: Build-on doesn't match available host

### Charm-Specific (Less Obvious)
- **dispatch-not-executable**: Entrypoint file exists but not executable (chmod +x)
- **ops-main-missing**: Imports ops but never calls ops.main()
- **duplicate-config-sources**: Config in both charmcraft.yaml AND config.yaml
- **duplicate-metadata-field**: Same field in charmcraft.yaml AND metadata.yaml
- **naming-convention-mixed**: Mixing snake_case and kebab-case in config options

### Integration
- **k8s-no-containers**: K8s charm missing containers definition
- **relation-missing-interface**: Relation definition missing interface
- **action-no-schema**: Action missing required description
