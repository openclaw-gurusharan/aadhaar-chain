# Automate Flow

Identify repeatable patterns from completed workflow and decide: automate or skip?

## Steps

1. Review session workflow
2. Find repeated steps (manual, error-prone, high token cost)
3. Assess current process cost (see decision framework below)
4. Decide: create script or log to context graph

## Decision Framework

Create script if:

- **Token savings:** `(tokens saved/use × total uses) - 200 > 0` AND current process costs tokens
- **Operational value:** Used >3x/session OR prevents errors

| Current Process | Cost | Script Worth It? |
| --- | --- | --- |
| Already using token-efficient MCP | ~0 | ❌ Skip |
| Manual multi-step bash/python | 100-500 | ✅ Yes |
| Loads raw data to context | 200-500 | ✅ Yes |

Examples: ❌ update-feature (already efficient) | ✅ restart-servers (operational consolidation) | ✅ CSV processing (avoids context loading)

## Script Requirements

- Exit codes: 0=pass, 1=fail, 2=timeout
- Store evidence in `/tmp/`
- Update `.claude/scripts/README.md`

## Skill Improvement Check

  Evaluate if any skill was used in current session workflow, and
  does it need any update to make it efficient and better.

**Update skill if:**

- Missing generic workflow step (applies to all projects)
- Token inefficiency in instructions
- MCP tool usage pattern that's universally useful
- Missing best practice

**DO NOT update with:**

- Project-specific URLs, ports, configs
- Project-specific script names

**If update needed:**

1. Document the improvement
2. Ask user: "Skill update needed: [description]. Apply?"
3. If approved: Use `skill-creator`

## If Not Worth Automating

Log to context graph:

```bash
context_store_trace(
  decision="Analyzed [workflow]: automation not justified. Reason: [reason]",
  category="testing",
  outcome="pending"
)
```
