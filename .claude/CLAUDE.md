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
