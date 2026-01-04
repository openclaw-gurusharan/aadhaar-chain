# Project Automation Scripts

## Overview

These scripts customize the Claude Code workflow for this project. They are copied during initialization and should be customized to match your project architecture.

## Scripts

### get-current-feature.sh

**Purpose:** Extract the next pending feature from `.claude/progress/feature-list.json`

**Output:** JSON with feature details

```json
{
  "id": "feat-013",
  "description": "Feature description",
  "priority": "P0",
  "status": "pending",
  "acceptance_criteria": [...]
}
```

**Customize for:**

- Monorepo structure (multiple feature lists)
- Custom feature ordering logic
- Filtering by priority, phase, or tags

**Default:** Returns first pending feature from feature-list.json

---

### health-check.sh

**Purpose:** Fast health diagnosis - show root cause immediately

**⚠️ CRITICAL:** This script runs at the START of EVERY SESSION by orchestrator.
**NO TIME should be wasted finding root cause.** Evolve this continuously.

**Exit codes:**

- `0` = All systems healthy
- `1` = Infrastructure/service failed (shows error immediately)
- `2` = Timeout

**Checks (in order - fails fast on infrastructure):**

1. **Infrastructure FIRST** (before services):
   - PostgreSQL database running
   - Disk space (prevent out-of-disk errors)
   - Required environment files exist

2. **Services:**
   - Frontend health endpoint (:3000)
   - Backend health endpoint (:8000/api/health)
   - Process status (running vs not responding)

3. **Logs:**
   - Recent errors from log files
   - Warnings (non-critical)

4. **Optional:**
   - MCP servers running

**Examples:**

```bash
# All healthy
./.claude/scripts/health-check.sh
# ✅ All systems healthy

# Database down - IMMEDIATE diagnosis
./.claude/scripts/health-check.sh
# ✗ PostgreSQL not responding
#
# Fix:
#   brew services start postgresql@15
# ❌ Infrastructure check FAILED

# Backend failed - shows WHY instantly
./.claude/scripts/health-check.sh
# ✗ Backend is NOT responding
#   Process 'uvicorn' is NOT running
#
# Recent errors from logs/backend.log:
# ---
# ConnectionRefusedError: [Errno 61] Connection refused
# Database initialization failed
# ---
```

**Customize for:**

- Your infrastructure (Redis, Solana validator, etc.)
- Your services (ports, health endpoints)
- Your log file locations
- Your environment file paths
- **Keep evolving this - add new failure patterns as you discover them**

---

### restart-servers.sh

**Purpose:** Kill processes on ports and restart frontend/backend servers

**Usage:**

```bash
./.claude/scripts/restart-servers.sh                    # Restart both
./.claude/scripts/restart-servers.sh --no-frontend      # Backend only
./.claude/scripts/restart-servers.sh --no-backend       # Frontend only
```

**What it does:**

1. Kills processes on ports 3000 and 8000
2. Starts backend with logs output to `logs/backend.log`
3. Starts frontend with logs output to `logs/frontend.log`
4. Waits for services to be ready (30s timeout)
5. Reports success/failure

**Customize for:**

- Different ports for your services
- Additional services (database, validator)
- Different start commands
- Log file locations

---

### feature-commit.sh

**Purpose:** Commit changes with feature ID in commit message

**Usage:**

```bash
.claude/scripts/feature-commit.sh feat-013 "Implemented DID registry"
```

**Customize for:**

- Commit message format (conventional commits, etc.)
- Git hooks (pre-commit hooks, signing, etc.)
- Branch naming conventions
- Linking to issue trackers

**Default format:**

```
[feat-013] Implemented DID registry

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

### mark-feature-complete.sh

**Purpose:** Update feature status in `.claude/progress/feature-list.json`

**Usage:**

```bash
.claude/scripts/mark-feature-complete.sh feat-013 implemented
.claude/scripts/mark-feature-complete.sh feat-013 tested
```

**Customize for:**

- Custom status values (e.g., "review", "deployed")
- Additional metadata (completion time, tester, etc.)
- State transitions (only allow tested → completed)

**Default:** Sets `status` field to provided value (default: "implemented")

---

### check-state.sh

**Purpose:** Get current state from `.claude/progress/state.json`

**Output:** Human-readable or JSON state

**Usage:**

```bash
.claude/scripts/check-state.sh          # Human-readable
.claude/scripts/check-state.sh --json   # JSON format
```

**Customize for:**

- Additional state information
- Custom state fields
- Integration with other tools

---

### validate-transition.sh

**Purpose:** Validate state machine transitions

**Usage:**

```bash
.claude/scripts/validate-transition.sh FROM TO
# Exit 0 = valid, Exit 1 = invalid
```

**Customize for:**

- Custom state machines
- Additional transition rules
- Project-specific constraints

**Default:** Enforces standard state machine (START → INIT → IMPLEMENT → TEST → COMPLETE)

---

### check-context.sh

**Purpose:** Monitor token usage and trigger compression

**Output:** Compression level (none, remove_raw, summarize, full, emergency)

**Usage:**

```bash
.claude/scripts/check-context.sh 0.75  # Pass usage percentage
```

**Customize for:**

- Custom thresholds
- Project-specific compression strategies
- Integration with context management tools

---

## Customization Workflow

### During Implementation

1. **Read this README** to understand script purposes
2. **Review each script** for project fit
3. **Customize as needed** before implementing feature
4. **Test scripts** to ensure they work for your architecture
5. **Commit changes** with clear commit messages

### Example Customization

```bash
# Before implementing feat-013
cat .claude/scripts/README.md  # Understand purposes
nano .claude/scripts/health-check.sh  # Customize for my services
./.claude/scripts/health-check.sh  # Test it works
git add .claude/scripts/health-check.sh
git commit -m "feat: customize health-check for multi-service architecture"
```

---

## Template Location

Original templates are maintained in:

```
~/.claude/skills/initialization/templates/
```

When in doubt, refer to templates for examples and best practices.

To re-copy templates (preserving your customizations):

```bash
~/.claude/skills/initialization/assets/copy-scripts.sh
```

---

## Evolution

These scripts should evolve with your project:

- **Initial:** Generic templates (copied from templates/)
- **Customized:** Modified for project architecture
- **Mature:** Optimized for project workflows and patterns

Track evolution in git:

```bash
git log --follow .claude/scripts/health-check.sh
```

---

## Troubleshooting

**Script not executable?**

```bash
chmod +x .claude/scripts/*.sh
```

**Script uses wrong paths?**

- Update paths to match your project structure
- Use relative paths from project root

**Health check failing?**

- Verify services are running
- Check ports and endpoints match your setup
- Increase timeout if services start slowly

**Feature list not found?**

- Ensure `.claude/progress/feature-list.json` exists
- Run initialization skill if missing
