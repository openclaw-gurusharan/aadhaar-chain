# Identity Agent Platform

Solana + Claude Agent SDK identity verification platform.

## State → Skill Loading

**Check `.claude/progress/state.json` for current state, then load corresponding skill.**

| State | Load Skill | When |
|-------|------------|------|
| **SESSION START** | `orchestrator/` | Every session - runs entry protocol |
| **FIX_BROKEN** | `enforcement/` | Health check fails |
| **INIT** | `initialization/` | No feature-list.json |
| **IMPLEMENT** | `implementation/` | Pending feature exists |
| **TEST** | `testing/` | Implementation complete |
| **COMPLETE** | `context-graph/` | All features tested |

## Truly "Any Time" Skills

**Load independently of state when needed:**

| Skill | Use When |
|-------|----------|
| `skill-creator` | Before creating/updating any skill |
| `claude-md-creator` | Before creating/updating CLAUDE.md |
| `browser-testing` | Testing web apps, debugging browser issues |

## Quick Reference

See `.claude/CLAUDE.md` for commands, project structure, and workflows.
