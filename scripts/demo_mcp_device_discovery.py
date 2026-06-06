#!/usr/bin/env python3
"""
MCP Device Discovery Demo — Standalone Script

This script replicates the behavior of the `sauce-api-mcp-rdc` MCP server
so you can demonstrate device discovery from the command line even when
Claude Desktop or Gemini CLI are not available.

Credentials are read from environment variables or the project's `.env` file.

Usage:
    python3 scripts/demo_mcp_device_discovery.py

It queries the Sauce Labs REST API for:
- Available RDC Android devices
- Available RDC iOS devices
- Recent RDC jobs
"""

import os
import sys
import json
import requests

API_BASE = "https://api.us-west-1.saucelabs.com"
AUTH = None


def _load_env():
    """Load .env file if credentials are not already in the environment."""
    if os.getenv("SAUCE_USERNAME") and os.getenv("SAUCE_ACCESS_KEY"):
        return
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.isfile(env_path):
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                if key in ("SAUCE_USERNAME", "SAUCE_ACCESS_KEY") and not os.getenv(key):
                    os.environ[key] = value


def _ensure_auth():
    global AUTH
    if AUTH is not None:
        return
    _load_env()
    username = os.getenv("SAUCE_USERNAME")
    access_key = os.getenv("SAUCE_ACCESS_KEY")
    if not username or not access_key:
        print("ERROR: SAUCE_USERNAME and SAUCE_ACCESS_KEY not found in environment or .env")
        sys.exit(1)
    AUTH = (username, access_key)


def get_available_android_devices():
    """Query Sauce Labs for available Android RDC devices."""
    _ensure_auth()
    url = f"{API_BASE}/v1/rdc/devices"
    resp = requests.get(url, auth=AUTH, timeout=15)
    resp.raise_for_status()
    devices = resp.json()

    android = [
        d for d in devices
        if d.get("os") == "Android" and d.get("available", False)
    ]
    return android


def get_available_ios_devices():
    """Query Sauce Labs for available iOS RDC devices."""
    _ensure_auth()
    url = f"{API_BASE}/v1/rdc/devices"
    resp = requests.get(url, auth=AUTH, timeout=15)
    resp.raise_for_status()
    devices = resp.json()

    ios = [
        d for d in devices
        if d.get("os") == "iOS" and d.get("available", False)
    ]
    return ios


def get_recent_rdc_jobs(limit=5):
    """Query Sauce Labs for recent RDC test jobs."""
    _ensure_auth()
    username = AUTH[0]
    url = f"{API_BASE}/v1/rdc/jobs"
    params = {"limit": limit}
    resp = requests.get(url, auth=AUTH, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json().get("jobs", [])


def print_devices(devices, label):
    print(f"\n{'=' * 60}")
    print(f"  {label} — {len(devices)} device(s) available")
    print(f"{'=' * 60}")
    for d in devices[:10]:
        name = d.get("name", "Unknown")
        os_version = d.get("os_version", "?")
        api_level = d.get("api_level", "N/A")
        resolution = d.get("resolution", "?")
        print(f"  • {name}")
        print(f"    OS: {os_version}  |  API: {api_level}  |  Resolution: {resolution}")


def print_jobs(jobs):
    print(f"\n{'=' * 60}")
    print(f"  Recent RDC Jobs — {len(jobs)} job(s)")
    print(f"{'=' * 60}")
    for job in jobs:
        status = "PASSED" if job.get("passed") else "FAILED"
        status_icon = "✅" if job.get("passed") else "❌"
        device = job.get("device_name", "Unknown")
        name = job.get("name", "Unnamed")
        duration = job.get("duration", 0)
        print(f"  {status_icon} {status} — {name}")
        print(f"     Device: {device}  |  Duration: {duration}s")
        print(f"     URL: {job.get('web_url', 'N/A')}")


def main():
    print("=" * 60)
    print("  MCP Device Discovery Demo")
    print("  (mimics sauce-api-mcp-rdc tool calls)")
    print("=" * 60)

    # Android devices
    try:
        android = get_available_android_devices()
        print_devices(android, "Android Devices")
    except Exception as e:
        print(f"\n⚠️  Failed to fetch Android devices: {e}")

    # iOS devices
    try:
        ios = get_available_ios_devices()
        print_devices(ios, "iOS Devices")
    except Exception as e:
        print(f"\n⚠️  Failed to fetch iOS devices: {e}")

    # Recent jobs
    try:
        jobs = get_recent_rdc_jobs()
        print_jobs(jobs)
    except Exception as e:
        print(f"\n⚠️  Failed to fetch recent jobs: {e}")

    print("\n" + "=" * 60)
    print("  Demo complete.")
    print("  In Claude Desktop / Gemini CLI, ask:")
    print('    "What Android devices are available?"')
    print('    "Show my recent RDC jobs"')
    print("=" * 60)


if __name__ == "__main__":
    main()
