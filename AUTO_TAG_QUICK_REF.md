# Auto Tag Quick Reference

## PR Title Formats

### Major Version Bump (1.0.0 → 2.0.0)
```
[major] Your PR title
major: Your PR title
BREAKING CHANGE: Your PR title
```

### Minor Version Bump (1.0.0 → 1.1.0)
```
[minor] Your PR title
minor: Your PR title
feat: Your PR title
feature: Your PR title
```

### Patch Version Bump (1.0.0 → 1.0.1)
```
[patch] Your PR title
patch: Your PR title
fix: Your PR title
bugfix: Your PR title
```

## Labels

| Label | Effect |
|-------|--------|
| `breaking` | Major bump |
| `feature`, `enhancement` | Minor bump |
| `bug`, `bugfix`, `fix` | Patch bump |
| `skip-release`, `no-release` | No tag created |

## Examples

### Feature (Minor)
```
Title: feat: Add weather alerts
Labels: enhancement
Result: v1.2.3 → v1.3.0
```

### Bug Fix (Patch)
```
Title: fix: Correct temperature conversion
Labels: bug
Result: v1.2.3 → v1.2.4
```

### Breaking Change (Major)
```
Title: [major] Redesign API
Labels: breaking
Result: v1.2.3 → v2.0.0
```

### Skip Release
```
Title: docs: Update README
Labels: skip-release
Result: No tag created
```

## What Happens

1. PR merged to `main`
2. Workflow detects bump type from title/labels
3. Calculates new version
4. Updates `manifest.json`
5. Creates and pushes git tag
6. Creates GitHub release
7. Release workflow triggers automatically

## When to Skip Release

Add `skip-release` label for:
- Documentation changes
- Code style changes
- Test additions
- CI/CD updates
- Dependency updates (unless they add features)

## Verification

Check the workflow ran:
1. Go to **Actions** tab
2. Find "Auto Tag and Version Bump" workflow
3. Check the summary for new version

## Manual Tag (Override)

If needed, create tag manually:
```bash
git tag -a v1.3.0 -m "Release v1.3.0"
git push origin v1.3.0
```

Workflow will skip if tag already exists.
