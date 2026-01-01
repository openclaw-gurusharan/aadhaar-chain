# Quick Reference

## Purpose

Identity Agent Platform - Solana + Claude Agent SDK

## Commands

| Task | Command |
|------|---------|
| Check state | `~/.claude/skills/orchestrator/scripts/check-state.sh` |
| Run tests | `npm test` |
| Health check | `curl -s http://localhost:3000/api/health` |
| Dev server | `cd frontend && npm run dev` |
| Build programs | `anchor build` |
| Deploy devnet | `anchor deploy --provider.cluster devnet` |
| Start gateway | `cd gateway && uvicorn app.main:app --reload` |

## State → Skill

| State | Skill |
|-------|-------|
| INIT | initialization/ |
| IMPLEMENT | implementation/ |
| TEST | testing/ |
| COMPLETE | context-graph/ |

## Config

| File | Purpose |
|------|---------|
| `.claude/config/project.json` | Project settings |
| `.claude/progress/state.json` | Current state |
| `.claude/progress/feature-list.json` | Features |
| `.mcp.json` | MCP servers |

## MCP Tools

**token-efficient**: `execute_code`, `process_csv`, `process_logs`
**context-graph**: `context_store_trace`, `context_query_traces`

## Issue Resolution Workflow

Smart decision-tracing system to learn from past issues and apply solutions:

| Step | Action | Tool |
| --- | --- | --- |
| 1 | Query context graph for similar issues | `context_query_traces(query, category)` |
| 2 | If found: apply learned solution pattern | Review `trace_id` and outcome |
| 3 | If not found: investigate and find fix | Debug using browser-testing skill |
| 4 | Apply fix and test in browser | Verify no regressions |
| 5 | Log decision trace with outcome | `context_store_trace(decision, category, outcome)` |

**Decision Trace Categories:**

| Category | Use For | Example Outcomes |
| --- | --- | --- |
| frontend | UI/component issues, rendering, interactions | WalletModal overlay blocking clicks |
| hydration | React server/client mismatches | Wallet adapter SSR incompatibility |
| framework | Architecture & pattern decisions | Next.js dynamic imports |
| testing | Test automation & validation workflows | Browser automation setup |
| css | Styling and layout issues | Theme colors, responsive design |

**Recent Traces:** Query similar issues before solving new problems - system learns from every fix
