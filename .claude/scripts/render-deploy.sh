#!/bin/bash
# Deploy web service to Render with automated setup
# Usage: ./.claude/scripts/render-deploy.sh [--dry-run]

set -e

# === Configuration (tailored during init) ===
SERVICE_NAME="identity-aadhar"
RUNTIME=""
BUILD_CMD=""
START_CMD=""
REPO=""
BRANCH=""
ROOT_DIR=""
PLAN="starter"
REGION="oregon"

# Parse arguments
DRY_RUN=false
for arg in "$@"; do
    case $arg in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --name=*)
            SERVICE_NAME="${arg#*=}"
            shift
            ;;
        --repo=*)
            REPO="${arg#*=}"
            shift
            ;;
        --plan=*)
            PLAN="${arg#*=}"
            shift
            ;;
        --region=*)
            REGION="${arg#*=}"
            shift
            ;;
    esac
done

echo "=== Render Deployment ==="
echo ""

# === 1. Pre-flight Security Check ===
echo "1. Running security check..."
if [ -f ~/.claude/skills/render-deploy/scripts/check-env.sh ]; then
    if ~/.claude/skills/render-deploy/scripts/check-env.sh .env 2>/dev/null; then
        echo "✓ Security check passed"
    else
        echo "⚠️  Security check found issues"
    fi
else
    echo "⚠️  Security check script not found, skipping..."
fi
echo ""

# === 2. Validate Required Variables ===
echo "2. Validating configuration..."
MISSING=false

if [ -z "$SERVICE_NAME" ]; then
    echo "❌ SERVICE_NAME not set"
    MISSING=true
fi

if [ -z "$RUNTIME" ]; then
    echo "❌ RUNTIME not set"
    MISSING=true
fi

if [ -z "$START_CMD" ] && [ "$RUNTIME" != "docker" ]; then
    echo "❌ START_CMD not set (required for non-Docker)"
    MISSING=true
fi

if [ -z "$REPO" ]; then
    echo "❌ RENDER_REPO not set"
    echo "   Set with: --repo=https://github.com/user/repo"
    MISSING=true
fi

if [ "$MISSING" = true ]; then
    echo ""
    echo "❌ Configuration incomplete. Edit this script to set required variables."
    exit 2
fi

echo "✓ Configuration validated:"
echo "   Service: $SERVICE_NAME"
echo "   Runtime: $RUNTIME"
echo "   Region:  $REGION"
echo "   Plan:    $PLAN"
echo ""

# === 3. Detect Deployment Type ===
echo "3. Determining deployment type..."
DEPLOY_TYPE="web_service"

if [ "$RUNTIME" = "docker" ]; then
    echo "✓ Docker deployment detected"
elif [ -f "package.json" ] && grep -q '"vite"' package.json 2>/dev/null; then
    DEPLOY_TYPE="static_site"
    echo "✓ Static site detected (Vite)"
elif [ -f "package.json" ] && grep -q '"react-scripts"' package.json 2>/dev/null; then
    DEPLOY_TYPE="static_site"
    echo "✓ Static site detected (Create React App)"
else
    echo "✓ Web service deployment"
fi
echo ""

# === 4. Dry Run or Deploy ===
if [ "$DRY_RUN" = true ]; then
    echo "=== Dry Run Configuration ==="
    echo ""
    echo "Service Name:  $SERVICE_NAME"
    echo "Deployment:    $DEPLOY_TYPE"
    echo "Runtime:       $RUNTIME"
    echo "Build Command: ${BUILD_CMD:-<none>}"
    echo "Start Command: ${START_CMD:-<Docker CMD>}"
    echo "Repository:    $REPO"
    echo "Branch:        ${BRANCH:-<default>}"
    echo "Root Dir:      ${ROOT_DIR:-<none>}"
    echo "Region:        $REGION"
    echo "Plan:          $PLAN"
    echo ""
    echo "To deploy: $0"
    exit 0
fi

# === 5. Deploy via MCP ===
echo "4. Deploying to Render..."
echo "   This requires the Render MCP server to be configured."
echo ""

# Check if MCP tools are available (this would be called by Claude with MCP)
echo "MCP deployment commands to execute:"
echo ""

if [ "$DEPLOY_TYPE" = "static_site" ]; then
    # Static site deployment
    PUBLISH_PATH="${ROOT_DIR}dist"
    echo "mcp__render__create_static_site:"
    echo "  name: $SERVICE_NAME"
    echo "  buildCommand: $BUILD_CMD"
    echo "  publishPath: $PUBLISH_PATH"
    echo "  repo: $REPO"
    if [ -n "$BRANCH" ]; then
        echo "  branch: $BRANCH"
    fi
else
    # Web service deployment
    echo "mcp__render__create_web_service:"
    echo "  name: $SERVICE_NAME"
    echo "  runtime: $RUNTIME"
    echo "  buildCommand: ${BUILD_CMD:-<default>}"
    echo "  startCommand: $START_CMD"
    echo "  repo: $REPO"
    echo "  region: $REGION"
    echo "  plan: $PLAN"
    if [ -n "$BRANCH" ]; then
        echo "  branch: $BRANCH"
    fi
    if [ -n "$ROOT_DIR" ]; then
        echo "  (Set root directory via Render dashboard: $ROOT_DIR)"
    fi
fi
echo ""

echo "=== Next Steps ==="
echo ""
echo "1. Visit https://dashboard.render.com to view deployment"
echo "2. Set environment variables in Render dashboard"
echo "3. Monitor logs: dashboard > service > logs"
echo ""
echo "Deployment configuration prepared!"
