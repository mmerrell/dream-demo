#!/usr/bin/env python3
"""
Attempt B: Log into Sauce Labs web UI programmatically to steal a session cookie,
then use that cookie to authenticate the AI Assistant WebSocket.

WARNING: This is fragile. Sauce Labs may use CSRF tokens, reCaptcha, or
other anti-automation measures that break this approach.
"""
import asyncio
import json
import os
import sys
import uuid
from urllib.parse import urljoin

import requests

try:
    import websockets
except ImportError:
    print("ERROR: 'websockets' package is required.")
    sys.exit(1)


SAUCE_USERNAME = os.environ.get("SAUCE_USERNAME", "")
SAUCE_ACCESS_KEY = os.environ.get("SAUCE_ACCESS_KEY", "")

if not SAUCE_USERNAME or not SAUCE_ACCESS_KEY:
    print("ERROR: Set SAUCE_USERNAME and SAUCE_ACCESS_KEY environment variables.")
    sys.exit(1)


def try_cookie_auth():
    """
    Strategy 1: Hit the Sauce Labs web UI with Basic Auth and hope
    it sets a session cookie we can reuse.
    """
    session = requests.Session()

    # Try the main app page with Basic Auth
    print("[AUTH] Trying app.saucelabs.com with Basic Auth...")
    resp = session.get(
        "https://app.saucelabs.com",
        auth=(SAUCE_USERNAME, SAUCE_ACCESS_KEY),
        allow_redirects=True,
        timeout=15
    )
    print(f"[AUTH] Status: {resp.status_code}")
    print(f"[AUTH] Cookies set: {list(session.cookies.keys())}")
    print(f"[AUTH] Final URL: {resp.url}")

    if session.cookies:
        return session.cookies
    return None


def try_login_form():
    """
    Strategy 2: Try the actual login form endpoint.
    Sauce Labs login flow may vary (SAML, OAuth, etc.).
    """
    session = requests.Session()

    # First, GET the login page to capture any CSRF tokens
    print("\n[AUTH] Trying to discover login form...")
    login_page = session.get("https://accounts.saucelabs.com/", timeout=15, allow_redirects=True)
    print(f"[AUTH] Login page status: {login_page.status_code}")
    print(f"[AUTH] Login page URL: {login_page.url}")

    # Try common login endpoints
    login_endpoints = [
        "https://accounts.saucelabs.com/login",
        "https://accounts.saucelabs.com/api/login",
        "https://app.saucelabs.com/api/login",
        "https://api.us-west-1.saucelabs.com/rest/v1/users/login",
    ]

    for endpoint in login_endpoints:
        print(f"\n[AUTH] Trying POST {endpoint}...")
        try:
            resp = session.post(
                endpoint,
                json={"username": SAUCE_USERNAME, "password": SAUCE_ACCESS_KEY},
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                timeout=10
            )
            print(f"[AUTH]   Status: {resp.status_code}")
            print(f"[AUTH]   Response: {resp.text[:200]}")
            if resp.status_code in (200, 302):
                print(f"[AUTH]   Cookies: {list(session.cookies.keys())}")
                if session.cookies:
                    return session.cookies
        except Exception as e:
            print(f"[AUTH]   Error: {e}")

    return None


def cookies_to_header(cookies):
    """Convert a RequestsCookieJar to a Cookie HTTP header string."""
    return "; ".join(f"{k}={v}" for k, v in cookies.items())


async def try_websocket_with_cookies(cookie_header: str, timeout: float = 30.0):
    correlation_id = str(uuid.uuid4())
    uri = f"wss://api.us-west-1.saucelabs.com/ai-assistant-gateway/v1/chat/ws/{correlation_id}"
    print(f"\n[WS] Connecting to {uri} ...")

    additional_headers = {
        "Origin": "https://app.saucelabs.com",
        "Cookie": cookie_header,
    }

    try:
        async with websockets.connect(uri, additional_headers=additional_headers) as ws:
            print("[WS] Connected!")

            # Send the same prompt from the HAR
            message_id = str(uuid.uuid4())
            payload = {
                "correlation_id": correlation_id,
                "type": "prompt",
                "name": "send_prompt",
                "message_id": message_id,
                "payload": {
                    "timezone": "America/Los_Angeles",
                    "prompt": "What is the Error Rate trend over the past seven days?",
                    "filters": {
                        "start": "2026-04-22T07:00:00.000Z",
                        "end": "2026-05-22T07:00:00.000Z"
                    }
                }
            }
            await ws.send(json.dumps(payload))
            print("[WS] SENT prompt.")

            messages = []
            while True:
                raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
                data = json.loads(raw)
                messages.append(data)
                state = data.get("payload", {}).get("response_state", "?")
                print(f"[WS] RECEIVED state={state}")
                if state == "DONE":
                    break

            print(f"\n[WS] SUCCESS! Received {len(messages)} messages.")
            return True

    except websockets.exceptions.InvalidStatus as exc:
        status = getattr(exc, 'response', None)
        code = status.status_code if status else '?'
        print(f"[WS] FAILED: HTTP {code}")
        return False
    except Exception as exc:
        print(f"[WS] FAILED: {exc}")
        return False


async def main():
    print("=" * 60)
    print("Sauce AI Insights: Cookie-Based Auth Attempt")
    print("=" * 60)

    # --- Strategy 1: Basic Auth to web UI ---
    cookies = try_cookie_auth()

    # --- Strategy 2: Login form ---
    if not cookies:
        cookies = try_login_form()

    if not cookies:
        print("\n[FAIL] Could not obtain session cookies.")
        print("The Sauce Labs web UI likely uses a login flow that requires")
        print("browser interaction (SAML, OAuth, CSRF tokens, etc.).")
        sys.exit(1)

    cookie_header = cookies_to_header(cookies)
    print(f"\n[OK] Got cookies: {cookie_header[:100]}...")

    # --- Try WebSocket with cookies ---
    success = await try_websocket_with_cookies(cookie_header)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
