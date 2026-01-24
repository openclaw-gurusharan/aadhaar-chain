# Quick Reference

## Commands

| Task | Command |
|------|---------|
| Check state | `~/.claude/skills/orchestrator/scripts/check-state.sh` |
| Restart servers | `.claude/scripts/restart-servers.sh` |
| Run tests | `npm test` |
| Health check | `curl -s http://localhost:3000/api/health` |
| Dev server | `cd frontend && npm run dev` |
| Build programs | `anchor build` |
| Deploy devnet | `anchor deploy --provider.cluster devnet` |
| Start gateway | `cd gateway && uvicorn app.main:app --reload` |

## Deterministic Workflows (`.claude/scripts/`)

**Project-specific scripts for repeatable automation.**

| Script | Purpose | Exit Codes |
|--------|---------|------------|
| `restart-servers.sh` | Kill + restart frontend (3000) + gateway (8000) | 0=healthy, 1=failed, 2=timeout |

**Convention:**

- Skills check `.claude/scripts/` first before global scripts
- Exit codes: 0=pass, 1=fail, 2=timeout/needs-fix
- Store evidence in `/tmp/` for verification
- After fixing issues, ask: "What should be automated into a script?"

**Automation Trigger:**
After completing any manual workflow (restart servers, test flow, debug session), ask:

- "What part of this workflow can be automated into `.claude/scripts/`?"
- Create/update script with deterministic exit codes
- Reference in CLAUDE.md for future agents

## Config

| File | Purpose |
|------|---------|
| `.claude/config/project.json` | Project settings |
| `.claude/progress/state.json` | Current state |
| `.claude/progress/feature-list.json` | Features |
| `.mcp.json` | MCP servers |

## Issue Resolution Workflow

**CRITICAL ENFORCEMENT:** Context graph is your FIRST tool, not your last. DO NOT skip to fixing.

| Step | Action | Tool | MANDATORY |
| --- | --- | --- | --- |
| 1 | **IMMEDIATELY** query context graph for similar issues | `context_query_traces(query="error description", category=...)` | 🔴 YES |
| 2 | If found: apply learned solution pattern from trace | Review `trace_id`, `decision`, `outcome` | 🔴 YES |
| 3 | If not found: investigate root cause | Debug using browser-testing or code inspection | ✓ |
| 4 | Implement fix and verify no regressions | Test in browser, check console for errors | ✓ |
| 5 | **IMMEDIATELY log trace** (do NOT batch) | `context_store_trace(decision, category, outcome="success")` | 🔴 YES |

**Enforcement Rules:**

- ❌ Do NOT investigate before querying traces
- ❌ Do NOT batch log traces (log after EACH fix)
- ❌ Do NOT treat context graph as post-work documentation
- ✓ DO query traces BEFORE touching code
- ✓ DO log traces IMMEDIATELY after fix completes
- ✓ DO treat context graph as active working memory

**Decision Trace Categories:**

| Category | Use For | Query Pattern | Example Issues |
| --- | --- | --- | --- |
| `frontend` | UI/component issues, rendering, interactions | `query="render error"` | WalletModal overlay, cascading renders, hydration mismatches |
| `hydration` | React server/client mismatches | `query="hydration mismatch"` | Wallet adapter SSR, useEffect issues |
| `framework` | Architecture & pattern decisions | `query="architecture pattern"` | Next.js routing, conditional rendering |
| `testing` | Test automation & validation workflows | `query="test automation"` | Browser testing setup, E2E patterns |
| `css` | Styling and layout issues | `query="layout"` | Theme colors, responsive breakpoints |
| `deployment` | Build/server errors | `query="build error"` | Server crashes, process management |

**When to Query:**

- ❌ Error appears → DO NOT fix immediately
- ✓ Error appears → Query context graph first with error message as search term
- ✓ Same error occurs twice → You should have found the trace the second time
- ✓ Before implementing new pattern → Search if similar pattern exists

**Reflexive Querying (Active Working Memory):**

- Every error → Query before investigating (check for learned patterns first)
- Every fix → Log immediately (don't wait for end-of-session batch)
- Every debug session → Start with context graph search (semantic similarity finds related issues)
- Test if second occurrence of error → You failed if trace wasn't found the first time
- Architectural decision → Query similar decisions before designing

## Architectural Choices Decision Traces

Capture architectural decisions in context graph for institutional knowledge and pattern reuse:

| Step | Action | Tool | When to Use |
| --- | --- | --- | --- |
| 1 | Complete feature implementation | - | After finishing significant work |
| 2 | Identify key architectural choice | - | Framework selection, pattern decision, integration approach |
| 3 | Document decision rationale | - | Why this approach vs alternatives |
| 4 | Store trace with category | `context_store_trace(decision, category, outcome)` | Always mark as "success" for completed work |
| 5 | Link to feature ID | Pass `feature_id` param | Enables querying by feature later |
| 6 | Query future decisions | `context_query_traces(query, category)` | Before making similar architectural choices |

**Capture Trigger Examples:**

| Situation | Example Trace | Category |
| --- | --- | --- |
| Choose animation library | "Selected GSAP + ScrollTrigger over Framer Motion for scroll performance and SVG control" | `frontend` |
| Design system decision | "Integrated cream/charcoal theme using CSS custom properties for dual-system support" | `css` |
| Layout architecture | "Implemented conditional layout pattern: hides navbar on landing, shows on app routes" | `framework` |
| Component patterns | "Converted 1000-line HTML to modular React: logic in hooks, UI in components, styles in CSS" | `frontend` |
| State management | "Chose Zustand over Redux for identity state: simpler API, smaller bundle, sufficient for use cases" | `framework` |
| MCP integration | "Built custom MCP servers for pattern-analyzer and compliance-rules with async processing" | `architecture` |

**Query Examples:**

```bash
# Find animation decisions
context_query_traces(query="animation library", category="frontend")

# Find design system patterns
context_query_traces(query="design system", category="css")

# Find layout patterns
context_query_traces(query="conditional layout", category="framework")

# Find all architectural decisions
context_query_traces(query="architecture", limit=20)
```

**Categories for Architectural Decisions:**

| Category | Use For | Examples |
| --- | --- | --- |
| `frontend` | UI patterns, component architecture, rendering decisions | Custom cursor, scroll animations, reusable hooks |
| `css` | Design system, theming, styling approaches | CSS variables, Tailwind integration, responsive patterns |
| `framework` | Layout patterns, routing, application structure | Conditional rendering, page organization, navigation |
| `architecture` | MCP servers, agent design, system integration | Data flow, communication patterns, service boundaries |
| `testing` | Test strategy, automation patterns, validation approach | Component testing, E2E strategies, verification methods |
| `deployment` | Build strategy, environment setup, release process | Build optimization, environment config, CI/CD choices |
