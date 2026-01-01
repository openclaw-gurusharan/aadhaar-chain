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
