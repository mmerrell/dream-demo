#!/usr/bin/env bash
#
# MCP + saucectl Unified Demo Script
#
# Shows the complete workflow:
#   1. MCP-style device discovery (via API)
#   2. saucectl run (Playwright web tests on Sauce Labs)
#   3. pytest run (Appium mobile tests on Sauce Labs RDC)
#   4. MCP-style job analysis (via API)
#
# Prerequisites:
#   - SAUCE_USERNAME and SAUCE_ACCESS_KEY available (env vars or .env file)
#   - saucectl installed
#   - pytest installed with Appium-Python-Client
#
# Usage:
#   export SAUCE_DEVICE_NAME="Google Pixel 8"
#   ./scripts/demo_mcp_saucectl.sh

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

function banner() {
  echo -e "${BLUE}"
  echo "============================================================"
  echo "  $1"
  echo "============================================================"
  echo -e "${NC}"
}

function step() {
  echo -e "${GREEN}▶ $1${NC}"
}

# ─── Source credentials from .env if not already in environment ──
if [[ -z "${SAUCE_USERNAME:-}" || -z "${SAUCE_ACCESS_KEY:-}" ]]; then
  if [[ -f "$PROJECT_ROOT/.env" ]]; then
    set -a
    source "$PROJECT_ROOT/.env"
    set +a
    step "Loaded credentials from .env"
  fi
fi

if [[ -z "${SAUCE_USERNAME:-}" || -z "${SAUCE_ACCESS_KEY:-}" ]]; then
  echo -e "${RED}ERROR: SAUCE_USERNAME and SAUCE_ACCESS_KEY not found in environment or .env${NC}"
  exit 1
fi

banner "STEP 1: MCP Device Discovery"
step "Querying Sauce Labs RDC for available devices..."
python3 scripts/demo_mcp_device_discovery.py

banner "STEP 2: saucectl — Web Tests (Playwright on VDC)"
step "Running Playwright e2e tests via saucectl..."
step "This uploads the tests-playwright/ suite and runs on Windows 11 + Chromium"

# Run saucectl (allow non-zero so we can still show analysis)
saucectl run --config .sauce/config.yml || SAUCECTL_EXIT=$?
SAUCECTL_EXIT=${SAUCECTL_EXIT:-0}

banner "STEP 3: Mobile Tests (pytest + Appium on RDC)"
step "Running Appium mobile tests on real device: ${SAUCE_DEVICE_NAME:-Google Pixel 8}"

# Run a subset of mobile tests
cd tests-e2e
pytest test_android_app.py -v -k "test_auth_screen_elements_visible" || PYTEST_EXIT=$?
PYTEST_EXIT=${PYTEST_EXIT:-0}
cd "$PROJECT_ROOT"

banner "STEP 4: MCP Job Analysis"
step "Fetching recent jobs from Sauce Labs API..."
python3 -c "
import os, requests
auth = (os.getenv('SAUCE_USERNAME'), os.getenv('SAUCE_ACCESS_KEY'))
resp = requests.get('https://api.us-west-1.saucelabs.com/v1/rdc/jobs', auth=auth, params={'limit': 3}, timeout=15)
jobs = resp.json().get('jobs', [])
print(f'\\nRecent RDC jobs: {len(jobs)}')
for j in jobs:
    status = 'PASSED' if j.get('passed') else 'FAILED'
    icon = '✅' if j.get('passed') else '❌'
    print(f'  {icon} {status} — {j.get(\"name\", \"Unnamed\")} on {j.get(\"device_name\", \"?\")}')
    print(f'     View: {j.get(\"web_url\", \"N/A\")}')
"

banner "Demo Complete"
echo -e "${GREEN}Summary:${NC}"
echo "  • Device discovery via MCP-style API query ✓"
echo "  • Web tests executed via saucectl (Playwright) ✓"
echo "  • Mobile tests executed via pytest (Appium + RDC) ✓"
echo "  • Job results fetched via API ✓"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  • Open Sauce Labs dashboard to view detailed results"
echo "  • Ask Claude Desktop: 'Show my recent test failures'"
echo "  • Ask Gemini CLI: 'Get logs for failed job XYZ'"
