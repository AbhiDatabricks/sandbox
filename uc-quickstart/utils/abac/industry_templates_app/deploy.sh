#!/usr/bin/env bash
set -euo pipefail

# Deploy this repo folder as a Databricks App with a timestamped name.
# Convention (going forward):
#   <base>-<YYYYMMDD-HHMM>
#
# Example:
#   abacindustry-20260106-1247

BASE_NAME="${1:-abacindustry}"
PROFILE="${DATABRICKS_CONFIG_PROFILE:-DEFAULT}"

TS="$(date +%Y%m%d-%H%M)"
APP_NAME="${BASE_NAME}-${TS}"

# Use current CLI user to build a per-user workspace source path (avoids collisions).
set +e
ME_JSON="$(databricks current-user me --profile "$PROFILE" --output json 2>&1)"
ME_EXIT=$?
set -e

if [ $ME_EXIT -ne 0 ]; then
  echo "❌ Databricks CLI is not authenticated for profile '${PROFILE}'."
  echo ""
  echo "Run:"
  echo "  databricks auth login --profile ${PROFILE}"
  echo ""
  echo "Then re-run:"
  echo "  ./deploy.sh ${BASE_NAME}"
  echo ""
  echo "CLI error:"
  echo "${ME_JSON}"
  exit 1
fi

CURRENT_USER="$(printf '%s' "$ME_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("userName",""))')"
if [ -z "$CURRENT_USER" ]; then
  echo "❌ Could not determine current user via Databricks CLI output. Are you logged in for profile '$PROFILE'?"
  exit 1
fi

SOURCE_CODE_PATH="/Workspace/Users/${CURRENT_USER}/apps/${APP_NAME}"

echo "🚀 Deploying Databricks App"
echo "  - profile: ${PROFILE}"
echo "  - name:    ${APP_NAME}"
echo "  - path:    ${SOURCE_CODE_PATH}"

databricks workspace mkdirs "$SOURCE_CODE_PATH" --profile "$PROFILE"
databricks sync --full . "$SOURCE_CODE_PATH" --profile "$PROFILE" >/dev/null 2>&1

# Create app if needed, then deploy
if ! databricks apps get "$APP_NAME" --profile "$PROFILE" >/dev/null 2>&1; then
  # Note: `apps create` no longer accepts `--source-code-path` in newer CLI versions.
  # We create the app first, then deploy code with `apps deploy --source-code-path`.
  databricks apps create "$APP_NAME" --profile "$PROFILE"
fi

databricks apps deploy "$APP_NAME" --source-code-path "$SOURCE_CODE_PATH" --profile "$PROFILE"

echo "✅ Deployed: ${APP_NAME}"
databricks apps get "$APP_NAME" --profile "$PROFILE" --output json | python3 -c 'import json,sys; d=json.load(sys.stdin); print("🌐 URL:", d.get("url","(not available)"))'

