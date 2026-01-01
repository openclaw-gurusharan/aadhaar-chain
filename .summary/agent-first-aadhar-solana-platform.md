# Agent-First Identity Platform - Implementation Plan

## Executive Summary

Create a self-sovereign identity platform on Solana powered by Claude Agent SDK that simplifies aadhar-solana by 70% while adding real agent automation.

**Key Improvements:**

- 5 Solana programs → 2 programs (2,005 → 350 lines)
- NestJS backend → FastAPI gateway (2,382 → 500 lines)
- On-chain PII storage → Hash-only commitments (928 → 128 bytes)
- Mock API Setu → Real government API integration
- Documentation-only agents → 4 running Claude Agent SDK agents
- **70% code reduction, 90% cost reduction**

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│ LAYER 2: AGENT LAYER (Claude Agent SDK)                            │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Doc Validator│  │Fraud Detector│  │ Compliance   │              │
│  │    Agent     │  │    Agent     │  │   Monitor    │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         └──────────────────┼──────────────────┘                      │
│                    ┌───────▼────────┐                               │
│                    │ Orchestrator   │                               │
│                    └───────┬────────┘                               │
└────────────────────────────┼─────────────────────────────────────────┘
                             │ MCP Tools
┌────────────────────────────┼─────────────────────────────────────────┐
│ LAYER 1: API Gateway (FastAPI, 500 lines)                          │
│ Stateless: JWT auth, rate limiting, agent proxy                     │
└────────────────────────────┼─────────────────────────────────────────┘
                             │
┌────────────────────────────┼─────────────────────────────────────────┐
│ LAYER 0: Solana (2 programs, 350 lines)                            │
│ Identity Core: DID registry, hash commitments, verification bitmap  │
│ Credential Vault: Verifiable credentials, ZK proofs, revocation     │
└─────────────────────────────────────────────────────────────────────┘

Off-Chain: IPFS encrypted blobs (928 bytes PII → 32 bytes commitment)
```

---

## Solana Programs (2 vs 5)

### 1. Identity Core (~200 lines)

**Merges**: identity-registry + verification-oracle + reputation-engine

**State**:

```rust
#[account]
pub struct Identity {
    pub authority: Pubkey,
    pub did: String,
    pub commitment_hash: [u8; 32],  // Replaces ALL encrypted PII fields
    pub verification_bitmap: u64,
    pub reputation: u16,
    pub created_at: i64,
}
```

**Instructions** (6):

- create_identity
- update_commitment
- set_verification_bit
- increment_reputation
- decrement_reputation
- recover_identity

### 2. Credential Vault (~150 lines)

**Simplifies**: credential-manager

**Instructions** (4):

- issue_credential
- revoke_credential
- verify_zk_proof
- update_registry

---

## Claude Agent SDK Agents (4)

### Agent 1: Document Validator

- Parse Aadhaar/PAN documents (PDF, images)
- OCR for scanned docs
- Field extraction & format validation
- **MCP**: document-processor

### Agent 2: Fraud Detection

- Document tampering detection
- Watchlist cross-reference
- Pattern recognition (synthetic IDs)
- **MCP**: pattern-analyzer, watchlist-db

### Agent 3: Compliance Monitor

- Aadhaar Act compliance check
- DPDP Act validation
- Consent artifact verification
- **MCP**: compliance-rules, audit-logger

### Agent 4: Verification Orchestrator (Meta-Agent)

- Coordinates workflow: Validator → Fraud → Compliance → Review
- State machine: PENDING → FRAUD_CHECK → COMPLIANCE_REVIEW → APPROVED/REJECTED
- Aggregates results, makes deterministic decision (temp=0)

---

## MCP Servers (4)

### 1. Document Processor (Python FastMCP)

- `parse_document(url, type)` - Extracted fields only (98% token savings)
- `validate_format(data, schema)` - Sandbox validation
- `ocr_image(image_bytes)` - OCR processing

### 2. Solana Interaction (TypeScript FastMCP)

- `get_identity(did)`
- `update_verification_bit(did, bit_index)`
- `submit_transaction(instruction)`
- `get_account_history(pubkey)`

### 3. API Setu Integration (Python FastMCP)

- `verify_aadhaar_otp(aadhaar_number, otp)` - REAL API (no mocks)
- `verify_pan_details(pan, name, dob)`
- `fetch_aadhaar_data(aadhaar_number, consent)`

### 4. IPFS Storage (TypeScript FastMCP)

- `store_encrypted_blob(encrypted_data, acl)`
- `retrieve_encrypted_blob(cid, decryption_key)`
- `generate_commitment(data)`

---

## Project Structure

```
identity-agent-platform/
├── programs/
│   ├── identity-core/          # 200 lines Rust
│   └── credential-vault/       # 150 lines Rust
├── gateway/                     # 500 lines FastAPI
│   └── app/
│       ├── api/routes/
│       │   ├── verify.py
│       │   └── identity.py
│       └── mcp/client.py
├── agents/                      # Claude Agent SDK configs
│   ├── orchestrator/
│   ├── document-validator/
│   ├── fraud-detection/
│   └── compliance-monitor/
├── mcp-servers/                 # 4 custom MCP servers
│   ├── document-processor/
│   ├── solana-interaction/
│   ├── apisetu-integration/
│   └── ipfs-storage/
├── mobile/                      # Simplified React Native (optional)
├── scripts/
│   ├── build-programs.sh
│   ├── deploy-programs.sh
│   └── test-integration.sh
└── tests/
```

---

## Implementation Phases

### Phase 1: Solana Programs (Week 1-2)

- Create project structure
- Implement Identity Core (200 lines, 6 instructions)
- Implement Credential Vault (150 lines, 4 instructions)
- Write Anchor tests
- Deploy to local validator

### Phase 2: MCP Servers (Week 3)

- Document Processor (OCR, PDF parsing, sandbox)
- Solana Interaction (Anchor client wrapper)
- API Setu Integration (REAL SDK, no mocks)
- IPFS Storage (encrypted blobs, commitments)

### Phase 3: Agent Development (Week 4)

- Configure 4 agents (agent.json, instructions.md)
- Create skills for each agent
- Test agent coordination

### Phase 4: API Gateway (Week 5)

- FastAPI with JWT, rate limiting
- Verification endpoints
- Identity endpoints
- MCP client integration

### Phase 5: Integration & Testing (Week 6)

- End-to-end verification flow tests
- Performance benchmarks
- Security audits
- Documentation

### Phase 6: Mobile App (Week 7-8, Optional)

- React Native with wallet integration
- Document upload, verification UI

---

## Token Efficiency

- **Sandbox processing**: Large docs processed in-memory, never loaded to context (98% savings)
- **Progressive disclosure**: Agent configs loaded on-demand (Level 1: names, Level 2: descriptions, Level 3: full instructions)
- **MCP defer_loading**: Tool descriptions loaded when invoked (85% savings)
- **Evidence collection**: Code verification (exit codes) not LLM judgment

---

## Data Flow: User → Agents → Blockchain

```
1. User uploads document → API Gateway
2. Gateway stores to IPFS encrypted → generates commitment
3. Orchestrator Agent triggers:
   ├─ Doc Validator (parallel): Parse doc, extract fields
   ├─ Fraud Detection (sequential): Check watchlists, tampering
   └─ Compliance Monitor (parallel): Check Aadhaar Act, consent
4. Review Agent: Aggregates → makes decision
5. Solana Interaction MCP: update_verification_bit() on-chain
6. Gateway polls blockchain → returns success to user
```

---

## Critical Reference Files

| File | Purpose |
|------|---------|
| `aadhar-solana/programs/identity-registry/src/state.rs` | PDA patterns (keep), over-engineered storage (remove) |
| `aadhar-solana/packages/api/src/services/api-setu.service.ts` | What NOT to do (mocks, setTimeout) |
| `token-efficient-mcp/README.md` | Token efficiency patterns for all MCP servers |
| `agent-harness/DESIGN-v2.md` | Agent orchestration patterns |

---

## Comparison: aadhar-solana → New Platform

| Metric | aadhar-solana | New Platform |
|--------|---------------|--------------|
| Solana Programs | 5 (2,005 lines) | 2 (350 lines) |
| Backend | NestJS (2,382 lines) | FastAPI (500 lines) |
| On-Chain Data | 928 bytes/identity | 128 bytes/identity |
| Cost/Identity | ~0.005 SOL | ~0.0005 SOL |
| Verification | Mock (100% fake) | Real agents + API Setu |
| Agents | Docs only | 4 running agents |
| Token Efficiency | None | 85%+ savings |
| **Total Lines** | ~5,000 | ~1,500 (70% reduction) |
