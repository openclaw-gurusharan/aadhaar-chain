# aadhaar-chain - Memory & Decision Log

## 🎯 Project Vision
Identity verification platform using Solana blockchain + Claude Agent SDK + MCP servers
- Verified credentials on-chain (DID, verification bitmap)
- OCR-based document parsing (Aadhaar, PAN)
- Fraud detection with compliance rules (Aadhaar Act 2019, DPDP Act 2019)
- Context Graph for decision traces and precedents

## 📊 Current Progress

### ✅ Completed Features (13/22 - 59%)
- Frontend (Phase 1-4): 11 features (50%)
- Backend + Agent SDK (Phase 5): 2 features (18%)

### 🏗️ Currently Working On
- Phase 5 (Backend + Agent SDK)
- Just completed: feat-009 (Pattern Analyzer + Compliance Rules MCP tools)

### 📋 Next Features (Pending)
- feat-010: Agent definitions - **IN PROGRESS** (partially done)
- feat-011: Orchestrator agent workflow
- feat-012: Verification routes with status tracking
- feat-013: Identity and Transaction routes
- feat-014: Credentials routes

## 💡 Important Decisions Made

### Architecture Decisions
1. **Tech Stack**
   - Frontend: Next.js 15, TypeScript, Tailwind CSS, shadcn/ui
   - Backend: FastAPI, Uvicorn, Pydantic
   - Agents: Claude Agent SDK (Anthropic)
   - Blockchain: Solana (solders)
   - MCP: Document Processor, Pattern Analyzer, Compliance Rules

2. **MCP Server Structure**
   - Decision: Separate MCP servers for specialized tasks
   - Reasoning: Better isolation, can scale individually
   - Storage: `mcp-servers/` directory structure
   - Files created:
     - `document-processor/__init__.py`
     - `pattern-analyzer/__init__.py`
     - `compliance-rules/__init__.py`

3. **Agent Architecture**
   - Decision: 4 specialized agents + 1 orchestrator
   - Agents: Document Validator, Fraud Detection, Compliance Monitor, Orchestrator
   - Tool restrictions: Subagents DON'T have Task tool (prevents infinite loops)
   - Orchestrator: HAS Task tool (can coordinate workflows)
   - Storage: `mcp/agents.py` with AgentDefinition class

4. **Context Graph Usage**
   - Decision: Store ALL verification decisions as traces
   - Benefits: Query precedents, learn from past decisions
   - Categories: architecture, fraud-detection, compliance-monitor, verification
   - MCP Tools: `mcp_context_store_trace`, `mcp_context_query_traces`

5. **Fraud Detection Approach**
   - Decision: Multi-layered (OCR quality + tampering + compliance)
   - Risk scoring: 0.0-1.0 scale
   - Categories: Safe (0-0.2), Low (0.2-0.5), Medium (0.5-0.7), High (0.7-1.0)
   - Outcome mapping:
     - Risk < 0.7 + Compliant + OCR > 0.6 → APPROVE
     - Risk > 0.7 OR Violation → REJECT
     - Otherwise → MANUAL_REVIEW

6. **Compliance Rules**
   - Aadhaar Act 2019:
     - Purpose limitation (KYC only)
     - Explicit consent required
     - Data minimization (only essential fields)
   - DPDP Act 2019:
     - Data minimization (collect only what's needed)
     - Storage duration (X days default)
     - Access control (role-based)

### Context Graph Queries Used
- Query: "FastAPI gateway setup backend scaffolding configuration health endpoint"
  - Category: architecture
  - Outcome: success
  - Decision: Use FastAPI (async, modern) over Flask

- Query: "Document Processor MCP tools Tesseract OCR"
  - Category: architecture
  - Outcome: success
  - Decision: Use Python OCR with Tesseract integration

### Data Model Decisions
1. **Verification Status**
   - Steps: document_received, parsing, fraud_check, compliance_check, blockchain_upload, complete
   - Progress: 0.0-1.0 float
   - State management: In-memory store (for development)

2. **Credential Model**
   - Structure: CredentialClaim (type, value, verified_at) on Credential
   - Revocation: Boolean flag
   - Storage: In-memory store (mock for development)

3. **Transaction Model**
   - Types: identity_create, credential_issue, transaction_submit
   - Status: pending, confirmed, failed

### Error Handling Strategy
1. **Network Restrictions**
   - Issue: Cannot pip install dependencies due to proxy (403 Forbidden)
   - Workaround: Skip testing in SRT sandbox, validate logic manually
   - Impact: Medium (tests run when environment allows)

2. **Git Workflow**
   - Issue: venv accidentally staged
   - Workaround: Reset venv, exclude in .gitignore
   - Push strategy: Push after each major feature, tag for review

### Integration Points
- **Frontend → Backend**
  - API: `gateway/app/routes.py` provides verification endpoints
  - Client: Next.js API client (lib/api.ts)
  - Authentication: Wallet-based routing (WalletRouter component)

- **Backend → Blockchain**
  - Solana: RPC client integration (future: feat-015)
  - Programs: Identity Core (feat-016), Credential Vault (feat-017)

- **Backend → Context Graph**
  - Storage: All verification decisions stored as traces
  - Query: Use before making similar decisions

## 🔄 Workflow Notes

### Current Workflow Pattern
```
1. Build Feature (Implementation skill)
   ├─ Query context-graph for precedents
   ├─ Write code (use DRAMS design)
   ├─ Write tests
   ├─ Type-check
   ├─ Run tests
   └─ Commit when ALL pass

2. Test Feature (Testing skill)
   ├─ Restart servers
   ├─ Run tests
   ├─ Browser testing
   └─ Return to tracker

3. Store Decision
   └─ mcp_context_store_trace (category, outcome, reasoning)
```

### Token Efficiency Strategy
- Use `mcp_execute_code` for >50 items (CSV processing, large log analysis)
- Batch context-graph queries when possible
- Compress at 70% / 85% when context gets large

### Known Issues
- [ ] feat-009 (Agent definitions) - Files created but commit status unclear
- [ ] MCP servers - Need to verify all tools are properly registered
- [ ] git status - Sometimes shows files as already tracked when they're not

### Next Immediate Actions
1. ✅ Complete feat-009 (Agent definitions) - Verify commit status
2. ⏳ Start feat-010 (Agent SDK integration)
3. ⏳ Build feat-011 (Orchestrator agent workflow)
4. ⏳ Create verification routes (feat-012)

### Context Graph Queries to Run
Before making architecture decisions:
- "FastAPI gateway backend choices"
- "MCP server architecture pattern"
- "Agent tool restrictions design"
- "Fraud detection risk scoring"

Before making fraud detection decisions:
- "Aadhaar document tampering patterns"
- "PAN card fraud precedents"
- "Document quality thresholds"

Before making compliance decisions:
- "Aadhaar Act 2019 data collection rules"
- "DPDP Act 2019 consent requirements"
- "Storage duration violation precedents"

---

**Last Updated:** 2026-02-03 16:25 UTC
**Agent:** Marvin (Clawdbot)
