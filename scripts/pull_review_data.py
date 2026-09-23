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

"""Stage 1: Pull raw review metadata for merged Pull Requests from GitHub.

Pulls pull request metadata, review requests, reviews, comments, and commit
timestamps via GitHub GraphQL API and saves the raw data to a .gitignored location.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

# Default bot logins to identify automated actions
DEFAULT_BOTS = {
    "gemini-code-assist",
    "google-claude-agent",
    "google-github-actions",
    "google-cla",
    "github-actions",
    "copybara-service",
    "a2ui-bot",
}

PR_SEARCH_GRAPHQL = """
query($searchQuery: String!, $cursor: String) {
  search(query: $searchQuery, type: ISSUE, first: 25, after: $cursor) {
    issueCount
    pageInfo {
      hasNextPage
      endCursor
    }
    nodes {
      ... on PullRequest {
        number
        title
        url
        createdAt
        mergedAt
        isDraft
        author {
          login
        }
        reviews(first: 50) {
          nodes {
            author {
              login
            }
            state
            submittedAt
          }
        }
        reviewRequests(first: 30) {
          nodes {
            requestedReviewer {
              ... on User {
                login
              }
              ... on Team {
                slug
              }
            }
          }
        }
        timelineItems(first: 100, itemTypes: [
          REVIEW_REQUESTED_EVENT,
          PULL_REQUEST_REVIEW,
          ISSUE_COMMENT,
          PULL_REQUEST_COMMIT,
          PULL_REQUEST_REVIEW_THREAD,
          READY_FOR_REVIEW_EVENT
        ]) {
          nodes {
            __typename
            ... on ReviewRequestedEvent {
              createdAt
              requestedReviewer {
                ... on User {
                  login
                }
                ... on Team {
                  slug
                }
              }
            }
            ... on PullRequestReview {
              author {
                login
              }
              state
              submittedAt
            }
            ... on IssueComment {
              author {
                login
              }
              createdAt
            }
            ... on PullRequestCommit {
              commit {
                committedDate
                author {
                  user {
                    login
                  }
                }
              }
            }
            ... on PullRequestReviewThread {
              comments(first: 20) {
                nodes {
                  author {
                    login
                  }
                  createdAt
                }
              }
            }
            ... on ReadyForReviewEvent {
              createdAt
            }
          }
        }
      }
    }
  }
}
"""


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


def run_gh_graphql(query: str, variables: dict[str, Any]) -> dict[str, Any]:
    """Execute a GitHub GraphQL query via the gh CLI."""
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, val in variables.items():
        if val is not None:
            cmd.extend(["-F", f"{key}={val}"])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"gh api error: {result.stderr.strip()}")

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as err:
        raise RuntimeError(f"Failed to parse gh api output: {err}\nOutput: {result.stdout}")

    if "errors" in data and not data.get("data"):
        raise RuntimeError(f"GraphQL error: {data['errors']}")

    return data


def parse_pr_node(pr: dict[str, Any]) -> dict[str, Any]:
    """Normalize raw GitHub PR node into structured review data."""
    pr_number = pr["number"]
    title = pr.get("title", "")
    url = pr.get("url", "")
    created_at = pr["createdAt"]
    merged_at = pr.get("mergedAt")
    is_draft = pr.get("isDraft", False)

    author_obj = pr.get("author")
    pr_author = author_obj.get("login") if author_obj else "ghost"

    # Listed reviewers requested via events or active requests
    # Store reviewer -> list of requestedAt timestamps
    listed_reviewers: dict[str, list[str]] = {}
    approvals: list[dict[str, Any]] = []
    reviews: list[dict[str, Any]] = []
    comments: list[dict[str, Any]] = []
    commits: list[dict[str, Any]] = []
    timeline_events: list[dict[str, Any]] = []

    # Initial event: PR creation
    timeline_events.append({
        "type": "pr_created",
        "timestamp": created_at,
        "author": pr_author,
        "role": "author",
    })

    # Direct reviewRequests (currently active, if any)
    for req in pr.get("reviewRequests", {}).get("nodes", []):
        rev = req.get("requestedReviewer")
        if rev:
            login = rev.get("login") or rev.get("slug")
            if login and login != pr_author:
                listed_reviewers.setdefault(login, [])

    # Direct reviews
    for rev in pr.get("reviews", {}).get("nodes", []):
        rev_author_obj = rev.get("author")
        rev_author = rev_author_obj.get("login") if rev_author_obj else None
        state = rev.get("state")
        sub_at = rev.get("submittedAt")
        if rev_author and sub_at:
            reviews.append({
                "author": rev_author,
                "state": state,
                "submittedAt": sub_at,
            })
            if state == "APPROVED":
                approvals.append({
                    "reviewer": rev_author,
                    "approvedAt": sub_at,
                })

    # Traverse timeline items
    timeline_nodes = pr.get("timelineItems", {}).get("nodes", [])
    for item in timeline_nodes:
        typename = item.get("__typename")
        if typename == "ReviewRequestedEvent":
            req_at = item.get("createdAt")
            reviewer_obj = item.get("requestedReviewer")
            if reviewer_obj and req_at:
                rev_login = reviewer_obj.get("login") or reviewer_obj.get("slug")
                if rev_login and rev_login != pr_author:
                    listed_reviewers.setdefault(rev_login, []).append(req_at)
                    timeline_events.append({
                        "type": "reviewer_requested",
                        "timestamp": req_at,
                        "author": pr_author,
                        "reviewer": rev_login,
                        "role": "author",
                    })

        elif typename == "PullRequestReview":
            sub_at = item.get("submittedAt")
            rev_author_obj = item.get("author")
            rev_author = rev_author_obj.get("login") if rev_author_obj else None
            state = item.get("state")
            if rev_author and sub_at:
                role = "bot" if is_bot(rev_author) else ("author" if rev_author == pr_author else "reviewer")
                timeline_events.append({
                    "type": "review",
                    "timestamp": sub_at,
                    "author": rev_author,
                    "state": state,
                    "role": role,
                })

        elif typename == "IssueComment":
            comm_at = item.get("createdAt")
            comm_author_obj = item.get("author")
            comm_author = comm_author_obj.get("login") if comm_author_obj else None
            if comm_author and comm_at:
                role = "bot" if is_bot(comm_author) else ("author" if comm_author == pr_author else "reviewer")
                comments.append({
                    "author": comm_author,
                    "createdAt": comm_at,
                    "type": "issue_comment",
                })
                timeline_events.append({
                    "type": "comment",
                    "timestamp": comm_at,
                    "author": comm_author,
                    "role": role,
                })

        elif typename == "PullRequestCommit":
            commit_info = item.get("commit", {})
            comm_date = commit_info.get("committedDate")
            c_author_obj = commit_info.get("author", {}).get("user")
            c_author = c_author_obj.get("login") if c_author_obj else pr_author
            if comm_date:
                commits.append({
                    "author": c_author,
                    "committedDate": comm_date,
                })
                timeline_events.append({
                    "type": "commit",
                    "timestamp": comm_date,
                    "author": c_author,
                    "role": "author" if c_author == pr_author else "contributor",
                })

        elif typename == "PullRequestReviewThread":
            thread_comments = item.get("comments", {}).get("nodes", [])
            for c in thread_comments:
                c_at = c.get("createdAt")
                c_auth_obj = c.get("author")
                c_auth = c_auth_obj.get("login") if c_auth_obj else None
                if c_auth and c_at:
                    role = "bot" if is_bot(c_auth) else ("author" if c_auth == pr_author else "reviewer")
                    comments.append({
                        "author": c_auth,
                        "createdAt": c_at,
                        "type": "review_comment",
                    })
                    timeline_events.append({
                        "type": "comment",
                        "timestamp": c_at,
                        "author": c_auth,
                        "role": role,
                    })

        elif typename == "ReadyForReviewEvent":
            ready_at = item.get("createdAt")
            if ready_at:
                timeline_events.append({
                    "type": "ready_for_review",
                    "timestamp": ready_at,
                    "author": pr_author,
                    "role": "author",
                })

    if merged_at:
        timeline_events.append({
            "type": "merged",
            "timestamp": merged_at,
            "author": pr_author,
            "role": "system",
        })

    # Sort timeline events chronologically
    timeline_events.sort(key=lambda ev: ev["timestamp"])

    # Identify other reviewers (people who reviewed or commented but were not listed)
    all_listed = set(listed_reviewers.keys())
    other_reviewers: set[str] = set()
    for rev in reviews:
        r_auth = rev["author"]
        if r_auth != pr_author and not is_bot(r_auth) and r_auth not in all_listed:
            other_reviewers.add(r_auth)
    for c in comments:
        c_auth = c["author"]
        if c_auth != pr_author and not is_bot(c_auth) and c_auth not in all_listed:
            other_reviewers.add(c_auth)

    return {
        "number": pr_number,
        "title": title,
        "url": url,
        "createdAt": created_at,
        "mergedAt": merged_at,
        "isDraft": is_draft,
        "author": pr_author,
        "listed_reviewers": [
            {"login": k, "requestedAt": min(v) if v else None, "allRequests": v}
            for k, v in listed_reviewers.items()
        ],
        "other_reviewers": sorted(list(other_reviewers)),
        "reviews": reviews,
        "approvals": approvals,
        "comments": comments,
        "commits": commits,
        "timeline_events": timeline_events,
    }


def pull_prs(
    repo: str,
    since_date: str,
    until_date: str | None = None,
    author: str | None = None,
    reviewer: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Query GitHub GraphQL for merged PRs matching criteria and pull all metadata."""
    query_parts = [
        f"repo:{repo}",
        "is:pr",
        "is:merged",
        f"created:>={since_date}",
    ]
    if until_date:
        query_parts.append(f"created:<={until_date}")
    if author:
        query_parts.append(f"author:{author}")
    if reviewer:
        query_parts.append(f"reviewed-by:{reviewer}")

    search_query = " ".join(query_parts)
    print(f"Executing GitHub search: {search_query}")

    all_prs: list[dict[str, Any]] = []
    cursor: str | None = None
    has_next_page = True
    page_num = 1

    while has_next_page:
        print(f"Fetching page {page_num}... (accumulated: {len(all_prs)} PRs)", end="\r", flush=True)
        response = run_gh_graphql(
            PR_SEARCH_GRAPHQL,
            {"searchQuery": search_query, "cursor": cursor},
        )
        search_res = response["data"]["search"]
        total_matched = search_res.get("issueCount", 0)
        page_info = search_res.get("pageInfo", {})
        has_next_page = page_info.get("hasNextPage", False)
        cursor = page_info.get("endCursor")

        raw_nodes = search_res.get("nodes", [])
        for node in raw_nodes:
            if not node or "number" not in node:
                continue
            parsed = parse_pr_node(node)
            all_prs.append(parsed)
            if limit and len(all_prs) >= limit:
                has_next_page = False
                break

        page_num += 1

    print(f"\nCompleted! Retrieved {len(all_prs)} merged PRs out of {total_matched} matching.")
    return all_prs


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pull raw review data for merged PRs in A2UI repository."
    )
    parser.add_argument(
        "--repo",
        default="a2ui-project/a2ui",
        help="GitHub repository in owner/repo format (default: a2ui-project/a2ui)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=84,
        help="Number of days of history to pull (default: 84 = 12 weeks)",
    )
    parser.add_argument(
        "--since",
        help="Start date in YYYY-MM-DD format (overrides --days)",
    )
    parser.add_argument(
        "--until",
        help="End date in YYYY-MM-DD format (default: now)",
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
        "--limit",
        type=int,
        help="Maximum number of PRs to pull (useful for quick prototyping)",
    )
    parser.add_argument(
        "--output",
        default="scripts/data/raw_prs.json",
        help="Output JSON file path (default: scripts/data/raw_prs.json)",
    )

    args = parser.parse_args()

    # Determine date range
    now_utc = datetime.now(timezone.utc)
    if args.since:
        since_date = args.since
    else:
        since_dt = now_utc - timedelta(days=args.days)
        since_date = since_dt.strftime("%Y-%m-%d")

    until_date = args.until or now_utc.strftime("%Y-%m-%d")

    prs = pull_prs(
        repo=args.repo,
        since_date=since_date,
        until_date=until_date,
        author=args.author,
        reviewer=args.reviewer,
        limit=args.limit,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_payload = {
        "metadata": {
            "repository": args.repo,
            "pulled_at": now_utc.isoformat(),
            "filters": {
                "days": args.days,
                "since": since_date,
                "until": until_date,
                "author": args.author,
                "reviewer": args.reviewer,
                "limit": args.limit,
            },
            "total_prs": len(prs),
        },
        "prs": prs,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2)

    print(f"Saved raw PR data to {output_path} ({os.path.getsize(output_path) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
