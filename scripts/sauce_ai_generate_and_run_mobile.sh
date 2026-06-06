#!/usr/bin/env bash
# Trigger Sauce AI test generation for MOBILE (Appium) and run on RDC
set -euo pipefail

if [ -z "${SAUCE_USERNAME:-}" ] || [ -z "${SAUCE_ACCESS_KEY:-}" ]; then
  echo "SAUCE_USERNAME or SAUCE_ACCESS_KEY not set"
  exit 1
fi

API_HOST="https://api.${SAUCE_REGION:-us-west-1}.saucelabs.com"

NAME="$1"
INTENT="$2"
BUILD_NAME="${3:-DreamDemo-AI-Mobile-$(date +%s)}"
APP_ID="${SAUCE_APP_ID:-storage:filename=flowershop.apk}"
DEVICE_NAME="${SAUCE_DEVICE_NAME:-Google Pixel 8}"
PLATFORM_VERSION="${SAUCE_PLATFORM_VERSION:-14}"

if [ -z "$NAME" ] || [ -z "$INTENT" ]; then
  echo "Usage: $0 <test-name> <nl-intent> [build-name]"
  exit 1
fi

TUNNEL_NAME="${SAUCE_TUNNEL_NAME:-${SAUCE_SC_TUNNEL:-}}"

# Build mobile capabilities
if [ -n "$TUNNEL_NAME" ]; then
  PAYLOAD=$(jq -n \
    --arg name "$NAME" \
    --arg intent "$INTENT" \
    --arg app "$APP_ID" \
    --arg device "$DEVICE_NAME" \
    --arg version "$PLATFORM_VERSION" \
    --arg tunnel "$TUNNEL_NAME" \
    '{
      name: $name,
      runSettings: {
        target: {
          capabilities: {
            platformName: "Android",
            deviceName: $device,
            platformVersion: $version,
            app: $app,
            automationName: "UiAutomator2",
            "sauce:options": {
              tunnelIdentifier: $tunnel,
              deviceOrientation: "PORTRAIT"
            }
          }
        }
      },
      promptSettings: { intent: $intent }
    }')
else
  PAYLOAD=$(jq -n \
    --arg name "$NAME" \
    --arg intent "$INTENT" \
    --arg app "$APP_ID" \
    --arg device "$DEVICE_NAME" \
    --arg version "$PLATFORM_VERSION" \
    '{
      name: $name,
      runSettings: {
        target: {
          capabilities: {
            platformName: "Android",
            deviceName: $device,
            platformVersion: $version,
            app: $app,
            automationName: "UiAutomator2",
            "sauce:options": {
              deviceOrientation: "PORTRAIT"
            }
          }
        }
      },
      promptSettings: { intent: $intent }
    }')
fi

echo "Payload: $PAYLOAD"

# 1. Request generation
RESP=$(curl -s -u "$SAUCE_USERNAME:$SAUCE_ACCESS_KEY" -H "Content-Type: application/json" -d "$PAYLOAD" "$API_HOST/v1/ai-authoring/testcases/generate")
echo "Generate response: $RESP"
TASK_ID=$(echo "$RESP" | jq -r '.data.taskId // empty')

if [ -z "$TASK_ID" ] || [ "$TASK_ID" = "null" ]; then
  echo "Failed to start generation: $RESP"
  exit 1
fi

echo "Generation task: $TASK_ID"

# 2. Poll status
while true; do
  sleep 5
  STATUS_RESP=$(curl -s -u "$SAUCE_USERNAME:$SAUCE_ACCESS_KEY" "$API_HOST/v1/ai-authoring/testcases/generate/$TASK_ID")
  STATUS=$(echo "$STATUS_RESP" | jq -r '.data.status // "UNKNOWN"')
  echo "Status: $STATUS"
  if [ "$STATUS" = "COMPLETED" ]; then
    TESTCASE_ID=$(echo "$STATUS_RESP" | jq -r '.data.testCaseId // empty')
    echo "Generated test case: $TESTCASE_ID"
    break
  fi
  if [ "$STATUS" = "FAILED" ]; then
    echo "Generation failed: $(echo "$STATUS_RESP" | jq -r '.data.error // .message // "Unknown error"')"
    exit 1
  fi
done

# 3. Trigger run
if [ -n "$TUNNEL_NAME" ]; then
  RUN_PAYLOAD=$(jq -n --arg build "$BUILD_NAME" --arg tunnel "$TUNNEL_NAME" '{buildName: $build, scTunnelName: $tunnel}')
else
  RUN_PAYLOAD=$(jq -n --arg build "$BUILD_NAME" '{buildName: $build}')
fi
RUN_RESP=$(curl -s -u "$SAUCE_USERNAME:$SAUCE_ACCESS_KEY" -H "Content-Type: application/json" -d "$RUN_PAYLOAD" "$API_HOST/v1/ai-authoring/testcases/$TESTCASE_ID/run")
echo "$RUN_RESP" | jq .