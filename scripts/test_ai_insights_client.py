#!/usr/bin/env python3
"""
Test client for the Sauce AI Insights Gateway.

Usage against the mock server:
  python3 scripts/test_ai_insights_client.py

Usage against the real Sauce Labs API:
  SAUCE_USERNAME="..." SAUCE_ACCESS_KEY="..." \
    python3 scripts/test_ai_insights_client.py \
    --host wss://api.us-west-1.saucelabs.com

The client connects via WebSocket, sends the same prompt captured in
NetworkCalls/TestInsightsApi.har, and validates the streamed responses.
"""
import argparse
import asyncio
import base64
import json
import os
import sys
import uuid
from urllib.parse import urljoin, urlparse, urlunparse

try:
    import websockets
except ImportError:
    print("ERROR: 'websockets' package is required.")
    print("Install it with:  pip install websockets")
    sys.exit(1)


PROMPT = (
    "What is the Error Rate trend over the past seven days "
    "and show me the top five errors by count."
)


def _build_ws_url(host: str, correlation_id: str, username: str = "", access_key: str = "") -> str:
    base = host.rstrip("/")
    if base.startswith("http://"):
        base = base.replace("http://", "ws://", 1)
    elif base.startswith("https://"):
        base = base.replace("https://", "wss://", 1)

    # Inject Basic auth credentials into the URL if provided
    if username and access_key:
        parsed = urlparse(base)
        netloc = f"{username}:{access_key}@{parsed.netloc}"
        base = urlunparse(parsed._replace(netloc=netloc))

    return f"{base}/ai-assistant-gateway/v1/chat/ws/{correlation_id}"


async def run_test(host: str, prompt: str = PROMPT, timeout: float = 30.0,
                   username: str = "", access_key: str = ""):
    correlation_id = str(uuid.uuid4())
    uri = _build_ws_url(host, correlation_id, username, access_key)
    # Mask credentials in printed URL
    safe_uri = uri.replace(f"{username}:{access_key}@", "***:***@") if username else uri
    print(f"Connecting to {safe_uri} ...")

    additional_headers = {
        "Origin": "https://app.saucelabs.com",
    }

    # For real Sauce Labs, the HAR showed no explicit auth headers on the WS
    # upgrade; auth is handled via cookies from the web UI session.  When
    # connecting programmatically, Basic auth in the URL is the standard
    # approach for Sauce Labs APIs, but the AI assistant gateway may
    # restrict access to browser sessions only.

    messages_received = []
    try:
        async with websockets.connect(uri, additional_headers=additional_headers) as ws:
            print("[CLIENT] Connected.\n")

            # 1. Send prompt
            message_id = str(uuid.uuid4())
            payload = {
                "correlation_id": correlation_id,
                "type": "prompt",
                "name": "send_prompt",
                "message_id": message_id,
                "payload": {
                    "timezone": "America/Los_Angeles",
                    "prompt": prompt,
                    "filters": {
                        "start": "2026-04-22T07:00:00.000Z",
                        "end": "2026-05-22T07:00:00.000Z"
                    }
                }
            }
            await ws.send(json.dumps(payload))
            print(f"[CLIENT] SENT prompt: {prompt[:60]}...\n")

            # 2. Receive streamed responses until DONE
            try:
                while True:
                    raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
                    data = json.loads(raw)
                    messages_received.append(data)

                    msg_id = data.get("message_id", "?")
                    state = data.get("payload", {}).get("response_state", "?")
                    widgets = data.get("payload", {}).get("data") or []
                    widget_types = [w.get("widget_type") for w in widgets if isinstance(w, dict)]

                    print(f"[CLIENT] RECEIVED  msg_id={msg_id}  state={state}  widgets={widget_types}")

                    if state == "DONE":
                        print("\n[CLIENT] Stream completed (DONE).")
                        break

            except asyncio.TimeoutError:
                print("\n[CLIENT] ERROR: Timed out waiting for response.")
                return False

    except websockets.exceptions.InvalidStatus as exc:
        status = exc.response.status_code if hasattr(exc, 'response') else '?'
        print(f"\n[CLIENT] ERROR: Server rejected WebSocket connection: HTTP {status}")
        if status == 401:
            print("Authentication failed. Ensure SAUCE_USERNAME and SAUCE_ACCESS_KEY are correct.")
        elif status == 403:
            print("Access forbidden. The AI Insights Gateway may only be accessible via the Sauce Labs web UI.")
            print("It likely requires a browser session cookie, not Basic Auth.")
        return False
    except Exception as exc:
        print(f"\n[CLIENT] ERROR: {exc}")
        return False

    # 3. Validate the shape of the conversation
    print(f"\n{'='*60}")
    print(f"VALIDATION  ({len(messages_received)} messages received)")
    print(f"{'='*60}")

    ok = True
    expected_states = ["PROCESSING", "PROCESSING", "PROCESSING", "DONE"]

    if len(messages_received) != len(expected_states):
        print(f"FAIL: Expected {len(expected_states)} messages, got {len(messages_received)}")
        ok = False
    else:
        for i, (msg, expected) in enumerate(zip(messages_received, expected_states)):
            actual = msg.get("payload", {}).get("response_state")
            if actual != expected:
                print(f"FAIL: Message {i+1} expected state '{expected}', got '{actual}'")
                ok = False

    # Check first message is a text widget
    if messages_received:
        first_data = messages_received[0].get("payload", {}).get("data", [])
        if not first_data or first_data[0].get("widget_type") != "text":
            print("FAIL: First message should contain a 'text' widget")
            ok = False
        else:
            print("PASS: First message contains 'text' widget")

    # Check second message is a chart widget
    if len(messages_received) > 1:
        second_data = messages_received[1].get("payload", {}).get("data", [])
        if not second_data or second_data[0].get("widget_type") != "chart":
            print("FAIL: Second message should contain a 'chart' widget")
            ok = False
        else:
            chart = second_data[0].get("value", {})
            chart_type = chart.get("chart_type")
            data_points = len(chart.get("data", []))
            print(f"PASS: Second message contains 'chart' widget (type={chart_type}, points={data_points})")

    # Check last message is DONE with null data
    if messages_received:
        last = messages_received[-1]
        if last.get("payload", {}).get("response_state") == "DONE" and last.get("payload", {}).get("data") is None:
            print("PASS: Final message signals DONE with null data")
        else:
            print("FAIL: Final message should signal DONE with null data")
            ok = False

    if ok:
        print("\nALL CHECKS PASSED.")
    else:
        print("\nSOME CHECKS FAILED.")

    return ok


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test client for Sauce AI Insights Gateway")
    parser.add_argument(
        "--host",
        default="ws://localhost:8765",
        help="WebSocket host (default: ws://localhost:8765 for mock server)"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Receive timeout in seconds (default: 30)"
    )
    parser.add_argument(
        "--username",
        default=os.environ.get("SAUCE_USERNAME", ""),
        help="Sauce Labs username (default: SAUCE_USERNAME env var)"
    )
    parser.add_argument(
        "--access-key",
        default=os.environ.get("SAUCE_ACCESS_KEY", ""),
        help="Sauce Labs access key (default: SAUCE_ACCESS_KEY env var)"
    )
    args = parser.parse_args()

    success = asyncio.run(
        run_test(args.host, timeout=args.timeout,
                 username=args.username, access_key=args.access_key)
    )
    sys.exit(0 if success else 1)
