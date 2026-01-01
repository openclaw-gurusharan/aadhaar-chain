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

- Use `mcp__token-efficient__execute_code` for sandbox execution
- Progressive disclosure for agent configs
- Hash commitments instead of on-chain PII (928 → 32 bytes)

## Implementation Phases

| Phase | Focus | Status |
|-------|-------|--------|
| 1-5 | Frontend (Next.js + wallet) | pending |
| 6-7 | Solana programs | pending |
| 7-8 | MCP servers | pending |
| 8-9 | Claude agents | pending |
| 9-10 | FastAPI gateway | pending |
| 11-12 | Integration | pending |
