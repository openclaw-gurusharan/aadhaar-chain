# Project Scripts

Deterministic workflows for repeatable automation.

| Script | Purpose | Usage | Exit Codes |
|--------|---------|-------|------------|
| `restart-servers.sh` | Kill + restart frontend (3000) + gateway (8000) | `.claude/scripts/restart-servers.sh` | 0=healthy, 1=failed, 2=timeout |

## Convention

- Exit codes: 0=pass, 1=fail, 2=timeout/needs-fix
- Evidence stored in `/tmp/` for verification
- Scripts execute without loading to context (0 tokens)
