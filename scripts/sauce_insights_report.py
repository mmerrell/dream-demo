#!/usr/bin/env python3
"""
Sauce Insights Weekly Report — Standalone Demo Script.

Fetches real data from Sauce Labs Insights REST APIs and prints a
weekly report with error trends, top errors, and test status breakdown.

Requires:
    export SAUCE_USERNAME="..."
    export SAUCE_ACCESS_KEY="..."

Usage:
    python3 scripts/sauce_insights_report.py [days]

Examples:
    python3 scripts/sauce_insights_report.py          # last 7 days
    python3 scripts/sauce_insights_report.py 14       # last 14 days
    python3 scripts/sauce_insights_report.py 30       # last 30 days
"""
import os
import sys
import json
import requests
from datetime import datetime, timezone, timedelta
from collections import defaultdict

SAUCE_USERNAME = os.environ.get("SAUCE_USERNAME", "")
SAUCE_ACCESS_KEY = os.environ.get("SAUCE_ACCESS_KEY", "")
API_HOST = "https://api.us-west-1.saucelabs.com"

if not SAUCE_USERNAME or not SAUCE_ACCESS_KEY:
    print("ERROR: Set SAUCE_USERNAME and SAUCE_ACCESS_KEY")
    sys.exit(1)


class InsightsReporter:
    def __init__(self, username: str, access_key: str, api_host: str = API_HOST):
        self.username = username
        self.access_key = access_key
        self.api_host = api_host
        self.org_id = None

    def _get(self, path: str, params: dict = None):
        url = f"{self.api_host}{path}"
        resp = requests.get(url, auth=(self.username, self.access_key), params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()

    def _resolve_org_id(self):
        """Fetch org ID from concurrency endpoint."""
        data = self._get(f"/rest/v1.2/users/{self.username}/concurrency")
        org = data.get("concurrency", {}).get("organization", {})
        self.org_id = org.get("id")
        return self.org_id

    def fetch_error_trends(self, days: int = 7, source: str = "vdc"):
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=days)
        return self._get(f"/v2/insights/{source}/errors/trends", {
            "org_id": self.org_id,
            "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "interval": "1d",
        })

    def fetch_top_errors(self, days: int = 7, limit: int = 5, source: str = "vdc"):
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=days)
        return self._get(f"/v2/insights/{source}/errors", {
            "org_id": self.org_id,
            "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "limit": limit,
        })

    def fetch_tests(self, days: int = 7, limit: int = 100):
        """Fetch test listing from analytics API (covers VDC + RDC)."""
        return self._get("/v1/analytics/tests", {
            "time_range": f"{days}d",
            "size": limit,
            "scope": "organization",
        })

    def fetch_rdc_jobs(self, limit: int = 300):
        """Fetch RDC jobs. Response uses 'entities' key, not 'jobs'."""
        try:
            return self._get("/v1/rdc/jobs", {"limit": limit})
        except requests.HTTPError as e:
            if e.response.status_code in (404, 403):
                return {"entities": []}
            raise

    def build_report(self, days: int = 7) -> dict:
        self._resolve_org_id()

        # VDC insights
        vdc_error_trends = self.fetch_error_trends(days, source="vdc")
        vdc_top_errors = self.fetch_top_errors(days, source="vdc")

        # RDC insights (may be empty if no RDC plan)
        try:
            rdc_error_trends = self.fetch_error_trends(days, source="rdc")
            rdc_top_errors = self.fetch_top_errors(days, source="rdc")
        except requests.HTTPError:
            rdc_error_trends = {"histogram": [], "trend": {}}
            rdc_top_errors = {"buckets": []}

        # Test data from analytics (includes both VDC and RDC)
        tests_data = self.fetch_tests(days)
        test_window = days
        if not tests_data.get("items"):
            tests_data = self.fetch_tests(90)
            test_window = 90

        # RDC jobs for supplementary info
        rdc_jobs = self.fetch_rdc_jobs()

        return self._format_report(
            vdc_error_trends, vdc_top_errors,
            rdc_error_trends, rdc_top_errors,
            tests_data, rdc_jobs, days, test_window
        )

    def _format_report(self, vdc_error_trends, vdc_top_errors,
                         rdc_error_trends, rdc_top_errors,
                         tests_data, rdc_jobs, error_days, test_window):
        # VDC histogram
        vdc_histogram = vdc_error_trends.get("histogram", [])
        vdc_trend = vdc_error_trends.get("trend", {})
        vdc_err_buckets = vdc_top_errors.get("buckets", [])

        # RDC histogram
        rdc_histogram = rdc_error_trends.get("histogram", [])
        rdc_trend = rdc_error_trends.get("trend", {})
        rdc_err_buckets = rdc_top_errors.get("buckets", [])

        test_items = tests_data.get("items", [])
        rdc_job_list = rdc_jobs.get("entities", [])  # RDC API returns 'entities', not 'jobs'

        # Combined histogram (VDC + RDC)
        all_dates = set()
        for p in vdc_histogram:
            all_dates.add(p["datetime"][:10])
        for p in rdc_histogram:
            all_dates.add(p["datetime"][:10])

        date_to_counts = {}
        for p in vdc_histogram:
            d = p["datetime"][:10]
            date_to_counts[d] = date_to_counts.get(d, 0) + p["count"]
        for p in rdc_histogram:
            d = p["datetime"][:10]
            date_to_counts[d] = date_to_counts.get(d, 0) + p["count"]

        sorted_dates = sorted(all_dates)
        max_count = max(date_to_counts.values(), default=0)

        sparkline = []
        for date in sorted_dates:
            count = date_to_counts.get(date, 0)
            if max_count > 0:
                bar_len = int((count / max_count) * 20)
                bar = "█" * bar_len + "░" * (20 - bar_len)
            else:
                bar = " " * 20
            sparkline.append(f"  {date}  |{bar}|  {count}")

        # VDC status breakdown from analytics API
        vdc_status_counts = defaultdict(int)
        for t in test_items:
            vdc_status_counts[t.get("status", "unknown")] += 1

        # RDC status breakdown — uses 'consolidated_status' field
        rdc_status_counts = defaultdict(int)
        for j in rdc_job_list:
            rdc_status_counts[j.get("consolidated_status", "unknown")] += 1

        # Combined counts (what the dashboard shows)
        status_counts = defaultdict(int)
        for k, v in vdc_status_counts.items():
            status_counts[k] += v
        for k, v in rdc_status_counts.items():
            status_counts[k] += v

        total_tests = len(test_items) + len(rdc_job_list)
        passed  = status_counts.get("passed", 0)
        failed  = status_counts.get("failed", 0)
        errored = status_counts.get("error", 0)
        complete = status_counts.get("complete", 0)

        pass_rate  = (passed  / total_tests * 100) if total_tests else 0
        error_rate = (errored / total_tests * 100) if total_tests else 0
        fail_rate  = (failed  / total_tests * 100) if total_tests else 0

        # Peak error day from combined data
        if date_to_counts:
            peak_date = max(date_to_counts, key=date_to_counts.get)
            peak_count = date_to_counts[peak_date]
        else:
            peak_date = "N/A"
            peak_count = 0

        total_errors = (vdc_trend.get("current", 0) + rdc_trend.get("current", 0))

        # Combine top errors from VDC + RDC
        all_errors = {}
        for e in vdc_err_buckets:
            msg = e["name"]
            all_errors[msg] = all_errors.get(msg, 0) + e["count"]
        for e in rdc_err_buckets:
            msg = e["name"]
            all_errors[msg] = all_errors.get(msg, 0) + e["count"]
        combined_top_errors = sorted(
            [{"message": k, "count": v} for k, v in all_errors.items()],
            key=lambda x: x["count"], reverse=True
        )[:5]

        return {
            "error_period_days": error_days,
            "test_period_days": test_window,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "data_sources": {
                "vdc_tests": len(test_items),
                "rdc_jobs": len(rdc_job_list),
            },
            "summary": {
                "total_tests": total_tests,
                "total_errors": total_errors,
                "peak_errors_day": peak_date,
                "peak_errors_count": peak_count,
                "pass_rate": round(pass_rate, 1),
                "error_rate": round(error_rate, 1),
                "fail_rate": round(fail_rate, 1),
            },
            "error_sparkline": sparkline,
            "top_errors": combined_top_errors,
            "test_breakdown": dict(status_counts),
            "raw": {
                "vdc_error_trends": vdc_error_trends,
                "vdc_top_errors": vdc_top_errors,
                "rdc_error_trends": rdc_error_trends,
                "rdc_top_errors": rdc_top_errors,
                "tests": tests_data,
                "rdc_jobs": rdc_jobs,
            }
        }

    def print_report(self, report: dict):
        s = report["summary"]
        ep = report["error_period_days"]
        tp = report["test_period_days"]

        ds = report.get("data_sources", {})

        print("═" * 70)
        print(f"  Sauce Labs Insights Report")
        print(f"  Account: {self.username}")
        print(f"  Errors: Last {ep} days  |  Tests: Last {tp} days")
        print(f"  Generated: {report['generated_at'][:19]}Z")
        print("═" * 70)
        print()

        print("┌──────────────────────────────────────────────────────────────────────┐")
        print("│  DATA SOURCES                                                        │")
        print("├──────────────────────────────────────────────────────────────────────┤")
        print(f"│  VDC tests (/v1/analytics/tests):  {ds.get('vdc_tests', 0):<6}                      │")
        print(f"│  RDC jobs  (/v1/rdc/jobs):         {ds.get('rdc_jobs', 0):<6}                      │")
        print("└──────────────────────────────────────────────────────────────────────┘")
        print()

        print("┌──────────────────────────────────────────────────────────────────────┐")
        print("│  SUMMARY                                                             │")
        print("├──────────────────────────────────────────────────────────────────────┤")
        print(f"│  Total Tests:         {s['total_tests']:<8}                            │")
        print(f"│  Total Errors:        {s['total_errors']:<8}                            │")
        print(f"│  Peak Error Day:      {s['peak_errors_day']} ({s['peak_errors_count']} errors)              │")
        print(f"│  Pass Rate:           {s['pass_rate']}%                                  │")
        print(f"│  Error Rate:          {s['error_rate']}%                                  │")
        print(f"│  Fail Rate:           {s['fail_rate']}%                                  │")
        print("└──────────────────────────────────────────────────────────────────────┘")
        print()

        if report["error_sparkline"]:
            print("┌──────────────────────────────────────────────────────────────────────┐")
            print("│  ERROR TREND (daily)                                                 │")
            print("├──────────────────────────────────────────────────────────────────────┤")
            for line in report["error_sparkline"]:
                print(f"│{line:<68}│")
            print("└──────────────────────────────────────────────────────────────────────┘")
            print()

        if report["top_errors"]:
            print("┌──────────────────────────────────────────────────────────────────────┐")
            print("│  TOP ERRORS                                                          │")
            print("├──────────────────┬───────────────────────────────────────────────────┤")
            print(f"│  {'Count':<6}│  {'Error Message':<51}│")
            print("├──────────────────┼───────────────────────────────────────────────────┤")
            for err in report["top_errors"]:
                msg = err["message"].replace("\n", " ")[:50]
                print(f"│  {err['count']:<6}│  {msg:<51}│")
            print("└──────────────────┴───────────────────────────────────────────────────┘")
            print()

        if report["test_breakdown"]:
            print("┌──────────────────────────────────────────────────────────────────────┐")
            print("│  TEST STATUS BREAKDOWN                                               │")
            print("├──────────────────────────────────────────────────────────────────────┤")
            for status, count in report["test_breakdown"].items():
                print(f"│  {status:<15} {count:<6}                                        │")
            print("└──────────────────────────────────────────────────────────────────────┘")
            print()

        print("─" * 70)
        print("  End of Report")
        print("─" * 70)

    def render_markdown(self, report: dict) -> str:
        """Render the report as Markdown."""
        s = report["summary"]
        ep = report["error_period_days"]
        tp = report["test_period_days"]

        ds = report.get("data_sources", {})
        lines = [
            "# Sauce Labs Insights Report",
            "",
            f"- **Account:** `{self.username}`",
            f"- **Error Period:** Last {ep} days",
            f"- **Test Period:** Last {tp} days",
            f"- **Generated:** {report['generated_at'][:19]}Z",
            "",
            "---",
            "",
            "## Data Sources",
            "",
            f"| Source | Count |",
            f"| :----- | :---- |",
            f"| VDC tests (`/v1/analytics/tests`) | {ds.get('vdc_tests', 0)} |",
            f"| RDC jobs  (`/v1/rdc/jobs`)        | {ds.get('rdc_jobs', 0)} |",
            "",
            "---",
            "",
            "## Summary",
            "",
            f"| Metric           | Value                |",
            f"| :--------------- | :------------------- |",
            f"| Total Tests      | {s['total_tests']}                    |",
            f"| Total Errors     | {s['total_errors']}                    |",
            f"| Peak Error Day   | {s['peak_errors_day']} ({s['peak_errors_count']} errors) |",
            f"| Pass Rate        | {s['pass_rate']}%                  |",
            f"| Error Rate       | {s['error_rate']}%                  |",
            f"| Fail Rate        | {s['fail_rate']}%                  |",
            "",
        ]

        if report["error_sparkline"]:
            lines += [
                "## Error Trend (Daily)",
                "",
                "```",
            ]
            for line in report["error_sparkline"]:
                lines.append(line)
            lines += [
                "```",
                "",
            ]

        if report["top_errors"]:
            lines += [
                "## Top Errors",
                "",
                "| Count | Error Message |",
                "| :---- | :------------ |",
            ]
            for err in report["top_errors"]:
                msg = err["message"].replace("\n", " ")[:60]
                lines.append(f"| {err['count']} | {msg} |")
            lines.append("")

        if report["test_breakdown"]:
            lines += [
                "## Test Status Breakdown",
                "",
                "| Status  | Count |",
                "| :------ | :---- |",
            ]
            for status, count in report["test_breakdown"].items():
                lines.append(f"| {status} | {count} |")
            lines.append("")

        lines += [
            "---",
            "",
            "*Generated by `scripts/sauce_insights_report.py`*",
            "",
        ]

        return "\n".join(lines)


def main():
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    if days < 1 or days > 90:
        print("ERROR: days must be between 1 and 90")
        sys.exit(1)

    reporter = InsightsReporter(SAUCE_USERNAME, SAUCE_ACCESS_KEY)
    report = reporter.build_report(days=days)
    reporter.print_report(report)

    # Save JSON
    json_file = f"sauce-insights-{days}d.json"
    with open(json_file, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nRaw JSON saved to: {json_file}")

    # Save Markdown
    md_file = f"sauce-insights-{days}d.md"
    with open(md_file, "w") as f:
        f.write(reporter.render_markdown(report))
    print(f"Markdown report saved to: {md_file}")


if __name__ == "__main__":
    main()
