# Identity Agent Platform

Self-sovereign identity on Solana powered by Claude Agent SDK.

## Architecture

| Layer | Component | Lines |
|-------|-----------|-------|
| 2 | Agent Layer (4 Claude agents) | ~400 |
| 1 | FastAPI Gateway | ~500 |
| 0 | Solana Programs (2) | ~350 |

## Project Structure

```text
├── frontend/          # Next.js 15 + wallet integration
├── programs/          # Solana Anchor programs
├── agents/            # Claude Agent SDK agents
├── mcp-servers/       # 4 MCP servers
├── gateway/           # FastAPI backend
└── scripts/           # Build, deploy, test
```

## Commands

| Task | Command |
|------|---------|
| Dev server | `cd frontend && npm run dev` |
| Build programs | `anchor build` |
| Deploy devnet | `anchor deploy --provider.cluster devnet` |
| Run tests | `npm test` |
| Start gateway | `cd gateway && uvicorn app.main:app --reload` |

## Agents

| Agent | Purpose | MCP |
|-------|---------|-----|
| Document Validator | Parse Aadhaar/PAN docs | document-processor |
| Fraud Detection | Tampering, watchlists | pattern-analyzer |
| Compliance Monitor | Aadhaar Act, DPDP | compliance-rules |
| Orchestrator | Workflow coordination | all |

## MCP Servers

| Server | Language | Purpose |
|--------|----------|---------|
| document-processor | Python | OCR, field extraction |
| solana-interaction | TypeScript | Blockchain ops |
| apisetu-integration | Python | Real govt API |
| ipfs-storage | TypeScript | Encrypted blobs |

## Solana Programs

| Program | Instructions |
|---------|--------------|
| identity-core | create_identity, update_commitment, set_verification_bit, recover_identity |
| credential-vault | issue_credential, revoke_credential, verify_zk_proof |

## Environment Variables

| Variable | Purpose |
|----------|---------|
| SOLANA_RPC_URL | Solana cluster endpoint |
| ANTHROPIC_API_KEY | Claude API access |
| IPFS_GATEWAY_URL | IPFS storage |
| APISETU_CLIENT_ID | API Setu credentials |

## Development Flow

1. Start Solana localnet: `solana-test-validator`
2. Deploy programs: `anchor deploy`
3. Start frontend: `cd frontend && npm run dev`
4. Start gateway: `cd gateway && uvicorn app.main:app --reload`

## Token Efficiency

**CRITICAL**: Proactively use token-efficient MCP tools BEFORE expensive operations.

| Instead of | Use This | When | Savings |
| :--- | :--- | :--- | :--- |
| `Bash` (code exec) | `mcp__token-efficient__execute_code` | Python/Bash/Node code | 98% |
| `Bash` (load CSV) | `mcp__token-efficient__process_csv` | >50 rows, filtering | 99% |
| `Bash` (grep logs) | `mcp__token-efficient__process_logs` | Pattern matching | 95% |
| `Read` (large files) | `Read` with offset/limit | Files >100 lines | 90% |
| Multiple CSVs | `mcp__token-efficient__batch_process_csv` | 2-5 files | 80% |

**Priority Rule**: If operation processes >50 items, MUST use token-efficient MCP.

**Available Tools**:

- `execute_code` - Python/Bash/Node in sandbox
- `process_csv` - Filter, aggregate, paginate CSV
- `batch_process_csv` - Multiple CSVs with same filter
- `process_logs` - Pattern match with pagination
- `search_tools` - Find MCP tools by keyword (95% savings)

## Bug Fix Verification

**CRITICAL**: Human verification required before logging successful decision traces.

### Workflow

```text
Bug Found → Query Context Graph → No trace?
                                      ↓
                        Fix issue → Browser test → Agent: "Fixed!"
                                                    ↓
                                    AskUserQuestion (verify)
                                                    ↓
                         ┌──────────────────┬────────────────┬────────────────┐
                         │                  │                │                │
                      YES (Fixed)        NO (Broken)    EXPLAIN          OTHER
                         │                  │                │                │
                    Log trace          Try again        Get details      Handle case
                  outcome="success"      with fix          │               appropriately
                                                        Retry fix
```

### User Verification Prompt

```python
AskUserQuestion(
    questions=[{
        "question": "I've fixed the issue. Can you verify in browser that it's resolved?",
        "header": "Verify Fix",
        "options": [
            {"label": "Yes, fixed", "description": "Issue is resolved, log to decision traces"},
            {"label": "No, still broken", "description": "Issue persists, try again"},
            {"label": "Explain more", "description": "Provide additional context"}
        ],
        "multiSelect": False
    }]
)
```

### Rules

| Action | When | Outcome |
| :--- | :--- | :--- |
| Log trace with `outcome: "success"` | User confirms "Yes, fixed" | ✅ Allowed |
| Log trace with `outcome: "failure"` | Multiple failed attempts | ✅ Allowed |
| Log trace with `outcome: "pending"` | Before user verification | ✅ Allowed |
| Log trace with `outcome: "success"` | Without user verification | ❌ Blocked |

### Context Graph Clean Data

- Only verified fixes logged as `success`
- Prevents garbage data in learning system
- Human is ultimate source of truth
