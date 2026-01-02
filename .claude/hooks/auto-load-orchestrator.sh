#!/bin/bash
# auto-load-orchestrator.sh
#
# UserPromptSubmit hook that reminds Claude to load orchestrator skill
# on first prompt of each session.
#
# Uses a session marker file to avoid repeating on every prompt.

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
SESSION_MARKER="/tmp/.claude-orchestrator-loaded-$$"

# Check if orchestrator was already loaded this session
# Use parent PID to track the Claude session
PARENT_PID=$(ps -o ppid= -p $$ 2>/dev/null | tr -d ' ')
SESSION_MARKER="/tmp/.claude-orchestrator-loaded-${PARENT_PID:-unknown}"

if [[ -f "$SESSION_MARKER" ]]; then
    # Already loaded this session, exit silently
    exit 0
fi

# Mark as loaded for this session
touch "$SESSION_MARKER"

# Read session-entry output if available
STATE_FILE="$PROJECT_DIR/.claude/progress/state.json"
CURRENT_STATE="UNKNOWN"
if [[ -f "$STATE_FILE" ]]; then
    CURRENT_STATE=$(jq -r '.state // "UNKNOWN"' "$STATE_FILE" 2>/dev/null || echo "UNKNOWN")
fi

# Output reminder for Claude (this appears in hook output)
cat << EOF
<system-reminder>
SESSION START PROTOCOL:
1. Load orchestrator skill: /orchestrator
2. Current state: $CURRENT_STATE
3. Run check-state.sh if needed
4. Load appropriate skill for state (init/implement/test/complete)
</system-reminder>
EOF

exit 0
