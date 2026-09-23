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

"""Stage 2: Generate review latency and turnaround metrics from pulled PR data.

Reads raw PR review data (JSON), aggregates metrics week-by-week grouped by PR
submission time, and exports Markdown reports and CSV files.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import statistics
import sys
from typing import Any

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
    # Remove trailing Z if present for fromisoformat compatibility
    clean_str = ts_str.replace("Z", "+00:00")
    return datetime.fromisoformat(clean_str)


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


def format_duration(hours: float) -> str:
    """Format duration in hours into a readable string (e.g., 25m, 3h 12m, 2d 4h)."""
    if hours == 0.0:
        return "0m"
    if hours < 1.0:
        mins = max(1, int(round(hours * 60)))
        return f"{mins}m"
    elif hours < 24.0:
        hrs = int(hours)
        mins = int(round((hours - hrs) * 60))
        return f"{hrs}h {mins}m" if mins > 0 else f"{hrs}h"
    else:
        days = int(hours // 24)
        rem_hrs = int(round(hours % 24))
        return f"{days}d {rem_hrs}h" if rem_hrs > 0 else f"{days}d"


def get_week_info(dt: datetime) -> tuple[str, str]:
    """Return ISO week key (e.g. 2026-W38) and readable date range."""
    year, week, _ = dt.isocalendar()
    week_key = f"{year}-W{week:02d}"
    # Calculate start of week (Monday) and end of week (Sunday)
    monday = datetime.fromisocalendar(year, week, 1)
    sunday = datetime.fromisocalendar(year, week, 7)
    range_str = f"{monday.strftime('%b %d')} - {sunday.strftime('%b %d')}"
    return week_key, range_str


def compute_turns(
    pr: dict[str, Any], include_bots: bool = False
) -> tuple[list[float], list[float], dict[str, list[float]]]:
    """Compute reviewer turn times and author turn times for a PR.

    Returns:
        reviewer_turns: list of reviewer turn durations in hours
        author_turns: list of author turn durations in hours
        per_reviewer_turns: mapping of reviewer login -> list of turn durations
    """
    pr_author = pr["author"]
    events = pr.get("timeline_events", [])

    reviewer_turns: list[float] = []
    author_turns: list[float] = []
    per_reviewer_turns: dict[str, list[float]] = {}

    last_author_action_time: datetime | None = None
    last_reviewer_action_time: datetime | None = None
    active_ball: str | None = None  # 'reviewer' or 'author'

    for ev in events:
        ev_author = ev.get("author")
        if not include_bots and is_bot(ev_author):
            continue

        ev_type = ev.get("type")
        ev_time = parse_iso(ev["timestamp"])

        if ev_type in ("pr_created", "reviewer_requested", "commit", "ready_for_review"):
            # Author action
            if ev_type == "reviewer_requested":
                # Specific reviewer requested
                req_rev = ev.get("reviewer")
                if req_rev and not is_bot(req_rev):
                    last_author_action_time = ev_time
                    active_ball = "reviewer"
            else:
                if ev_author == pr_author or ev.get("role") in ("author", "contributor"):
                    if active_ball == "author" and last_reviewer_action_time:
                        duration = (ev_time - last_reviewer_action_time).total_seconds() / 3600.0
                        if duration >= 0:
                            author_turns.append(duration)
                    last_author_action_time = ev_time
                    active_ball = "reviewer"

        elif ev_type in ("review", "comment"):
            if ev_author != pr_author and not is_bot(ev_author):
                # Reviewer action
                if active_ball == "reviewer" and last_author_action_time:
                    duration = (ev_time - last_author_action_time).total_seconds() / 3600.0
                    if duration >= 0:
                        reviewer_turns.append(duration)
                        per_reviewer_turns.setdefault(ev_author, []).append(duration)
                last_reviewer_action_time = ev_time
                active_ball = "author"

            elif ev_author == pr_author:
                # Author comment
                if active_ball == "author" and last_reviewer_action_time:
                    duration = (ev_time - last_reviewer_action_time).total_seconds() / 3600.0
                    if duration >= 0:
                        author_turns.append(duration)
                last_author_action_time = ev_time
                active_ball = "reviewer"

    return reviewer_turns, author_turns, per_reviewer_turns


def analyze_prs(
    prs: list[dict[str, Any]],
    include_bots: bool = False,
) -> dict[str, Any]:
    """Perform full metrics aggregation across weeks and reviewers."""
    weekly_groups: dict[str, dict[str, Any]] = {}
    reviewer_aggregates: dict[str, dict[str, list[float]]] = {}
    author_aggregates: dict[str, dict[str, Any]] = {}
    pr_details: list[dict[str, Any]] = []

    for pr in prs:
        pr_author = pr["author"]
        if not include_bots and is_bot(pr_author):
            continue

        created_dt = parse_iso(pr["createdAt"])
        merged_dt = parse_iso(pr["mergedAt"]) if pr.get("mergedAt") else None
        week_key, week_range = get_week_info(created_dt)

        if week_key not in weekly_groups:
            weekly_groups[week_key] = {
                "week_key": week_key,
                "week_range": week_range,
                "prs": [],
                "added_to_lgtm_durations": [],
                "sub_to_first_reviewer_durations": [],
                "first_reviewer_to_lgtm_durations": [],
                "sub_to_merge_durations": [],
                "reviewer_turn_durations": [],
                "author_turn_durations": [],
                "reviewer_lgtm_durations": {},  # reviewer -> list[hours]
            }

        week = weekly_groups[week_key]
        week["prs"].append(pr)

        auth_entry = author_aggregates.setdefault(
            pr_author,
            {
                "prs_count": 0,
                "sub_to_first_rev_durations": [],
                "added_to_lgtm_durations": [],
                "sub_to_merge_durations": [],
                "author_turn_durations": [],
            },
        )
        auth_entry["prs_count"] += 1

        # 1. PR submission to first reviewer added
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

        sub_to_first_reviewer_hrs: float | None = None
        if first_reviewer_req_dt:
            sub_to_first_reviewer_hrs = max(
                0.0, (first_reviewer_req_dt - created_dt).total_seconds() / 3600.0
            )
            week["sub_to_first_reviewer_durations"].append(sub_to_first_reviewer_hrs)
            auth_entry["sub_to_first_rev_durations"].append(sub_to_first_reviewer_hrs)

        # 2. Time from adding reviewer to LGTM
        approvals = pr.get("approvals", [])
        # Also check reviews for APPROVED state
        seen_approvals: dict[str, datetime] = {}
        for app in approvals:
            rev_name = app.get("reviewer")
            app_at = app.get("approvedAt")
            if rev_name and app_at and (include_bots or not is_bot(rev_name)):
                app_dt = parse_iso(app_at)
                if rev_name not in seen_approvals or app_dt < seen_approvals[rev_name]:
                    seen_approvals[rev_name] = app_dt

        first_lgtm_dt = min(seen_approvals.values()) if seen_approvals else None

        # Time from first reviewer requested to first LGTM
        if first_reviewer_req_dt and first_lgtm_dt:
            first_req_to_lgtm_hrs = max(
                0.0, (first_lgtm_dt - first_reviewer_req_dt).total_seconds() / 3600.0
            )
            week["first_reviewer_to_lgtm_durations"].append(first_req_to_lgtm_hrs)

        pr_lgtm_durations: list[float] = []
        for rev_name, app_dt in seen_approvals.items():
            # Baseline: when reviewer was requested, or PR creation time if never requested
            req_dt = reviewer_first_requested.get(rev_name, created_dt)
            lgtm_hrs = max(0.0, (app_dt - req_dt).total_seconds() / 3600.0)
            week["added_to_lgtm_durations"].append(lgtm_hrs)
            week["reviewer_lgtm_durations"].setdefault(rev_name, []).append(lgtm_hrs)

            reviewer_aggregates.setdefault(
                rev_name, {"lgtm_durations": [], "turn_durations": []}
            )["lgtm_durations"].append(lgtm_hrs)
            pr_lgtm_durations.append(lgtm_hrs)

        if pr_lgtm_durations:
            auth_entry["added_to_lgtm_durations"].append(min(pr_lgtm_durations))

        # 3. Total PR Lifespan (Submission -> Merge)
        sub_to_merge_hrs: float | None = None
        if merged_dt:
            sub_to_merge_hrs = max(0.0, (merged_dt - created_dt).total_seconds() / 3600.0)
            week["sub_to_merge_durations"].append(sub_to_merge_hrs)
            auth_entry["sub_to_merge_durations"].append(sub_to_merge_hrs)

        # 4. Turn latencies
        rev_turns, auth_turns, per_rev_turns = compute_turns(pr, include_bots=include_bots)
        week["reviewer_turn_durations"].extend(rev_turns)
        week["author_turn_durations"].extend(auth_turns)
        auth_entry["author_turn_durations"].extend(auth_turns)

        for rev_name, r_turns in per_rev_turns.items():
            reviewer_aggregates.setdefault(
                rev_name, {"lgtm_durations": [], "turn_durations": []}
            )["turn_durations"].extend(r_turns)

        # Record PR row for CSV detailed export
        pr_details.append({
            "number": pr["number"],
            "title": pr.get("title", ""),
            "author": pr_author,
            "created_at": pr["createdAt"],
            "merged_at": pr.get("mergedAt", ""),
            "week": week_key,
            "sub_to_first_rev_hrs": round(sub_to_first_reviewer_hrs, 2) if sub_to_first_reviewer_hrs is not None else "",
            "min_added_to_lgtm_hrs": round(min(pr_lgtm_durations), 2) if pr_lgtm_durations else "",
            "sub_to_merge_hrs": round(sub_to_merge_hrs, 2) if sub_to_merge_hrs is not None else "",
            "median_reviewer_turn_hrs": round(statistics.median(rev_turns), 2) if rev_turns else "",
            "approvers": ", ".join(sorted(seen_approvals.keys())),
            "all_reviewers": ", ".join(sorted(set(list(reviewer_first_requested.keys()) + pr.get("other_reviewers", [])))),
        })

    return {
        "weekly": weekly_groups,
        "reviewers": reviewer_aggregates,
        "authors": author_aggregates,
        "pr_details": pr_details,
    }


def generate_markdown_report(
    analysis: dict[str, Any], metadata: dict[str, Any]
) -> str:
    """Format full analysis into a clean, Github-Flavored Markdown report."""
    weekly = analysis["weekly"]
    reviewers = analysis["reviewers"]
    pr_details = analysis["pr_details"]

    sorted_weeks = sorted(weekly.keys())

    # Overall totals
    total_prs = len(pr_details)
    all_added_to_lgtm: list[float] = []
    all_sub_to_first_rev: list[float] = []
    all_first_rev_to_lgtm: list[float] = []
    all_rev_turns: list[float] = []
    all_auth_turns: list[float] = []
    all_sub_to_merge: list[float] = []

    for w_data in weekly.values():
        all_added_to_lgtm.extend(w_data["added_to_lgtm_durations"])
        all_sub_to_first_rev.extend(w_data["sub_to_first_reviewer_durations"])
        all_first_rev_to_lgtm.extend(w_data["first_reviewer_to_lgtm_durations"])
        all_rev_turns.extend(w_data["reviewer_turn_durations"])
        all_auth_turns.extend(w_data["author_turn_durations"])
        all_sub_to_merge.extend(w_data["sub_to_merge_durations"])

    stats_added_to_lgtm = calc_stats(all_added_to_lgtm)
    stats_sub_to_rev = calc_stats(all_sub_to_first_rev)
    stats_rev_turns = calc_stats(all_rev_turns)
    stats_sub_to_merge = calc_stats(all_sub_to_merge)

    lines: list[str] = []
    lines.append("# A2UI Code Review Performance Report\n")
    lines.append(f"> **Repository:** `{metadata.get('repository', 'a2ui-project/a2ui')}`  ")
    lines.append(f"> **Data Timeframe:** {metadata.get('filters', {}).get('since', 'N/A')} to {metadata.get('filters', {}).get('until', 'N/A')}  ")
    lines.append(f"> **Generated at:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}  ")
    lines.append(f"> **Merged PRs Analyzed:** {total_prs}\n")

    lines.append("## Executive Summary\n")
    lines.append("| Metric | Median | 90th Percentile (P90) | Sample Count |")
    lines.append("| :--- | :---: | :---: | :---: |")
    lines.append(
        f"| **Reviewer Added &rarr; LGTM** | **{format_duration(float(stats_added_to_lgtm['median']))}** ({stats_added_to_lgtm['median']}h) | **{format_duration(float(stats_added_to_lgtm['p90']))}** ({stats_added_to_lgtm['p90']}h) | {stats_added_to_lgtm['count']} approvals |"
    )
    lines.append(
        f"| **Reviewer Turn Time** (Author Action &rarr; Reviewer Response) | **{format_duration(float(stats_rev_turns['median']))}** ({stats_rev_turns['median']}h) | **{format_duration(float(stats_rev_turns['p90']))}** ({stats_rev_turns['p90']}h) | {stats_rev_turns['count']} turns |"
    )
    lines.append(
        f"| **Submission &rarr; First Reviewer Added** | **{format_duration(float(stats_sub_to_rev['median']))}** ({stats_sub_to_rev['median']}h) | **{format_duration(float(stats_sub_to_rev['p90']))}** ({stats_sub_to_rev['p90']}h) | {stats_sub_to_rev['count']} PRs |"
    )
    lines.append(
        f"| **PR Lifespan** (Submission &rarr; Merge) | **{format_duration(float(stats_sub_to_merge['median']))}** ({stats_sub_to_merge['median']}h) | **{format_duration(float(stats_sub_to_merge['p90']))}** ({stats_sub_to_merge['p90']}h) | {stats_sub_to_merge['count']} PRs |"
    )
    lines.append("\n---\n")

    lines.append("## Week-by-Week Breakdown (by PR Submission Time)\n")
    lines.append(
        "Each pull request is assigned to a week based on its **submission time** (`createdAt`).\n"
    )
    lines.append(
        "| Week | Range | Merged PRs | Added &rarr; LGTM (Median) | Added &rarr; LGTM (P90) | Sub &rarr; Rev Added (Median) | Sub &rarr; Rev Added (P90) | Rev Turn (Median) | Rev Turn (P90) | Sub &rarr; Merge (Median) |"
    )
    lines.append(
        "| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |"
    )

    for wk in sorted_weeks:
        w_data = weekly[wk]
        st_lgtm = calc_stats(w_data["added_to_lgtm_durations"])
        st_sub_rev = calc_stats(w_data["sub_to_first_reviewer_durations"])
        st_rev_turn = calc_stats(w_data["reviewer_turn_durations"])
        st_merge = calc_stats(w_data["sub_to_merge_durations"])

        med_lgtm_str = f"{format_duration(float(st_lgtm['median']))}" if st_lgtm["count"] else "-"
        p90_lgtm_str = f"{format_duration(float(st_lgtm['p90']))}" if st_lgtm["count"] else "-"
        med_sub_rev_str = f"{format_duration(float(st_sub_rev['median']))}" if st_sub_rev["count"] else "-"
        p90_sub_rev_str = f"{format_duration(float(st_sub_rev['p90']))}" if st_sub_rev["count"] else "-"
        med_rev_turn_str = f"{format_duration(float(st_rev_turn['median']))}" if st_rev_turn["count"] else "-"
        p90_rev_turn_str = f"{format_duration(float(st_rev_turn['p90']))}" if st_rev_turn["count"] else "-"
        med_merge_str = f"{format_duration(float(st_merge['median']))}" if st_merge["count"] else "-"

        lines.append(
            f"| `{wk}` | {w_data['week_range']} | {len(w_data['prs'])} | {med_lgtm_str} | {p90_lgtm_str} | {med_sub_rev_str} | {p90_sub_rev_str} | {med_rev_turn_str} | {p90_rev_turn_str} | {med_merge_str} |"
        )

    lines.append("\n---\n")

    lines.append("## Individual Reviewer Performance\n")
    lines.append(
        "Metrics for active code reviewers across the entire analysis window:\n"
    )
    lines.append(
        "| Reviewer | Approvals (LGTMs) | Median Added &rarr; LGTM | P90 Added &rarr; LGTM | Reviewer Turns | Median Turn Time | P90 Turn Time |"
    )
    lines.append(
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: |"
    )

    # Sort reviewers by approvals count descending
    sorted_revs = sorted(
        reviewers.items(),
        key=lambda item: len(item[1]["lgtm_durations"]),
        reverse=True,
    )

    for rev_name, rev_data in sorted_revs:
        lgtm_st = calc_stats(rev_data["lgtm_durations"])
        turn_st = calc_stats(rev_data["turn_durations"])

        med_lgtm = format_duration(float(lgtm_st["median"])) if lgtm_st["count"] else "-"
        p90_lgtm = format_duration(float(lgtm_st["p90"])) if lgtm_st["count"] else "-"
        med_turn = format_duration(float(turn_st["median"])) if turn_st["count"] else "-"
        p90_turn = format_duration(float(turn_st["p90"])) if turn_st["count"] else "-"

        lines.append(
            f"| **`@{rev_name}`** | {lgtm_st['count']} | {med_lgtm} | {p90_lgtm} | {turn_st['count']} | {med_turn} | {p90_turn} |"
        )

    lines.append("\n---\n")

    lines.append("## Individual Author Performance\n")
    lines.append(
        "Metrics for pull request authors across the entire analysis window:\n"
    )
    lines.append(
        "| Author | Merged PRs | Median Added &rarr; LGTM | P90 Added &rarr; LGTM | Median Sub &rarr; Rev Added | Median Sub &rarr; Merge | Author Turns | Median Turn Time | P90 Turn Time |"
    )
    lines.append(
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |"
    )

    authors = analysis.get("authors", {})
    sorted_authors = sorted(
        authors.items(),
        key=lambda item: item[1]["prs_count"],
        reverse=True,
    )

    for auth_name, auth_data in sorted_authors:
        st_lgtm = calc_stats(auth_data["added_to_lgtm_durations"])
        st_sub_rev = calc_stats(auth_data["sub_to_first_rev_durations"])
        st_merge = calc_stats(auth_data["sub_to_merge_durations"])
        st_turn = calc_stats(auth_data["author_turn_durations"])

        med_lgtm = format_duration(float(st_lgtm["median"])) if st_lgtm["count"] else "-"
        p90_lgtm = format_duration(float(st_lgtm["p90"])) if st_lgtm["count"] else "-"
        med_sub_rev = format_duration(float(st_sub_rev["median"])) if st_sub_rev["count"] else "-"
        med_merge = format_duration(float(st_merge["median"])) if st_merge["count"] else "-"
        med_turn = format_duration(float(st_turn["median"])) if st_turn["count"] else "-"
        p90_turn = format_duration(float(st_turn["p90"])) if st_turn["count"] else "-"

        lines.append(
            f"| **`@{auth_name}`** | {auth_data['prs_count']} | {med_lgtm} | {p90_lgtm} | {med_sub_rev} | {med_merge} | {st_turn['count']} | {med_turn} | {p90_turn} |"
        )

    lines.append("\n---\n")

    lines.append("## Metric Definitions\n")
    lines.append("- **Added &rarr; LGTM**: Elapsed time between when a reviewer is requested (`ReviewRequestedEvent`) and when they submit an `APPROVED` review. (If not explicitly requested beforehand, uses PR submission time).")
    lines.append("- **Submission &rarr; Reviewer Added**: Elapsed time between PR creation (`createdAt`) and the timestamp the first reviewer was assigned.")
    lines.append("- **Reviewer Turn Time**: Latency between an author action (PR opened, reviewer requested, author pushed commit, or author replied) and a reviewer action (submitting review or posting a comment). This is the key metric reflecting reviewer responsiveness.")
    lines.append("- **Author Turn Time**: Latency between a reviewer action (requesting changes or asking questions) and the author's response (new commit or reply).")
    lines.append("- **PR Lifespan**: Total duration from PR creation to merge.")
    lines.append("- **Bot Filtering**: Automated accounts (e.g. `gemini-code-assist`, `github-actions[bot]`) are excluded by default to avoid skewing human review times.")

    return "\n".join(lines)


def export_csv_reports(analysis: dict[str, Any], output_dir: Path) -> None:
    """Export weekly metrics, reviewer metrics, author metrics, and detailed PR rows to CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)
    weekly = analysis["weekly"]
    reviewers = analysis["reviewers"]
    authors = analysis.get("authors", {})
    pr_details = analysis["pr_details"]

    # 1. Weekly CSV
    weekly_csv_path = output_dir / "weekly_metrics.csv"
    with open(weekly_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "week",
            "date_range",
            "merged_prs_count",
            "added_to_lgtm_median_hours",
            "added_to_lgtm_p90_hours",
            "sub_to_first_rev_median_hours",
            "sub_to_first_rev_p90_hours",
            "reviewer_turn_median_hours",
            "reviewer_turn_p90_hours",
            "sub_to_merge_median_hours",
            "sub_to_merge_p90_hours",
        ])
        for wk in sorted(weekly.keys()):
            w_data = weekly[wk]
            st_lgtm = calc_stats(w_data["added_to_lgtm_durations"])
            st_sub_rev = calc_stats(w_data["sub_to_first_reviewer_durations"])
            st_rev_turn = calc_stats(w_data["reviewer_turn_durations"])
            st_merge = calc_stats(w_data["sub_to_merge_durations"])
            writer.writerow([
                wk,
                w_data["week_range"],
                len(w_data["prs"]),
                st_lgtm["median"],
                st_lgtm["p90"],
                st_sub_rev["median"],
                st_sub_rev["p90"],
                st_rev_turn["median"],
                st_rev_turn["p90"],
                st_merge["median"],
                st_merge["p90"],
            ])

    # 2. Reviewer CSV
    reviewer_csv_path = output_dir / "reviewer_metrics.csv"
    with open(reviewer_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "reviewer",
            "approvals_count",
            "added_to_lgtm_median_hours",
            "added_to_lgtm_p90_hours",
            "turns_count",
            "turn_median_hours",
            "turn_p90_hours",
        ])
        for rev_name, rev_data in sorted(reviewers.items()):
            lgtm_st = calc_stats(rev_data["lgtm_durations"])
            turn_st = calc_stats(rev_data["turn_durations"])
            writer.writerow([
                rev_name,
                lgtm_st["count"],
                lgtm_st["median"],
                lgtm_st["p90"],
                turn_st["count"],
                turn_st["median"],
                turn_st["p90"],
            ])

    # 3. Author CSV
    author_csv_path = output_dir / "author_metrics.csv"
    with open(author_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "author",
            "merged_prs_count",
            "added_to_lgtm_median_hours",
            "added_to_lgtm_p90_hours",
            "sub_to_first_rev_median_hours",
            "sub_to_first_rev_p90_hours",
            "sub_to_merge_median_hours",
            "sub_to_merge_p90_hours",
            "author_turns_count",
            "author_turn_median_hours",
            "author_turn_p90_hours",
        ])
        for auth_name, auth_data in sorted(
            authors.items(), key=lambda item: item[1]["prs_count"], reverse=True
        ):
            st_lgtm = calc_stats(auth_data["added_to_lgtm_durations"])
            st_sub_rev = calc_stats(auth_data["sub_to_first_rev_durations"])
            st_merge = calc_stats(auth_data["sub_to_merge_durations"])
            st_turn = calc_stats(auth_data["author_turn_durations"])
            writer.writerow([
                auth_name,
                auth_data["prs_count"],
                st_lgtm["median"],
                st_lgtm["p90"],
                st_sub_rev["median"],
                st_sub_rev["p90"],
                st_merge["median"],
                st_merge["p90"],
                st_turn["count"],
                st_turn["median"],
                st_turn["p90"],
            ])

    # 4. Detailed PRs CSV
    pr_csv_path = output_dir / "pr_details.csv"
    with open(pr_csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "number",
            "title",
            "author",
            "created_at",
            "merged_at",
            "week",
            "sub_to_first_rev_hrs",
            "min_added_to_lgtm_hrs",
            "sub_to_merge_hrs",
            "median_reviewer_turn_hrs",
            "approvers",
            "all_reviewers",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in pr_details:
            writer.writerow(row)


def filter_prs(
    prs: list[dict[str, Any]],
    author: str | None = None,
    reviewer: str | None = None,
    since: str | None = None,
    until: str | None = None,
) -> list[dict[str, Any]]:
    """Filter raw PR list in memory by author, reviewer, or date range."""
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

        filtered.append(pr)

    return filtered


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate review metrics and markdown report from raw PR data."
    )
    parser.add_argument(
        "--input",
        default="scripts/data/raw_prs.json",
        help="Input JSON file path containing raw PRs (default: scripts/data/raw_prs.json)",
    )
    parser.add_argument(
        "--markdown",
        default="scripts/reports/review_report.md",
        help="Output Markdown report path (default: scripts/reports/review_report.md)",
    )
    parser.add_argument(
        "--csv-dir",
        default="scripts/reports",
        help="Directory to output CSV summary and detailed files (default: scripts/reports)",
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

    filtered_prs = filter_prs(
        prs,
        author=args.author,
        reviewer=args.reviewer,
        since=args.since,
        until=args.until,
    )

    print(f"Analyzing {len(filtered_prs)} PRs (filtered from {len(prs)} total in {input_path})...")

    analysis = analyze_prs(filtered_prs, include_bots=args.include_bots)

    # Generate Markdown Report
    report_md = generate_markdown_report(analysis, metadata)
    md_output_path = Path(args.markdown)
    md_output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(md_output_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"Saved Markdown report to {md_output_path}")

    # Export CSVs
    csv_dir_path = Path(args.csv_dir)
    export_csv_reports(analysis, csv_dir_path)
    print(f"Exported CSV reports to {csv_dir_path}/ (weekly_metrics.csv, reviewer_metrics.csv, pr_details.csv)")

    if args.stdout:
        print("\n" + "=" * 80)
        print(report_md)


if __name__ == "__main__":
    main()
