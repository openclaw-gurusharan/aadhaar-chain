# Project Scripts

Deterministic workflows for repeatable automation.

| Script | Purpose | Usage | Exit Codes |
|--------|---------|-------|------------|
| `restart-servers.sh` | Kill + restart frontend (3000) + gateway (8000) | `.claude/scripts/restart-servers.sh` | 0=healthy, 1=failed, 2=timeout |
| `update-feature.sh` | Update feature list status and manage transitions | `.claude/scripts/update-feature.sh <feat_id> <status> [next_id] [next_status]` | 0=success, 1=error, 2=validation |

## Convention

- Exit codes: 0=pass, 1=fail, 2=timeout/needs-fix
- Evidence stored in `/tmp/` for verification
- Scripts execute without loading to context (0 tokens)

## Scripts

### `update-feature.sh`

**Purpose:** Atomically update feature status in `.claude/progress/feature-list.json` with automatic summary recalculation.

**Usage:**

```bash
# Update single feature
.claude/scripts/update-feature.sh feat-012a completed

# Update current and transition to next
.claude/scripts/update-feature.sh feat-012e completed feat-012f in_progress
```

**Behavior:**

- Creates backup before modification
- Validates status values (pending|in_progress|completed)
- Recalculates summary counts
- Restores backup on error
- Returns exit code 0 on success

**When to use:**

- After completing a feature phase
- Before starting next feature
- Reduces ~150 tokens vs manual Python scripts
