#!/usr/bin/env bash
# Trigger Sauce AI test generation for WEB and run
set -euo pipefail

if [ -z "${SAUCE_USERNAME:-}" ] || [ -z "${SAUCE_ACCESS_KEY:-}" ]; then
  echo "SAUCE_USERNAME or SAUCE_ACCESS_KEY not set"
  exit 1
fi

API_HOST="https://api.${SAUCE_REGION:-us-west-1}.saucelabs.com"

NAME="$1"
INTENT="$2"
BUILD_NAME="${3:-DreamDemo-AI-Web-$(date +%s)}"

if [ -z "$NAME" ] || [ -z "$INTENT" ]; then
  echo "Usage: $0 <test-name> <nl-intent> [build-name]"
  exit 1
fi

# 1. Request generation
PAYLOAD=$(jq -n --arg name "$NAME" --arg intent "$INTENT" --arg tunnel "${SAUCE_TUNNEL_NAME:-}" '{
  name: $name,
  runSettings: {
    target: {
      capabilities: {
        browserName: "chrome",
        platformName: "Windows 11",
        browserVersion: "latest",
        "goog:chromeOptions": {
          args: ["--disable-notifications", "--disable-geolocation", "--disable-features=PrivacySandbox,MediaRouter,OptimizationHints,Translate,PermissionBubble,SitePerProcess", "--disable-popup-blocking", "--disable-infobars"],
          prefs: {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_setting_values.geolocation": 2,
            "profile.default_content_setting_values.media_stream": 2,
            "profile.default_content_setting_values.media_stream_mic": 2,
            "profile.default_content_setting_values.media_stream_camera": 2,
            "profile.default_content_setting_values.protocol_handlers": 2,
            "profile.default_content_setting_values.serial": 2,
            "profile.default_content_setting_values.usb": 2,
            "profile.default_content_setting_values.hid": 2,
            "profile.default_content_setting_values.bluetooth": 2,
            "profile.default_content_setting_values.file_system": 2,
            "profile.default_content_setting_values.window_placement": 2,
            "profile.default_content_setting_values.popups": 2
          }
        },
        "sauce:options": {
          "tunnelIdentifier": $tunnel
        }
      }
    },
    testUrl: "http://localhost:3000/"
  },
  promptSettings: { intent: $intent }
}')
RESP=$(curl -s -u "$SAUCE_USERNAME:$SAUCE_ACCESS_KEY" -H "Content-Type: application/json" -d "$PAYLOAD" "$API_HOST/v1/ai-authoring/testcases/generate")
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
RUN_PAYLOAD=$(jq -n --arg build "$BUILD_NAME" '{buildName: $build}')
RUN_RESP=$(curl -s -u "$SAUCE_USERNAME:$SAUCE_ACCESS_KEY" -H "Content-Type: application/json" -d "$RUN_PAYLOAD" "$API_HOST/v1/ai-authoring/testcases/$TESTCASE_ID/run")
echo "$RUN_RESP" | jq .

# Extract job ID and wait for completion
JOB_ID=$(echo "$RUN_RESP" | jq -r '.data.jobs[0].id // empty')
if [ -n "$JOB_ID" ]; then
  echo ""
  echo "Job ID: $JOB_ID"
  echo "Waiting ~90s for test to complete before shutting down tunnel..."
  sleep 90
  echo "Done waiting. Check https://app.saucelabs.com/tests/ for results."
fi