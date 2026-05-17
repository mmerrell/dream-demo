#!/usr/bin/env bash
# Trigger Sauce AI test generation and poll until completion, then optionally run the generated test case
set -euo pipefail

if [ -z "${SAUCE_USERNAME:-}" ] || [ -z "${SAUCE_ACCESS_KEY:-}" ]; then
  echo "SAUCE_USERNAME or SAUCE_ACCESS_KEY not set"
  exit 1
fi

API_HOST="https://api.${SAUCE_REGION:-us-west-1}.saucelabs.com"

NAME="$1"
INTENT="$2"
BUILD_NAME="${3:-DreamDemo-AI-Run-$(date +%s)}"

if [ -z "$NAME" ] || [ -z "$INTENT" ]; then
  echo "Usage: $0 <test-name> <nl-intent> [build-name]"
  exit 1
fi

# 1. Request generation
PAYLOAD=$(jq -n --arg name "$NAME" --arg intent "$INTENT" '{name:$name, runSettings:{target:{capabilities:{browserName:"chrome",platformName:"Windows 11",browserVersion:"latest"}}, testUrl:"https://localhost:3000/"}, promptSettings:{intent:$intent}}')
RESP=$(curl -s -u "$SAUCE_USERNAME:$SAUCE_ACCESS_KEY" -H "Content-Type: application/json" -d "$PAYLOAD" "$API_HOST/v1/ai-authoring/testcases/generate")
TASK_ID=$(echo "$RESP" | jq -r '.data.taskId')

echo "Generation task: $TASK_ID"

# 2. Poll status
while true; do
  sleep 3
  STATUS_RESP=$(curl -s -u "$SAUCE_USERNAME:$SAUCE_ACCESS_KEY" "$API_HOST/v1/ai-authoring/testcases/generate/$TASK_ID")
  STATUS=$(echo "$STATUS_RESP" | jq -r '.data.status')
  echo "Status: $STATUS"
  if [ "$STATUS" = "COMPLETED" ]; then
    TESTCASE_ID=$(echo "$STATUS_RESP" | jq -r '.data.testCaseId')
    echo "Generated test case: $TESTCASE_ID"
    break
  fi
  if [ "$STATUS" = "FAILED" ]; then
    echo "Generation failed: $(echo $STATUS_RESP | jq -r '.data.error')"
    exit 1
  fi
done

# 3. Trigger run
RUN_RESP=$(curl -s -u "$SAUCE_USERNAME:$SAUCE_ACCESS_KEY" -H "Content-Type: application/json" -d "{\"buildName\": \"$BUILD_NAME\"}" "$API_HOST/v1/ai-authoring/testcases/$TESTCASE_ID/run")
echo "$RUN_RESP" | jq .
