#!/bin/bash
# Sauce MCP Integration Verification Script
# Checks that sauce-api-mcp servers are installed and configs are in place

echo "=== Sauce Labs MCP Integration Verification ==="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS=0
FAIL=0
WARN=0

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASS++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAIL++))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARN++))
}

# 1. Check if sauce-api-mcp executables exist
echo "1. Checking MCP server installation..."
if which sauce-api-mcp > /dev/null 2>&1; then
    check_pass "sauce-api-mcp found in PATH ($(which sauce-api-mcp))"
else
    check_fail "sauce-api-mcp NOT found in PATH"
fi

if which sauce-api-mcp-rdc > /dev/null 2>&1; then
    check_pass "sauce-api-mcp-rdc found in PATH ($(which sauce-api-mcp-rdc))"
else
    check_fail "sauce-api-mcp-rdc NOT found in PATH"
fi

# 2. Check environment variables
echo ""
echo "2. Checking environment variables..."
if [ -n "$SAUCE_USERNAME" ]; then
    check_pass "SAUCE_USERNAME is set (value: ${SAUCE_USERNAME:0:20}...)"
else
    check_warn "SAUCE_USERNAME not set in environment"
fi

if [ -n "$SAUCE_ACCESS_KEY" ]; then
    check_pass "SAUCE_ACCESS_KEY is set (value: ${SAUCE_ACCESS_KEY:0:10}...)"
else
    check_warn "SAUCE_ACCESS_KEY not set in environment"
fi

# 3. Check Claude Desktop config
echo ""
echo "3. Checking Claude Desktop configuration..."
CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
if [ -f "$CLAUDE_CONFIG" ]; then
    check_pass "Claude config exists at $CLAUDE_CONFIG"
    if grep -q "sauce-api-mcp-core" "$CLAUDE_CONFIG" 2>/dev/null; then
        check_pass "Claude config contains sauce-api-mcp-core server"
    else
        check_fail "sauce-api-mcp-core not found in Claude config"
    fi
    if grep -q "sauce-api-mcp-rdc" "$CLAUDE_CONFIG" 2>/dev/null; then
        check_pass "Claude config contains sauce-api-mcp-rdc server"
    else
        check_fail "sauce-api-mcp-rdc not found in Claude config"
    fi
else
    check_fail "Claude config not found at $CLAUDE_CONFIG"
fi

# 4. Check Gemini CLI config
echo ""
echo "4. Checking Gemini CLI configuration..."
GEMINI_CONFIG="$HOME/.gemini/settings.json"
if [ -f "$GEMINI_CONFIG" ]; then
    check_pass "Gemini config exists at $GEMINI_CONFIG"
    if grep -q "sauce-api-mcp" "$GEMINI_CONFIG" 2>/dev/null; then
        check_pass "Gemini config contains MCP server entries"
    else
        check_fail "MCP servers not found in Gemini config"
    fi
else
    check_fail "Gemini config not found at $GEMINI_CONFIG"
fi

# 5. Check project .env
echo ""
echo "5. Checking project .env file..."
PROJECT_ENV="/Users/adam.toth-fejel/Documents/GitHub/dream-demo/.env"
if [ -f "$PROJECT_ENV" ]; then
    check_pass "Project .env exists"
    if grep -q "SAUCE_USERNAME" "$PROJECT_ENV" 2>/dev/null; then
        check_pass "Project .env contains SAUCE_USERNAME"
    else
        check_warn "SAUCE_USERNAME missing from .env (optional if set globally)"
    fi
    if grep -q "SAUCE_ACCESS_KEY" "$PROJECT_ENV" 2>/dev/null; then
        check_pass "Project .env contains SAUCE_ACCESS_KEY"
    else
        check_warn "SAUCE_ACCESS_KEY missing from .env (optional if set globally)"
    fi
else
    check_warn "Project .env not found (optional if env vars set globally)"
fi

# 6. Summary
echo ""
echo "=== Summary ==="
echo -e "Passed: ${GREEN}$PASS${NC}"
echo -e "Failed: ${RED}$FAIL${NC}"
if [ $WARN -gt 0 ]; then
    echo -e "Warnings: ${YELLOW}$WARN${NC}"
fi

echo ""
if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✓ All critical checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Restart Claude Desktop and/or Gemini CLI"
    echo "2. Ask your AI assistant: 'What devices are available in Sauce Labs?'"
    echo "3. Run an RDC test: pytest tests-e2e/test_android_app.py"
    echo "4. Query results: 'Show me my recent test jobs'"
    echo ""
    echo "See MCP_SETUP.md for detailed usage examples and troubleshooting."
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Review configuration.${NC}"
    echo "See MCP_SETUP.md for troubleshooting."
    exit 1
fi

