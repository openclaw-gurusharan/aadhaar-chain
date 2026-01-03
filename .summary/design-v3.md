# Agent Harness v3 - System Design

## Overview

Token-efficient, autonomous, self-improving agent framework for building applications with minimal context overhead.

| Metric | v2 | v3 | Improvement |
|--------|----|----|-------------|
| Context at session start | 500+ lines | 76-159 lines | **70-85%** |
| Manual skill invocations | 1-3/session | 0 | **100%** |
| Learning from traces | Never | Continuous | **New** |

---

## Core Principles

1. **Zero Manual Skill Invocation** - Auto-detect intent from prompt + state
2. **Compiled Context** - Extract essentials, cache with hash invalidation
3. **Closed Learning Loop** - Traces → Patterns → Skills → Better Traces
4. **Determinism** - Code verification > LLM judgment
5. **Progressive Disclosure** - Load on-demand, never upfront

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SESSION START                                │
│  UserPromptSubmit Hook (auto-load-skill.sh)                    │
│  ├── detect-skill.py → Which skill needed?                     │
│  ├── compile-context.py → State-specific context (~70 lines)   │
│  └── Output: Compiled context + Skill procedures               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DURING SESSION                               │
│  ├── Skills access compiled context (no CLAUDE.md re-reads)    │
│  ├── Token-efficient MCP for data >50 items                    │
│  ├── Context-graph for decision precedents                     │
│  └── Determinism for all verification (exit codes)             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    SESSION END                                  │
│  SessionEnd Hook (session-end.sh)                              │
│  ├── Store decision traces                                     │
│  ├── Create checkpoint commit                                  │
│  └── Remind to log traces                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## State Machine

```
START ──┬── INIT ──── IMPLEMENT ──── TEST ──┬── COMPLETE
        │                  ↑         │      │
        │                  └─────────┘      │
        └── IMPLEMENT (if feature-list exists)

FIX_BROKEN ← Any state (when health check fails)
```

| State | Trigger | Skill Loaded |
|-------|---------|--------------|
| START | New session, no state.json | None (detect from prompt) |
| INIT | No feature-list.json | initialization |
| IMPLEMENT | Pending features exist | implementation |
| TEST | Feature code complete | testing |
| COMPLETE | All features tested | context-graph |
| FIX_BROKEN | Health check fails | enforcement |

---

## Skills Inventory

### Core State Skills (5)

| Skill | Purpose | Lines | When Loaded |
|-------|---------|-------|-------------|
| `orchestrator` | State machine, compression triggers | 45 | Manual only (auto-load handles it) |
| `initialization` | Project setup, feature breakdown | ~150 | INIT state |
| `implementation` | Feature development workflow | ~200 | IMPLEMENT state |
| `testing` | Validation with determinism | ~100 | TEST state |
| `context-graph` | Learning loops, pattern storage | ~80 | COMPLETE state |

### Setup Skills (5)

| Skill | Purpose | When Used |
|-------|---------|-----------|
| `global-hook-setup` | Install 8 global hooks | Once per machine |
| `project-hook-setup` | Install project-specific hooks | Once per project |
| `enforcement` | Blocking mechanisms (exit 2) | FIX_BROKEN state |
| `determinism` | Code > LLM judgment patterns | Any verification |
| `mcp-setup` | Configure MCP servers | Once per project |

### Utility Skills (5)

| Skill | Purpose | Trigger |
|-------|---------|---------|
| `token-efficient` | Process data >50 items | Large datasets |
| `skill-creator` | Create/update skills | Before skill work |
| `claude-md-creator` | Manage CLAUDE.md files | Before CLAUDE.md edits |
| `mcp-builder` | Build MCP servers | MCP development |
| `browser-testing` | Chrome automation | UI testing |

### Domain Skills (Variable)

| Skill | Purpose |
|-------|---------|
| `brand-guidelines` | Anthropic visual identity |
| `scroll-storyteller` | Scroll-based experiences |
| `terminal-ui-design` | CLI/TUI design |
| `duotone-identity` | Identity platform UI |

---

## Hooks

### Global Hooks (`~/.claude/hooks/`)

| Hook | Event | Blocking | Purpose |
|------|-------|----------|---------|
| `auto-load-skill.sh` | UserPromptSubmit | No | Auto-detect + load skill |
| `verify-state-transition.py` | PreToolUse | Yes | Validate state machine |
| `require-commit-before-tested.py` | PreToolUse | Yes | Git hygiene |
| `require-outcome-update.py` | PreToolUse | Yes | Learning loop closure |
| `link-feature-to-trace.py` | PostToolUse | No | Auto-link features |
| `markdownlint-fix.sh` | PostToolUse | No | Auto-fix markdown |
| `session-end.sh` | SessionEnd | No | Checkpoint commit |
| `remind-decision-trace.sh` | SessionEnd | No | Trace reminder |

### Project Hooks (`.claude/hooks/`)

| Hook | Event | Purpose |
|------|-------|---------|
| `verify-tests.py` | PreToolUse | Run tests before marking tested |
| `verify-health.py` | PreToolUse | Health check before transition |
| `session-entry.sh` | SessionStart | 3-phase entry protocol |

---

## Auto-Load System (v3 New)

### Detection Priority

```python
# detect-skill.py priority order:
1. Simple questions ("what is X") → No skill
2. Slash commands (/commit) → Handled by Skill tool
3. Explicit requests ("run tests") → Override state
4. State-based (IMPLEMENT → implementation)
5. Keyword-based ("build feature" → implementation)
6. Default → No skill
```

### Compiled Context

```python
# compile-context.py extracts:
- Token Budget table (from global CLAUDE.md)
- Execution Decision table
- Core Rules (top 5 bullets)
- Commands table (from project CLAUDE.md)
- Config paths table
- State → Skill mapping
- Current feature summary
```

### Cache Structure

```
~/.claude/cache/
├── context-INIT.md        # Cached INIT context
├── context-INIT.hash      # Hash for invalidation
├── context-IMPLEMENT.md   # Cached IMPLEMENT context
├── context-IMPLEMENT.hash
├── context-TEST.md
├── context-TEST.hash
└── context-COMPLETE.md
```

---

## MCP Servers

### Token-Efficient MCP

| Tool | Purpose | Savings |
|------|---------|---------|
| `execute_code` | Python/Bash/Node in sandbox | 98% |
| `process_csv` | Filter/aggregate CSV | 99% |
| `process_logs` | Pattern match logs | 95% |
| `search_tools` | Find tools by keyword | 95% |
| `batch_process_csv` | Multiple CSVs | 80% |

### Context-Graph MCP

| Tool | Purpose |
|------|---------|
| `context_store_trace` | Store decision with embedding |
| `context_query_traces` | Semantic search for patterns |
| `context_get_trace` | Get trace by ID |
| `context_update_outcome` | Mark success/failure |
| `context_list_traces` | List with pagination |
| `context_list_categories` | Category breakdown |

---

## File Structure

### Global (`~/.claude/`)

```
~/.claude/
├── CLAUDE.md                 # Global instructions (148 lines)
├── settings.json             # Hooks, permissions, plugins
├── cache/                    # Compiled context cache
│   ├── context-{STATE}.md
│   └── context-{STATE}.hash
├── hooks/                    # Global hooks (8 files)
│   ├── auto-load-skill.sh    # NEW: Auto-detect + load
│   ├── verify-state-transition.py
│   ├── require-commit-before-tested.py
│   ├── require-outcome-update.py
│   ├── link-feature-to-trace.py
│   ├── markdownlint-fix.sh
│   ├── session-end.sh
│   └── remind-decision-trace.sh
├── skills/                   # All skills
│   ├── orchestrator/
│   │   ├── skill.md          # Slimmed to 45 lines
│   │   ├── scripts/
│   │   │   ├── detect-skill.py      # NEW: Intent detection
│   │   │   ├── compile-context.py   # NEW: Context compilation
│   │   │   ├── check-state.sh
│   │   │   ├── enter-state.sh
│   │   │   └── session-entry.sh
│   │   └── references/
│   ├── initialization/
│   ├── implementation/
│   ├── testing/
│   ├── context-graph/
│   └── ... (other skills)
└── rules/                    # Modular rules
    └── markdown-formatting.md
```

### Project (`.claude/`)

```
project/
├── CLAUDE.md                 # Project instructions (30-100 lines)
├── .claude/
│   ├── CLAUDE.md             # Quick reference (50-150 lines)
│   ├── config/
│   │   └── project.json      # Project settings
│   ├── progress/
│   │   ├── state.json        # Current state
│   │   ├── feature-list.json # Features with status
│   │   └── traces.json       # Decision traces (local)
│   ├── scripts/              # Project-specific automation
│   │   ├── get-current-feature.sh
│   │   ├── health-check.sh
│   │   ├── feature-commit.sh
│   │   ├── mark-feature-complete.sh
│   │   └── restart-servers.sh
│   └── hooks/                # Project-specific hooks
└── mcp/                      # MCP servers (git submodules)
    ├── token-efficient-mcp/
    └── context-graph-mcp/
```

---

## Token Efficiency Patterns

### Never Do

| Anti-Pattern | Why Bad |
|--------------|---------|
| Load raw CSV/logs | Wastes 99% of tokens |
| Read full CLAUDE.md every session | 500+ lines overhead |
| LLM judgment for verification | Non-deterministic |
| Load skill references upfront | May not need them |

### Always Do

| Pattern | Savings |
|---------|---------|
| Use compiled context | 70-85% |
| Use token-efficient MCP for data | 95-99% |
| Progressive disclosure for skills | 98% |
| Exit codes for verification | 100% deterministic |
| Cache with hash invalidation | Repeated access |

---

## Learning Loop (Phase 3 - Planned)

```
┌─────────────────────────────────────────────────────────────────┐
│                   LEARNING LOOP                                 │
│                                                                 │
│  1. Session ends → Store traces                                 │
│  2. Weekly: Query traces by category                            │
│  3. Extract patterns: "When X, do Y" (>3 occurrences)          │
│  4. Update skill references with patterns                       │
│  5. Generate .claude/scripts/ for repeated workflows            │
└─────────────────────────────────────────────────────────────────┘
```

### Pattern Extraction Rules

- Minimum 3 occurrences with same fix
- All must have `outcome: success`
- Grouped by category (frontend, hydration, api, etc.)

### Auto-Generated Artifacts

| Artifact | Source | Example |
|----------|--------|---------|
| Skill reference | Successful patterns | `implementation/references/patterns.md` |
| Automation script | Repeated workflows | `.claude/scripts/fix-hydration.sh` |
| CLAUDE.md update | New commands | Add to Commands table |

---

## Configuration

### settings.json (Key Sections)

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "hooks": [{
        "type": "command",
        "command": "/bin/bash ~/.claude/hooks/auto-load-skill.sh"
      }]
    }],
    "PreToolUse": [...],
    "PostToolUse": [...],
    "SessionEnd": [...]
  },
  "permissions": {
    "allow": ["Bash(*)", "mcp__*", "Skill(*)"],
    "deny": ["Bash(rm -rf /)"]
  }
}
```

### project.json

```json
{
  "project_type": "fastapi",
  "dev_server_port": 8000,
  "health_check": "curl -sf http://localhost:8000/health",
  "test_command": "pytest",
  "required_env": ["DATABASE_URL", "API_KEY"]
}
```

---

## Success Metrics

| Metric | Target | How Measured |
|--------|--------|--------------|
| Context overhead | <100 lines | `wc -l` on hook output |
| Manual invocations | 0 | Count `/skill` commands |
| Pattern reuse | >50% | Traces with `outcome: success` from query |
| Session startup | <2s | Time to first productive work |
| Token efficiency | 95%+ | Sandbox vs context loading |

---

## Migration from v2

1. **Backup existing skills**: `cp -r ~/.claude/skills ~/.claude/skills-v2-backup`
2. **Update hooks**: Add `UserPromptSubmit` hook to settings.json
3. **Create cache dir**: `mkdir -p ~/.claude/cache`
4. **Install new scripts**: `detect-skill.py`, `compile-context.py`
5. **Slim orchestrator**: Replace with 45-line version
6. **Test**: Start new session, verify auto-load works

---

## Changelog

### v3.0 (2026-01-03)

- **Phase 1: Auto-Load** - Zero manual skill invocation
  - `detect-skill.py` - Intent detection from prompt + state
  - `auto-load-skill.sh` - UserPromptSubmit hook
  - Slimmed orchestrator to 45 lines

- **Phase 2: Compiled Context** - 70-85% context reduction
  - `compile-context.py` - Extract essentials from CLAUDE.md
  - `~/.claude/cache/` - Hash-based caching
  - State-specific context compilation

- **Phase 3: Learning Loop** - (Planned)
  - Pattern extraction from traces
  - Auto-update skill references
  - Generate automation scripts

### v2.0 (Previous)

- State machine with 5 states
- 15 skills (core + setup + utility)
- 8 global hooks
- Token-efficient + context-graph MCP servers
