#!/bin/bash
# Update feature list status and manage state transitions
# Usage: update-feature.sh <feature_id> <new_status> [next_feature_id] [next_status]
# Exit codes: 0=success, 1=error, 2=validation failed

set -e

FEATURE_LIST=".claude/progress/feature-list.json"

# Validate inputs
if [[ $# -lt 2 ]]; then
    echo "Usage: update-feature.sh <feature_id> <new_status> [next_feature_id] [next_status]"
    echo "Exit codes: 0=success, 1=error, 2=validation failed"
    exit 2
fi

FEATURE_ID="$1"
NEW_STATUS="$2"
NEXT_FEATURE_ID="${3:-}"
NEXT_STATUS="${4:-}"

# Validate feature list exists
if [[ ! -f "$FEATURE_LIST" ]]; then
    echo "ERROR: Feature list not found at $FEATURE_LIST"
    exit 1
fi

# Validate status value
case "$NEW_STATUS" in
    pending|in_progress|completed)
        ;;
    *)
        echo "ERROR: Invalid status '$NEW_STATUS'. Must be: pending, in_progress, completed"
        exit 2
        ;;
esac

# Create backup
cp "$FEATURE_LIST" "${FEATURE_LIST}.bak"

# Update feature status using Python (for JSON parsing)
python3 << PYTHON_EOF
import json
import sys

try:
    with open('$FEATURE_LIST', 'r') as f:
        data = json.load(f)

    # Update current feature
    found = False
    for feature in data['features']:
        if feature['id'] == '$FEATURE_ID':
            old_status = feature['status']
            feature['status'] = '$NEW_STATUS'
            found = True

            # Update next feature if provided
            if '$NEXT_FEATURE_ID':
                for f in data['features']:
                    if f['id'] == '$NEXT_FEATURE_ID':
                        f['status'] = '$NEXT_STATUS'
                        break
            break

    if not found:
        print("ERROR: Feature '$FEATURE_ID' not found")
        sys.exit(1)

    # Recalculate summary
    statuses = [f['status'] for f in data['features']]
    data['summary']['by_status'] = {
        'pending': statuses.count('pending'),
        'in_progress': statuses.count('in_progress'),
        'completed': statuses.count('completed'),
    }

    # Write back
    with open('$FEATURE_LIST', 'w') as f:
        json.dump(data, f, indent=2)

    print("✓ Updated $FEATURE_ID → $NEW_STATUS")
    if '$NEXT_FEATURE_ID':
        print("✓ Updated $NEXT_FEATURE_ID → $NEXT_STATUS")
    print("✓ Summary recalculated")

except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
PYTHON_EOF

if [[ $? -ne 0 ]]; then
    # Restore backup on error
    mv "${FEATURE_LIST}.bak" "$FEATURE_LIST"
    exit 1
fi

# Clean up backup
rm "${FEATURE_LIST}.bak"
exit 0
