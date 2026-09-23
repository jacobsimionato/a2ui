#!/usr/bin/env python3
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Stage 2: Dimension-agnostic code review latency and performance analytics.

Reads raw PR review data (JSON), applies multi-dimensional filtering and grouping
(by time intervals like week/month, PR size/LoC tiers, and optional author/reviewer
dimensions), and exports Markdown reports and CSV files.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
import statistics
import sys
from typing import Any

from zoneinfo import ZoneInfo

PST_TZ = ZoneInfo("America/Los_Angeles")

DEFAULT_BOTS = {
    "gemini-code-assist",
    "google-claude-agent",
    "google-github-actions",
    "google-cla",
    "github-actions",
    "copybara-service",
    "a2ui-bot",
}


def is_bot(login: str | None) -> bool:
    """Determine if a GitHub user login is an automated bot."""
    if not login:
        return False
    login_lower = login.lower()
    if login_lower in DEFAULT_BOTS:
        return True
    if login_lower.endswith("[bot]") or login_lower.endswith("-bot"):
        return True
    return False


def parse_iso(ts_str: str) -> datetime:
    """Parse ISO-8601 timestamp string into datetime."""
    clean_str = ts_str.replace("Z", "+00:00")
    return datetime.fromisoformat(clean_str)


def business_duration_hours(start_dt: datetime, end_dt: datetime, tz: ZoneInfo = PST_TZ) -> float:
    """Calculate elapsed business hours excluding weekends (Sat/Sun) in PST."""
    if end_dt <= start_dt:
        return 0.0
    start_local = start_dt.astimezone(tz)
    end_local = end_dt.astimezone(tz)

    current = start_local
    total_seconds = 0.0

    while current < end_local:
        next_day = (current + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        chunk_end = min(next_day, end_local)

        # Monday=0 ... Friday=4 in PST (weekdays)
        if current.weekday() < 5:
            total_seconds += (chunk_end - current).total_seconds()

        current = chunk_end

    return total_seconds / 3600.0


def percentile(values: list[float], p: float) -> float:
    """Calculate the p-th percentile of sorted values using linear interpolation."""
    if not values:
        return 0.0
    vals = sorted(values)
    k = (len(vals) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return vals[int(k)]
    d0 = vals[int(f)] * (c - k)
    d1 = vals[int(c)] * (k - f)
    return d0 + d1


def calc_stats(values: list[float]) -> dict[str, float | int]:
    """Calculate count, median, p90, and mean for a list of floats."""
    if not values:
        return {"count": 0, "median": 0.0, "p90": 0.0, "mean": 0.0}
    vals = sorted(values)
    med = statistics.median(vals)
    p90 = percentile(vals, 90.0)
    mean_val = statistics.mean(vals)
    return {
        "count": len(vals),
        "median": round(med, 2),
        "p90": round(p90, 2),
        "mean": round(mean_val, 2),
    }


def format_business_duration(hours: float) -> str:
    """Format duration in business days and hours/mins in PST."""
    if hours == 0.0:
        return "0.00 bdays (0m)"

    bdays = hours / 24.0

    if hours < 1.0:
        mins = max(1, int(round(hours * 60)))
        time_str = f"{mins}m"
    elif hours < 24.0:
        hrs = int(hours)
        mins = int(round((hours - hrs) * 60))
        time_str = f"{hrs}h {mins}m" if mins > 0 else f"{hrs}h"
    else:
        d = int(hours // 24)
        rem_hrs = int(round(hours % 24))
        time_str = f"{d}d {rem_hrs}h" if rem_hrs > 0 else f"{d}d"

    return f"{bdays:.2f} bdays ({time_str})"


def get_interval_info(dt: datetime, interval_type: str = "week") -> tuple[str, str]:
    """Return interval key and formatted label for a given datetime."""
    if interval_type == "month":
        key = dt.strftime("%Y-%m")
        label = dt.strftime("%b %Y")
        return key, label
    else:
        year, week, _ = dt.isocalendar()
        key = f"{year}-W{week:02d}"
        monday = datetime.fromisocalendar(year, week, 1)
        sunday = datetime.fromisocalendar(year, week, 7)
        label = f"{monday.strftime('%b %d')} - {sunday.strftime('%b %d')}"
        return key, label


def classify_size(total_loc: int, loc_split: int | None = None) -> tuple[str, str]:
    """Classify PR into a size tier."""
    if loc_split is not None:
        if total_loc < loc_split:
            return f"0_{loc_split}", f"< {loc_split} LoC"
        else:
            return f"1_{loc_split}", f"≥ {loc_split} LoC"

    # Default size categories
    if total_loc < 100:
        return "1_xs", "< 100 LoC (XS)"
    elif total_loc < 500:
        return "2_s", "100 - 499 LoC (S)"
    elif total_loc < 1000:
        return "3_m", "500 - 999 LoC (M)"
    else:
        return "4_l", "1000+ LoC (L)"


def compute_turns(
    pr: dict[str, Any], include_bots: bool = False
) -> tuple[list[float], list[float], dict[str, list[float]]]:
    """Compute reviewer turn times and author turn times for a PR."""
    pr_author = pr["author"]
    events = pr.get("timeline_events", [])

    reviewer_turns: list[float] = []
    author_turns: list[float] = []
    per_reviewer_turns: dict[str, list[float]] = {}

    last_author_action_time: datetime | None = None
    last_reviewer_action_time: datetime | None = None
    active_ball: str | None = None

    for ev in events:
        ev_author = ev.get("author")
        if not include_bots and is_bot(ev_author):
            continue

        ev_type = ev.get("type")
        ev_time = parse_iso(ev["timestamp"])

        if ev_type in ("pr_created", "reviewer_requested", "commit", "ready_for_review"):
            if ev_type == "reviewer_requested":
                req_rev = ev.get("reviewer")
                if req_rev and not is_bot(req_rev):
                    last_author_action_time = ev_time
                    active_ball = "reviewer"
            else:
                if ev_author == pr_author or ev.get("role") in ("author", "contributor"):
                    if active_ball == "author" and last_reviewer_action_time:
                        duration = business_duration_hours(last_reviewer_action_time, ev_time)
                        if duration >= 0:
                            author_turns.append(duration)
                    last_author_action_time = ev_time
                    active_ball = "reviewer"

        elif ev_type in ("review", "comment"):
            if ev_author != pr_author and not is_bot(ev_author):
                if active_ball == "reviewer" and last_author_action_time:
                    duration = business_duration_hours(last_author_action_time, ev_time)
                    if duration >= 0:
                        reviewer_turns.append(duration)
                        per_reviewer_turns.setdefault(ev_author, []).append(duration)
                last_reviewer_action_time = ev_time
                active_ball = "author"

            elif ev_author == pr_author:
                if active_ball == "author" and last_reviewer_action_time:
                    duration = business_duration_hours(last_reviewer_action_time, ev_time)
                    if duration >= 0:
                        author_turns.append(duration)
                last_author_action_time = ev_time
                active_ball = "reviewer"

    return reviewer_turns, author_turns, per_reviewer_turns


def filter_prs(
    prs: list[dict[str, Any]],
    author: str | None = None,
    reviewer: str | None = None,
    since: str | None = None,
    until: str | None = None,
    min_loc: int | None = None,
    max_loc: int | None = None,
) -> list[dict[str, Any]]:
    """Filter raw PR list in memory by criteria."""
    filtered: list[dict[str, Any]] = []
    since_dt = parse_iso(f"{since}T00:00:00Z") if since else None
    until_dt = parse_iso(f"{until}T23:59:59Z") if until else None

    for pr in prs:
        if author and pr.get("author", "").lower() != author.lower():
            continue

        if reviewer:
            rev_lower = reviewer.lower()
            all_revs = {
                r["login"].lower() for r in pr.get("listed_reviewers", [])
            } | {r.lower() for r in pr.get("other_reviewers", [])}
            if rev_lower not in all_revs:
                continue

        created_dt = parse_iso(pr["createdAt"])
        if since_dt and created_dt < since_dt:
            continue
        if until_dt and created_dt > until_dt:
            continue

        total_loc = pr.get("total_loc", (pr.get("additions", 0) + pr.get("deletions", 0)))
        if min_loc is not None and total_loc < min_loc:
            continue
        if max_loc is not None and total_loc > max_loc:
            continue

        filtered.append(pr)

    return filtered


def analyze_records(
    prs: list[dict[str, Any]],
    interval: str = "week",
    group_dimensions: list[str] | None = None,
    loc_split: int | None = None,
    include_bots: bool = False,
) -> dict[str, Any]:
    """Group and analyze PRs across requested dimensions using PST business days."""
    if not group_dimensions:
        group_dimensions = ["interval"]

    groups: dict[tuple, dict[str, Any]] = {}
    pr_rows: list[dict[str, Any]] = []

    for pr in prs:
        pr_author = pr["author"]
        if not include_bots and is_bot(pr_author):
            continue

        created_dt = parse_iso(pr["createdAt"])
        merged_dt = parse_iso(pr["mergedAt"]) if pr.get("mergedAt") else None
        total_loc = pr.get("total_loc", (pr.get("additions", 0) + pr.get("deletions", 0)))

        interval_key, interval_label = get_interval_info(created_dt, interval_type=interval)
        size_key, size_label = classify_size(total_loc, loc_split=loc_split)

        # Extract reviewer requested & approved times
        listed = pr.get("listed_reviewers", [])
        requested_times: list[datetime] = []
        reviewer_first_requested: dict[str, datetime] = {}

        for lr in listed:
            rev_name = lr["login"]
            if not include_bots and is_bot(rev_name):
                continue
            all_reqs = lr.get("allRequests") or ([lr["requestedAt"]] if lr.get("requestedAt") else [])
            for r_ts in all_reqs:
                if r_ts:
                    r_dt = parse_iso(r_ts)
                    requested_times.append(r_dt)
                    if rev_name not in reviewer_first_requested or r_dt < reviewer_first_requested[rev_name]:
                        reviewer_first_requested[rev_name] = r_dt

        first_reviewer_req_dt = min(requested_times) if requested_times else None

        sub_to_first_rev_hrs: float | None = None
        if first_reviewer_req_dt:
            sub_to_first_rev_hrs = business_duration_hours(created_dt, first_reviewer_req_dt)

        approvals = pr.get("approvals", [])
        seen_approvals: dict[str, datetime] = {}
        for app in approvals:
            rev_name = app.get("reviewer")
            app_at = app.get("approvedAt")
            if rev_name and app_at and (include_bots or not is_bot(rev_name)):
                app_dt = parse_iso(app_at)
                if rev_name not in seen_approvals or app_dt < seen_approvals[rev_name]:
                    seen_approvals[rev_name] = app_dt

        pr_lgtm_durations: list[float] = []
        req_dts_for_approvers: list[datetime] = []
        for rev_name, app_dt in seen_approvals.items():
            req_dt = reviewer_first_requested.get(rev_name, created_dt)
            req_dts_for_approvers.append(req_dt)
            lgtm_hrs = business_duration_hours(req_dt, app_dt)
            pr_lgtm_durations.append(lgtm_hrs)

        # PR level: time until ALL approving reviewers approved
        pr_all_lgtm_hrs: float | None = None
        if seen_approvals:
            earliest_req = min(req_dts_for_approvers)
            latest_app = max(seen_approvals.values())
            pr_all_lgtm_hrs = business_duration_hours(earliest_req, latest_app)

        sub_to_merge_hrs: float | None = None
        if merged_dt:
            sub_to_merge_hrs = business_duration_hours(created_dt, merged_dt)

        rev_turns, auth_turns, per_rev_turns = compute_turns(pr, include_bots=include_bots)

        pr_rows.append({
            "number": pr["number"],
            "title": pr.get("title", ""),
            "author": pr_author,
            "created_at": pr["createdAt"],
            "merged_at": pr.get("mergedAt", ""),
            "total_loc": total_loc,
            "interval_key": interval_key,
            "interval_label": interval_label,
            "size_label": size_label,
            "sub_to_first_rev_hrs": round(sub_to_first_rev_hrs, 2) if sub_to_first_rev_hrs is not None else "",
            "min_added_to_lgtm_hrs": round(min(pr_lgtm_durations), 2) if pr_lgtm_durations else "",
            "all_lgtm_hrs": round(pr_all_lgtm_hrs, 2) if pr_all_lgtm_hrs is not None else "",
            "sub_to_merge_hrs": round(sub_to_merge_hrs, 2) if sub_to_merge_hrs is not None else "",
            "approvers": ", ".join(sorted(seen_approvals.keys())),
        })

        if "reviewer" in group_dimensions:
            reviewers_to_evaluate = sorted(seen_approvals.keys()) or list(reviewer_first_requested.keys())
            if not reviewers_to_evaluate:
                reviewers_to_evaluate = ["(no reviewer)"]
        else:
            reviewers_to_evaluate = [None]

        for current_reviewer in reviewers_to_evaluate:
            key_parts = []
            labels = {}
            for dim in group_dimensions:
                if dim == "interval":
                    key_parts.append(interval_key)
                    labels["interval"] = interval_label
                elif dim == "size":
                    key_parts.append(size_key)
                    labels["size"] = size_label
                elif dim == "author":
                    key_parts.append(pr_author)
                    labels["author"] = f"@{pr_author}"
                elif dim == "reviewer":
                    key_parts.append(current_reviewer)
                    labels["reviewer"] = f"@{current_reviewer}" if current_reviewer else "-"

            full_key = tuple(key_parts)
            if full_key not in groups:
                groups[full_key] = {
                    "key": full_key,
                    "labels": labels,
                    "prs": [],
                    "all_lgtm_durations": [],
                    "added_to_lgtm_durations": [],
                    "reviewer_turn_durations": [],
                    "sub_to_first_rev_durations": [],
                    "sub_to_merge_durations": [],
                }

            g = groups[full_key]
            g["prs"].append(pr)

            if pr_all_lgtm_hrs is not None:
                g["all_lgtm_durations"].append(pr_all_lgtm_hrs)

            if current_reviewer and current_reviewer in seen_approvals:
                req_dt = reviewer_first_requested.get(current_reviewer, created_dt)
                lgtm_hrs = business_duration_hours(req_dt, seen_approvals[current_reviewer])
                g["added_to_lgtm_durations"].append(lgtm_hrs)
            elif not current_reviewer:
                g["added_to_lgtm_durations"].extend(pr_lgtm_durations)

            if current_reviewer and current_reviewer in per_rev_turns:
                g["reviewer_turn_durations"].extend(per_rev_turns[current_reviewer])
            elif not current_reviewer:
                g["reviewer_turn_durations"].extend(rev_turns)

            if sub_to_first_rev_hrs is not None:
                g["sub_to_first_rev_durations"].append(sub_to_first_rev_hrs)
            if sub_to_merge_hrs is not None:
                g["sub_to_merge_durations"].append(sub_to_merge_hrs)

    return {
        "groups": groups,
        "pr_rows": pr_rows,
        "dimensions": group_dimensions,
        "interval": interval,
    }


def generate_markdown_report(
    analysis: dict[str, Any], metadata: dict[str, Any]
) -> str:
    """Format analysis into a clean, Github-Flavored Markdown report in PST business days."""
    groups = analysis["groups"]
    dims = analysis["dimensions"]
    pr_rows = analysis["pr_rows"]

    total_prs = len(pr_rows)
    all_pr_lgtm = []
    all_indiv_lgtm = []
    all_rev_turns = []
    all_sub_rev = []
    all_merge = []

    for g in groups.values():
        all_pr_lgtm.extend(g["all_lgtm_durations"])
        all_indiv_lgtm.extend(g["added_to_lgtm_durations"])
        all_rev_turns.extend(g["reviewer_turn_durations"])
        all_sub_rev.extend(g["sub_to_first_rev_durations"])
        all_merge.extend(g["sub_to_merge_durations"])

    st_all_lgtm = calc_stats(all_pr_lgtm)
    st_indiv_lgtm = calc_stats(all_indiv_lgtm)
    st_turn_all = calc_stats(all_rev_turns)
    st_sub_rev_all = calc_stats(all_sub_rev)
    st_merge_all = calc_stats(all_merge)

    lines: list[str] = []
    lines.append("# A2UI Code Review Performance Report\n")
    lines.append(f"> **Repository:** `{metadata.get('repository', 'a2ui-project/a2ui')}`  ")
    lines.append(f"> **Timeframe:** {metadata.get('filters', {}).get('since', 'All')} to {metadata.get('filters', {}).get('until', 'All')}  ")
    lines.append(f"> **Measurement:** **Business Days in US/Pacific (PST/PDT)** *(weekends excluded)*  ")
    lines.append(f"> **Grouped by:** {', '.join(dims)}  ")
    lines.append(f"> **Merged PRs Analyzed:** {total_prs}\n")

    lines.append("## Executive Summary\n")
    lines.append("| Metric | Median | 90th Percentile (P90) | Sample Count |")
    lines.append("| :--- | :---: | :---: | :---: |")
    lines.append(
        f"| **Review Time: Reviewers Added &rarr; All LGTMs** | **{format_business_duration(float(st_all_lgtm['median']))}** | **{format_business_duration(float(st_all_lgtm['p90']))}** | {st_all_lgtm['count']} PRs with approvals |"
    )
    lines.append(
        f"| **Individual Reviewer: Added &rarr; LGTM** | **{format_business_duration(float(st_indiv_lgtm['median']))}** | **{format_business_duration(float(st_indiv_lgtm['p90']))}** | {st_indiv_lgtm['count']} approvals |"
    )
    lines.append(
        f"| **Reviewer Turn Time** (Author Action &rarr; Reviewer Response) | **{format_business_duration(float(st_turn_all['median']))}** | **{format_business_duration(float(st_turn_all['p90']))}** | {st_turn_all['count']} turns |"
    )
    lines.append(
        f"| **Submission &rarr; First Reviewer Added** | **{format_business_duration(float(st_sub_rev_all['median']))}** | **{format_business_duration(float(st_sub_rev_all['p90']))}** | {st_sub_rev_all['count']} PRs |"
    )
    lines.append(
        f"| **PR Lifespan** (Submission &rarr; Merge) | **{format_business_duration(float(st_merge_all['median']))}** | **{format_business_duration(float(st_merge_all['p90']))}** | {st_merge_all['count']} PRs |"
    )
    lines.append("\n---\n")

    lines.append("## Cohort Breakdown\n")

    headers = []
    if "interval" in dims:
        headers.append("Time Period")
    if "size" in dims:
        headers.append("PR Size")
    if "author" in dims:
        headers.append("Author")
    if "reviewer" in dims:
        headers.append("Reviewer")

    headers.extend([
        "Merged PRs",
        "Review Time: All LGTMs (Median)",
        "Review Time: All LGTMs (P90)",
        "Indiv. LGTM (Median)",
        "Reviewer Turn (Median)",
        "Sub → Merge (Median)",
    ])

    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join([":---" if i < len(dims) else (":---:" if i == len(dims) else ":---:") for i in range(len(headers))]) + " |")

    sorted_keys = sorted(groups.keys())

    for k in sorted_keys:
        g = groups[k]
        st_all_g = calc_stats(g["all_lgtm_durations"])
        st_ind_g = calc_stats(g["added_to_lgtm_durations"])
        st_turns = calc_stats(g["reviewer_turn_durations"])
        st_merge = calc_stats(g["sub_to_merge_durations"])

        row = []
        if "interval" in dims:
            row.append(f"`{g['labels']['interval']}`")
        if "size" in dims:
            row.append(f"**{g['labels']['size']}**")
        if "author" in dims:
            row.append(f"{g['labels']['author']}")
        if "reviewer" in dims:
            row.append(f"{g['labels']['reviewer']}")

        row.append(str(len(g["prs"])))
        row.append(format_business_duration(float(st_all_g["median"])) if st_all_g["count"] else "-")
        row.append(format_business_duration(float(st_all_g["p90"])) if st_all_g["count"] else "-")
        row.append(format_business_duration(float(st_ind_g["median"])) if st_ind_g["count"] else "-")
        row.append(format_business_duration(float(st_turns["median"])) if st_turns["count"] else "-")
        row.append(format_business_duration(float(st_merge["median"])) if st_merge["count"] else "-")

        lines.append("| " + " | ".join(row) + " |")

    lines.append("\n---\n")
    lines.append("## Metric Definitions\n")
    lines.append("- **Added &rarr; LGTM**: Elapsed time between when a reviewer is requested (`ReviewRequestedEvent`) and when they submit an `APPROVED` review.")
    lines.append("- **Reviewer Turn Time**: Latency between an author action (PR opened, reviewer requested, commit pushed, comment replied) and a reviewer response (review or comment).")
    lines.append("- **Submission &rarr; Reviewer Added**: Elapsed time between PR creation (`createdAt`) and the timestamp the first reviewer was assigned.")
    lines.append("- **Sub &rarr; Merge**: Total lead time from PR creation to merge.")
    lines.append("- **Bot Filtering**: Automated accounts (e.g. `gemini-code-assist`, `github-actions[bot]`, `google-cla`) are excluded by default.")

    return "\n".join(lines)


def export_csv_reports(analysis: dict[str, Any], output_dir: Path) -> None:
    """Export aggregated metrics and PR rows to CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)
    groups = analysis["groups"]
    dims = analysis["dimensions"]
    pr_rows = analysis["pr_rows"]

    metrics_csv_path = output_dir / "metrics.csv"
    with open(metrics_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        header = list(dims) + [
            "merged_prs_count",
            "review_time_all_lgtm_median_bdays",
            "review_time_all_lgtm_p90_bdays",
            "indiv_lgtm_median_bdays",
            "indiv_lgtm_p90_bdays",
            "reviewer_turn_median_bdays",
            "reviewer_turn_p90_bdays",
            "sub_to_merge_median_bdays",
            "sub_to_merge_p90_bdays",
            "review_time_all_lgtm_median_hours",
            "review_time_all_lgtm_p90_hours",
            "indiv_lgtm_median_hours",
            "indiv_lgtm_p90_hours",
        ]
        writer.writerow(header)
        for k in sorted(groups.keys()):
            g = groups[k]
            st_all_lgtm = calc_stats(g["all_lgtm_durations"])
            st_indiv_lgtm = calc_stats(g["added_to_lgtm_durations"])
            st_turns = calc_stats(g["reviewer_turn_durations"])
            st_merge = calc_stats(g["sub_to_merge_durations"])

            dim_vals = [g["labels"].get(d, str(k[i])) for i, d in enumerate(dims)]
            writer.writerow(dim_vals + [
                len(g["prs"]),
                round(float(st_all_lgtm["median"]) / 24.0, 2) if st_all_lgtm["count"] else "",
                round(float(st_all_lgtm["p90"]) / 24.0, 2) if st_all_lgtm["count"] else "",
                round(float(st_indiv_lgtm["median"]) / 24.0, 2) if st_indiv_lgtm["count"] else "",
                round(float(st_indiv_lgtm["p90"]) / 24.0, 2) if st_indiv_lgtm["count"] else "",
                round(float(st_turns["median"]) / 24.0, 2) if st_turns["count"] else "",
                round(float(st_turns["p90"]) / 24.0, 2) if st_turns["count"] else "",
                round(float(st_merge["median"]) / 24.0, 2) if st_merge["count"] else "",
                round(float(st_merge["p90"]) / 24.0, 2) if st_merge["count"] else "",
                st_all_lgtm["median"],
                st_all_lgtm["p90"],
                st_indiv_lgtm["median"],
                st_indiv_lgtm["p90"],
            ])

    pr_csv_path = output_dir / "prs.csv"
    with open(pr_csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "number",
            "title",
            "author",
            "created_at",
            "merged_at",
            "total_loc",
            "interval_label",
            "size_label",
            "sub_to_first_rev_hrs",
            "min_added_to_lgtm_hrs",
            "sub_to_merge_hrs",
            "approvers",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in pr_rows:
            writer.writerow(row)


def get_n_months_ago_start(now_dt: datetime, n_months: int) -> datetime:
    """Calculate the first day of the month N calendar months ago."""
    year = now_dt.year
    month = now_dt.month - n_months + 1
    while month <= 0:
        month += 12
        year -= 1
    return datetime(year, month, 1, 0, 0, 0, tzinfo=timezone.utc)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Dimension-agnostic code review performance analytics."
    )
    parser.add_argument(
        "--input",
        default="scripts/data/raw_prs.json",
        help="Input JSON file path containing raw PRs (default: scripts/data/raw_prs.json)",
    )
    parser.add_argument(
        "--interval",
        choices=["week", "month"],
        default="week",
        help="Time cohort grouping interval: 'week' or 'month' (default: week)",
    )
    parser.add_argument(
        "--months",
        type=int,
        help="Filter to the last N calendar months (e.g. --months 4)",
    )
    parser.add_argument(
        "--weeks",
        type=int,
        help="Filter to the last N weeks",
    )
    parser.add_argument(
        "--loc-split",
        type=int,
        help="Split PRs into binary size tiers around LoC threshold (e.g. --loc-split 1000)",
    )
    parser.add_argument(
        "--min-loc",
        type=int,
        help="Filter PRs with total LoC >= min_loc",
    )
    parser.add_argument(
        "--max-loc",
        type=int,
        help="Filter PRs with total LoC <= max_loc",
    )
    parser.add_argument(
        "--group-by",
        help="Comma-separated dimensions to group by: interval, size, author, reviewer",
    )
    parser.add_argument(
        "--author",
        help="Filter by PR author username",
    )
    parser.add_argument(
        "--reviewer",
        help="Filter by reviewer username",
    )
    parser.add_argument(
        "--since",
        help="Filter by submission date >= YYYY-MM-DD",
    )
    parser.add_argument(
        "--until",
        help="Filter by submission date <= YYYY-MM-DD",
    )
    parser.add_argument(
        "--include-bots",
        action="store_true",
        help="Include automated bot accounts in review metrics",
    )
    parser.add_argument(
        "--markdown",
        default="scripts/reports/review_report.md",
        help="Output Markdown report path (default: scripts/reports/review_report.md)",
    )
    parser.add_argument(
        "--csv-dir",
        default="scripts/reports",
        help="Directory to output CSV reports (default: scripts/reports)",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Also output the generated Markdown report to stdout",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file {input_path} does not exist.", file=sys.stderr)
        print("Run 'python3 scripts/pull_review_data.py' first to pull raw data.", file=sys.stderr)
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    metadata = payload.get("metadata", {})
    prs = payload.get("prs", [])

    # Calculate date range if --months or --weeks is provided
    now_utc = datetime.now(timezone.utc)
    since_date = args.since
    if args.months:
        since_date = get_n_months_ago_start(now_utc, args.months).strftime("%Y-%m-%d")
    elif args.weeks:
        since_date = (now_utc - timedelta(weeks=args.weeks)).strftime("%Y-%m-%d")

    filtered_prs = filter_prs(
        prs,
        author=args.author,
        reviewer=args.reviewer,
        since=since_date,
        until=args.until,
        min_loc=args.min_loc,
        max_loc=args.max_loc,
    )

    # Determine grouping dimensions
    if args.group_by:
        dimensions = [d.strip().lower() for d in args.group_by.split(",") if d.strip()]
    elif args.loc_split is not None:
        dimensions = ["interval", "size"]
    else:
        dimensions = ["interval"]

    metadata["filters"] = {
        "since": since_date,
        "until": args.until,
        "author": args.author,
        "reviewer": args.reviewer,
        "loc_split": args.loc_split,
        "min_loc": args.min_loc,
        "max_loc": args.max_loc,
    }

    print(f"Analyzing {len(filtered_prs)} PRs (filtered from {len(prs)} total) grouped by {dimensions}...")

    analysis = analyze_records(
        filtered_prs,
        interval=args.interval,
        group_dimensions=dimensions,
        loc_split=args.loc_split,
        include_bots=args.include_bots,
    )

    report_md = generate_markdown_report(analysis, metadata)
    md_output_path = Path(args.markdown)
    md_output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(md_output_path, "w", encoding="utf-8") as f:
        f.write(report_md)

    csv_dir_path = Path(args.csv_dir)
    export_csv_reports(analysis, csv_dir_path)

    if args.stdout:
        print("\n" + "=" * 80)
        print(report_md)


if __name__ == "__main__":
    main()
