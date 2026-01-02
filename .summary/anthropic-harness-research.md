# Anthropic Long-Running Agent Research

Source: <https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents>

## Key Failure Modes

| Problem | Initializer Solution | Coding Agent Solution |
|---------|---------------------|----------------------|
| Declares victory too early | Feature list file | Read feature list, work on one feature |
| Leaves broken state | Git repo + progress notes | Start by testing dev server, fix bugs first |
| Marks features done prematurely | Feature list file | Self-verify, only mark as passing after testing |
| Spends time figuring out how to run app | Write init.sh | Read init.sh |

## Critical: Test Basic Functionality FIRST

Before implementing new features:

1. Start dev server (init.sh)
2. Run basic e2e test via browser automation
3. If tests fail → enter FIX_BROKEN state immediately

## Session Start Protocol

```
1. pwd → see working directory
2. git log → recent work
3. Read feature-list.json → choose next feature
4. Run init.sh → start dev server
5. TEST BASIC FUNCTIONALITY FIRST ← Critical!
6. Only then: implement new feature
```

## Feature List Format

```json
{
  "category": "functional",
  "description": "New chat button creates a fresh conversation",
  "steps": [...],
  "passes": false
}
```

**Key Rule**: Only edit `passes` field, never remove tests.

## Browser Automation is Critical

> "Claude tended to make code changes and do testing... but would fail to recognize that the feature didn't work end-to-end."

**Solution**: Explicit prompting to use browser automation tools (Puppeteer/Chrome MCP) to test as a human would.

## Gap in Current System

| Component | Status | Action |
|-----------|--------|--------|
| feature-list.json | ✅ Exists | - |
| session-state.json | ✅ Exists | - |
| session-entry.sh | ✅ Exists | Add "test first" enforcement |
| browser-testing skill | ✅ Exists | Require for UI features |
| **Test before new work** | ❌ Missing | **Add to session-entry** |
| **Block passes=true without proof** | ❌ Missing | **Add hook** |

## To Implement Later

1. Update `session-entry.sh` to require basic e2e test
2. Create hook that blocks `tested: true` without verification evidence
3. Add browser automation requirement for all UI feature changes
4. Only mark `passes: true` after actual browser verification
