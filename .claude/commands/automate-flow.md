# Automate Flow

Analyze the completed workflow and identify repeatable patterns that should be converted into deterministic scripts.

## Workflow

1. **Review the session**: What workflow was just completed?
2. **Identify automation opportunities**: Look for steps that were:
   - Repeated multiple times
   - Manual and error-prone
   - High token cost (could be scripted)
   - Required for future sessions
3. **Evaluate value**: Is the automation worth scripting?
4. **Create or log**:
   - **If YES**: Create script in `.claude/scripts/`, update README.md
   - **If NO**: Log to context graph as "not worth automating yet"

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
