# Auto Tag Workflow Summary

## What Was Created

A complete automated versioning and tagging system for INMET Weather integration.

## Files Created

1. **[.github/workflows/auto-tag.yml](.github/workflows/auto-tag.yml)** - GitHub Actions workflow
2. **[AUTO_TAG_GUIDE.md](AUTO_TAG_GUIDE.md)** - Complete documentation
3. **[AUTO_TAG_QUICK_REF.md](AUTO_TAG_QUICK_REF.md)** - Quick reference card

## How It Works

### Trigger
```
Pull Request merged to main → Workflow runs
```

### Process Flow
```
1. Detect version bump type from PR title/labels
2. Calculate new version (semver)
3. Update manifest.json with new version
4. Commit the change
5. Create and push git tag
6. Create GitHub release with changelog
7. Release workflow automatically triggers
```

### Version Bump Detection

The workflow intelligently determines version bump type:

| Input | Bump Type | Example |
|-------|-----------|---------|
| `[major]`, `BREAKING CHANGE` | Major | v1.2.3 → v2.0.0 |
| `feat:`, `[minor]` | Minor | v1.2.3 → v1.3.0 |
| `fix:`, `[patch]` | Patch | v1.2.3 → v1.2.4 |
| Label: `breaking` | Major | v1.2.3 → v2.0.0 |
| Label: `feature` | Minor | v1.2.3 → v1.3.0 |
| Label: `bug` | Patch | v1.2.3 → v1.2.4 |
| Label: `skip-release` | None | No tag created |

## Features

### ✅ Intelligent Version Bumping
- Detects bump type from PR title
- Falls back to PR labels
- Defaults to patch bump
- Supports skipping releases

### ✅ Automatic manifest.json Update
- Updates version in manifest.json
- Commits the change
- Pushes to main branch

### ✅ Git Tag Creation
- Creates annotated tag
- Includes PR info in tag message
- Pushes to repository

### ✅ GitHub Release Creation
- Creates release for the tag
- Includes changelog
- Lists PR details
- Shows commit history

### ✅ Integration with Release Workflow
- Auto-tag creates tag
- Release workflow detects tag
- Release workflow runs automatically
- ZIP file created and uploaded

### ✅ Skip Release Support
- Add `skip-release` label
- No tag or release created
- Useful for docs/tests

## Usage Examples

### Example 1: Feature PR

**PR Title:** `feat: Add weather alerts support`

**Labels:** `enhancement`

**Action:**
1. PR merged
2. Workflow detects `feat:` prefix
3. Bumps minor version: v1.2.3 → v1.3.0
4. Updates manifest.json to "1.3.0"
5. Creates tag v1.3.0
6. Creates GitHub release
7. Release workflow runs

**Result:** New release v1.3.0 with ZIP file

### Example 2: Bug Fix PR

**PR Title:** `fix: Correct temperature parsing`

**Labels:** `bug`

**Action:**
1. PR merged
2. Workflow detects `fix:` prefix
3. Bumps patch version: v1.2.3 → v1.2.4
4. Updates manifest.json to "1.2.4"
5. Creates tag v1.2.4
6. Creates GitHub release
7. Release workflow runs

**Result:** New release v1.2.4 with ZIP file

### Example 3: Breaking Change PR

**PR Title:** `[major] Redesign API structure`

**Labels:** `breaking`

**Action:**
1. PR merged
2. Workflow detects `[major]` prefix
3. Bumps major version: v1.2.3 → v2.0.0
4. Updates manifest.json to "2.0.0"
5. Creates tag v2.0.0
6. Creates GitHub release
7. Release workflow runs

**Result:** New release v2.0.0 with ZIP file

### Example 4: Documentation PR

**PR Title:** `docs: Update installation guide`

**Labels:** `documentation`, `skip-release`

**Action:**
1. PR merged
2. Workflow detects `skip-release` label
3. Workflow exits early
4. No tag created
5. No release created

**Result:** Only code changes merged, no release

## Workflow File Overview

### Key Sections

**Trigger:**
```yaml
on:
  pull_request:
    types: [closed]
    branches:
      - main
```

**Permissions:**
```yaml
permissions:
  contents: write  # Needed to create tags and releases
```

**Conditional Execution:**
```yaml
if: github.event.pull_request.merged == true
```

**Steps:**
1. Checkout code
2. Get latest tag
3. Determine version bump type
4. Calculate new version
5. Update manifest.json
6. Commit changes
7. Create and push tag
8. Generate release notes
9. Create GitHub release
10. Display summary

## Benefits

### For Developers
- ✅ No manual version management
- ✅ No need to remember to create tags
- ✅ No manifest.json version updates
- ✅ Consistent versioning
- ✅ Clear PR title conventions

### For Project
- ✅ Automated releases
- ✅ Semantic versioning enforced
- ✅ Professional release notes
- ✅ Complete changelog
- ✅ Reduced human error

### For Users
- ✅ Regular releases
- ✅ Clear version numbers
- ✅ Detailed release notes
- ✅ Easy to update via HACS

## PR Title Best Practices

### Conventional Commits Format

```
<type>[optional scope]: <description>
```

**Types:**
- `feat:` - New feature (minor)
- `fix:` - Bug fix (patch)
- `docs:` - Documentation (skip-release)
- `chore:` - Maintenance (skip-release)
- `test:` - Tests (skip-release)
- `refactor:` - Refactoring (patch/minor)
- `perf:` - Performance (patch)
- `style:` - Formatting (skip-release)
- `ci:` - CI/CD (skip-release)

**Breaking Changes:**
- `feat!:` - Breaking feature
- `BREAKING CHANGE:` in body
- `[major]` prefix

### Examples

**Good PR Titles:**
```
feat: Add support for hourly forecasts
fix: Correct wind speed conversion
[major] Redesign configuration structure
chore: Update dependencies
docs: Add troubleshooting section
test: Add integration tests
```

**Bad PR Titles:**
```
Update code
Fix stuff
Changes
WIP
Merge branch
```

## Labels to Create

Create these labels in your GitHub repository (Settings → Labels):

### Version Control
- `breaking` (red) - Major version bump
- `feature` (blue) - Minor version bump
- `enhancement` (blue) - Minor version bump
- `bug` (red) - Patch version bump
- `bugfix` (red) - Patch version bump
- `fix` (red) - Patch version bump

### Release Control
- `skip-release` (gray) - Don't create release
- `no-release` (gray) - Don't create release

### Other Useful
- `documentation` (gray) - Docs only
- `dependencies` (green) - Dependency updates
- `security` (red) - Security fixes
- `performance` (yellow) - Performance improvements

## Monitoring

### Check Workflow Execution

1. Go to **Actions** tab
2. Find "Auto Tag and Version Bump"
3. Click on the workflow run
4. Review the summary

**Success looks like:**
```
🎉 Auto Tag Complete!

- New Version: v1.3.0
- Bump Type: minor
- PR: #42
- Author: @username

✅ Tag created and pushed
✅ manifest.json updated
✅ GitHub Release created
```

### Verify Results

**Check manifest.json:**
```bash
grep version custom_components/inmet_weather/manifest.json
# Should show: "version": "1.3.0"
```

**Check tags:**
```bash
git tag
# Should show new tag: v1.3.0
```

**Check releases:**
- Go to Releases tab
- New release should be visible
- ZIP file should be attached

## Troubleshooting

### Workflow Didn't Run

**Causes:**
- PR was closed without merging
- PR target wasn't `main` branch
- Workflow file has syntax error

**Solution:**
- Verify PR was merged (not just closed)
- Check PR target branch
- Validate YAML syntax

### Wrong Version Bump

**Causes:**
- PR title doesn't match expected format
- Wrong or missing labels

**Solution:**
- Use correct PR title prefix
- Add appropriate labels
- Or manually delete and recreate tag

### Tag Already Exists

**Cause:**
- Tag was manually created
- Workflow ran twice

**Solution:**
```bash
# Delete the tag
git tag -d v1.3.0
git push origin :refs/tags/v1.3.0

# Re-run workflow or create correct tag
```

### manifest.json Not Updated

**Cause:**
- Workflow failed at commit step
- Permission issues

**Solution:**
- Check workflow logs
- Verify permissions in workflow
- Manually update manifest.json if needed

## Integration with Existing Workflows

### Works With Release Workflow

The auto-tag workflow integrates seamlessly:

```
PR Merged → Auto-Tag Runs → Creates Tag → Release Workflow Triggers → Creates ZIP
```

Both workflows work together:
1. **Auto-tag** creates tag and updates manifest
2. **Release** validates version and creates ZIP
3. **ZIP** is automatically attached to the release

### No Conflicts

The workflows don't conflict:
- Auto-tag runs on PR merge
- Release runs on tag creation
- Both have different triggers
- Both update different aspects

## Future Enhancements

### Possible Additions

1. **Changelog Generation**
   - Auto-generate CHANGELOG.md
   - Update on each release

2. **Pre-release Support**
   - Label: `prerelease` → creates v1.3.0-beta.1
   - For testing before stable release

3. **Hotfix Support**
   - Branch: `hotfix/*` → patch bump
   - Direct to main without PR

4. **Custom Version**
   - PR body: `version: 2.0.0-rc.1`
   - Override automatic versioning

5. **Slack/Discord Notifications**
   - Notify team of new releases
   - Include changelog

## Summary

**Created a complete automated versioning system:**

✅ **Auto-detects version bump type** from PR title/labels
✅ **Updates manifest.json** automatically
✅ **Creates git tags** with proper messages
✅ **Generates GitHub releases** with changelogs
✅ **Integrates with release workflow** seamlessly
✅ **Supports skip-release** for non-release PRs
✅ **Follows semantic versioning** strictly
✅ **Zero manual intervention** required

**No more manual version management!** 🎉

Just merge PRs with proper titles, and everything else is automatic! 🚀
