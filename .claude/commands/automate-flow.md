# Automate Flow

Analyze the completed workflow and identify repeatable patterns that should be converted into deterministic scripts.

## Workflow

1. **Review the session**: What workflow was just completed?
2. **Identify automation opportunities**: Look for steps that were:
   - Repeated multiple times
   - Manual and error-prone
   - High token cost (could be scripted)
   - Required for future sessions
3. **Assess token efficiency of current process** (see below)
4. **Evaluate value**: Is the automation worth scripting?
5. **Create or log**:
   - **If YES**: Create script in `.claude/scripts/`, update README.md
   - **If NO**: Log to context graph as "not worth automating yet"

## Token Efficiency Assessment

Before creating a script, analyze the **current process cost**:

| Current Process | Context Cost | Script Value |
|---|---|---|
| Already uses `token-efficient` MCP (execute_code, process_csv, etc.) | ~0 tokens | ❌ No token savings |
| Loads raw data/files into context | 200-500+ tokens | ✅ High - script can eliminate loading |
| Multi-step manual bash operations | 100-300 tokens | ✅ Medium-High - consolidates into one operation |
| Manual Python with data in context | 150-400+ tokens | ✅ High - wrap in script to avoid context loading |

**Decision Framework:**

Script is worth creating if:

- **Token savings:** `(Tokens saved per use × expected total uses) - (script creation overhead ~200) > 0`
  - AND current process is expensive (not already using token-efficient MCP)
- **Operational value:** Process used >3 times per session OR prevents critical errors
  - Even if token savings are marginal, operational benefit justifies it

**Examples:**

| Workflow | Current Cost | Script Benefit | Decision |
|---|---|---|---|
| Update feature list (using token-efficient MCP) | ~0 tokens | Adds bash wrapper, no token savings | ❌ Skip - already efficient |
| Restart servers (kill + start 2 services) | 30-60s manual + error prone | Consolidates steps, health checks | ✅ Keep - operational value |
| Load CSV, grep logs, process output | 200+ tokens in context | Can run entirely in sandbox | ✅ Create - high token savings |

## Script Convention

Scripts in `.claude/scripts/` must follow:

- Exit codes: 0=pass, 1=fail, 2=timeout/needs-fix
- Store evidence in `/tmp/` for verification
- Update `.claude/scripts/README.md` with concise usage

## Example Output

```
Workflow: Server restart + browser testing
Repeated steps:
1. Kill processes on ports 3000, 8000
2. Start frontend (npm run dev)
3. Start gateway (uvicorn)
4. Wait for health checks

Decision: Create .claude/scripts/restart-servers.sh
Value: Saves 30-60s per test session, eliminates manual errors
```

## Skill Improvement Check

Also evaluate: Does `browser-testing` skill need updates?

**Principle:** Keep skill **project-agnostic** (applicable to any project).

**Update skill if:**

- Missing generic workflow step (applies to all browser testing)
- Token inefficiency in instructions
- MCP tool usage pattern that's universally useful
- Missing best practice

**DO NOT update skill with:**

- Project-specific URLs, ports, or configs
- Project-specific script names
- Anything that only helps this project

**If skill update is needed:**

1. Document the specific improvement
2. Ask user: "browser-testing skill update needed: [description]. Apply?"
3. If user approves: Use `skill-creator` to update the skill
4. If user declines: Log to context graph as "suggested improvement"

## Context Graph Log

If not worth automating, store trace:

```bash
context_store_trace(
  decision="Analyzed [workflow]: automation not justified yet. Reason: [reason]",
  category="testing",
  outcome="pending"
)
```
