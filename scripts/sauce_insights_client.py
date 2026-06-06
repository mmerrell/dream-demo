#!/usr/bin/env python3
"""
Real Sauce Insights API Client.

Calls the public Sauce Labs Insights REST APIs (not the browser-only WebSocket)
to get error rate trends and top errors. This is the programmatic equivalent of
the AI Assistant chat shown in NetworkCalls/TestInsightsApi.har.

Usage:
    export SAUCE_USERNAME="..."
    export SAUCE_ACCESS_KEY="..."
    python3 scripts/sauce_insights_client.py
"""
import os
import sys
import json
import requests
from datetime import datetime, timezone, timedelta

SAUCE_USERNAME = os.environ.get("SAUCE_USERNAME", "")
SAUCE_ACCESS_KEY = os.environ.get("SAUCE_ACCESS_KEY", "")
ORG_ID = "f8eccdf81c62461c852e6c906f777124"  # From concurrency API
API_HOST = "https://api.us-west-1.saucelabs.com"

if not SAUCE_USERNAME or not SAUCE_ACCESS_KEY:
    print("ERROR: Set SAUCE_USERNAME and SAUCE_ACCESS_KEY")
    sys.exit(1)


def get_error_trends(days=7):
    """Get daily error counts over the past N days."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)

    url = f"{API_HOST}/v2/insights/vdc/errors/trends"
    resp = requests.get(url, auth=(SAUCE_USERNAME, SAUCE_ACCESS_KEY), params={
        "org_id": ORG_ID,
        "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "interval": "1d",
    }, timeout=15)
    resp.raise_for_status()
    return resp.json()


def get_top_errors(days=7, limit=5):
    """Get top errors by occurrence count."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)

    url = f"{API_HOST}/v2/insights/vdc/errors"
    resp = requests.get(url, auth=(SAUCE_USERNAME, SAUCE_ACCESS_KEY), params={
        "org_id": ORG_ID,
        "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "end": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "limit": limit,
    }, timeout=15)
    resp.raise_for_status()
    return resp.json()


def format_like_ai_assistant(trends, errors):
    """Format the raw API response like the AI Assistant chat output."""
    histogram = trends.get("histogram", [])
    trend = trends.get("trend", {})
    buckets = errors.get("buckets", [])

    # Build line chart data matching the HAR format
    chart_data = []
    for point in histogram:
        dt = point["datetime"]
        # Extract just the date portion for display
        date_label = dt[:10] if "T" in dt else dt
        chart_data.append({
            "name": f"{date_label}T00:00:00.000Z",
            "errors": float(point["count"])
        })

    # Text intro
    text_intro = "Here's the error rate trend over the past seven days:"

    # Build top errors table
    lines = ["| ERROR_TYPE | ERROR_COUNT |", "| :--------- | :---------- |"]
    for err in buckets:
        name = err["name"].replace("\n", " ").replace("|", "\\|")[:60]
        lines.append(f"| {name} | {err['count']} |")

    # Summary text
    peak_day = max(histogram, key=lambda x: x["count"]) if histogram else {"count": 0, "datetime": "N/A"}
    peak_date = peak_day["datetime"][:10] if "T" in peak_day["datetime"] else peak_day["datetime"]
    summary = (
        f"The chart above shows the daily count of errors. "
        f"There was a peak of {int(peak_day['count'])} errors on {peak_date}.\n\n"
        f"Here are the top {len(buckets)} errors by count in the last seven days:\n\n"
        + "\n".join(lines)
    )

    return {
        "text_intro": text_intro,
        "chart": {
            "chart_type": "line",
            "dataKeys": ["errors"],
            "data": chart_data,
            "units": {"x_label": "Date", "y_label": "number"}
        },
        "summary": summary,
        "raw": {
            "trend": trend,
            "total_errors": errors.get("all_items_count", 0),
            "unique_errors": errors.get("total", 0)
        }
    }


def main():
    print("=" * 60)
    print("Sauce Labs Insights API — Real Data")
    print("=" * 60)
    print()

    print("[API] Fetching error trends...")
    trends = get_error_trends(days=7)

    print("[API] Fetching top errors...")
    errors = get_top_errors(days=7, limit=5)

    result = format_like_ai_assistant(trends, errors)

    print()
    print("─" * 60)
    print("RESULT (formatted like AI Assistant output)")
    print("─" * 60)
    print()
    print(result["text_intro"])
    print()
    print(f"[Line Chart: {len(result['chart']['data'])} data points]")
    for pt in result["chart"]["data"]:
        print(f"  {pt['name'][:10]} → {int(pt['errors'])} errors")
    print()
    print(result["summary"])
    print()
    print("─" * 60)
    print("RAW METADATA")
    print("─" * 60)
    print(json.dumps(result["raw"], indent=2))


if __name__ == "__main__":
    main()
