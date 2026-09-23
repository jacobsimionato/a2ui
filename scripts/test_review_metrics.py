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

"""Unit tests for review metrics extraction and analytics pipeline."""

from datetime import datetime, timezone
import unittest

from scripts.generate_review_metrics import (
    analyze_records,
    calc_stats,
    classify_size,
    compute_turns,
    filter_prs,
    format_duration,
    get_interval_info,
    get_n_months_ago_start,
    is_bot,
    percentile,
)
from scripts.pull_review_data import build_review_records, parse_pr_node


class TestReviewPipeline(unittest.TestCase):

    # -------------------------------------------------------------------------
    # Part 1: pull_review_data.py tests
    # -------------------------------------------------------------------------

    def test_parse_pr_node_with_loc(self):
        node = {
            "number": 2747,
            "title": "feat: dart agent",
            "url": "https://github.com/a2ui-project/a2ui/pull/2747",
            "createdAt": "2026-09-22T22:32:16Z",
            "mergedAt": "2026-09-22T23:44:00Z",
            "isDraft": False,
            "additions": 680,
            "deletions": 24,
            "changedFiles": 20,
            "author": {"login": "polina-c"},
            "reviews": {
                "nodes": [
                    {
                        "author": {"login": "nan-yu"},
                        "state": "APPROVED",
                        "submittedAt": "2026-09-22T23:33:03Z",
                    }
                ]
            },
            "reviewRequests": {"nodes": []},
            "timelineItems": {
                "nodes": [
                    {
                        "__typename": "ReviewRequestedEvent",
                        "createdAt": "2026-09-22T22:45:21Z",
                        "requestedReviewer": {"login": "nan-yu"},
                    },
                    {
                        "__typename": "PullRequestReview",
                        "author": {"login": "nan-yu"},
                        "state": "APPROVED",
                        "submittedAt": "2026-09-22T23:33:03Z",
                    },
                ]
            },
        }

        parsed = parse_pr_node(node)
        self.assertEqual(parsed["number"], 2747)
        self.assertEqual(parsed["additions"], 680)
        self.assertEqual(parsed["deletions"], 24)
        self.assertEqual(parsed["changed_files"], 20)
        self.assertEqual(parsed["total_loc"], 704)
        self.assertEqual(parsed["author"], "polina-c")
        self.assertEqual(len(parsed["listed_reviewers"]), 1)
        self.assertEqual(parsed["listed_reviewers"][0]["login"], "nan-yu")
        self.assertEqual(len(parsed["approvals"]), 1)

    def test_build_review_records(self):
        prs = [
            {
                "number": 100,
                "title": "Test PR",
                "author": "alice",
                "createdAt": "2026-09-20T10:00:00Z",
                "total_loc": 1500,
                "additions": 1200,
                "deletions": 300,
                "listed_reviewers": [{"login": "bob", "requestedAt": "2026-09-20T10:30:00Z"}],
                "approvals": [{"reviewer": "bob", "approvedAt": "2026-09-20T12:30:00Z"}],
            }
        ]
        records = build_review_records(prs)
        self.assertEqual(len(records), 1)
        rec = records[0]
        self.assertEqual(rec["pr_number"], 100)
        self.assertEqual(rec["reviewer"], "bob")
        self.assertEqual(rec["pr_author"], "alice")
        self.assertEqual(rec["pr_total_loc"], 1500)
        self.assertTrue(rec["was_formally_requested"])
        # From 10:30 to 12:30 is 2.0 hours
        self.assertAlmostEqual(rec["added_to_lgtm_hrs"], 2.0)

    # -------------------------------------------------------------------------
    # Part 2: generate_review_metrics.py tests
    # -------------------------------------------------------------------------

    def test_classify_size(self):
        # Binary split around 1000 LoC
        key_small, label_small = classify_size(450, loc_split=1000)
        self.assertEqual(label_small, "< 1000 LoC")

        key_large, label_large = classify_size(1250, loc_split=1000)
        self.assertEqual(label_large, "≥ 1000 LoC")

        # Standard tiers
        _, label_xs = classify_size(50)
        self.assertEqual(label_xs, "< 100 LoC (XS)")
        _, label_s = classify_size(250)
        self.assertEqual(label_s, "100 - 499 LoC (S)")
        _, label_m = classify_size(750)
        self.assertEqual(label_m, "500 - 999 LoC (M)")
        _, label_l = classify_size(2000)
        self.assertEqual(label_l, "1000+ LoC (L)")

    def test_interval_info(self):
        dt = datetime(2026, 9, 22, 12, 0, 0)
        # Week interval
        w_key, w_label = get_interval_info(dt, interval_type="week")
        self.assertEqual(w_key, "2026-W39")
        self.assertIn("Sep 21", w_label)

        # Month interval
        m_key, m_label = get_interval_info(dt, interval_type="month")
        self.assertEqual(m_key, "2026-09")
        self.assertEqual(m_label, "Sep 2026")

    def test_get_n_months_ago_start(self):
        now_dt = datetime(2026, 9, 24, 10, 0, 0, tzinfo=timezone.utc)
        # 4 months ago includes Sep, Aug, Jul, Jun -> starts Jun 1, 2026
        start_dt = get_n_months_ago_start(now_dt, 4)
        self.assertEqual(start_dt.year, 2026)
        self.assertEqual(start_dt.month, 6)
        self.assertEqual(start_dt.day, 1)

    def test_filter_prs_loc(self):
        prs = [
            {"number": 1, "author": "a", "createdAt": "2026-09-01T00:00:00Z", "total_loc": 50},
            {"number": 2, "author": "b", "createdAt": "2026-09-01T00:00:00Z", "total_loc": 500},
            {"number": 3, "author": "c", "createdAt": "2026-09-01T00:00:00Z", "total_loc": 1500},
        ]
        small_only = filter_prs(prs, max_loc=999)
        self.assertEqual([p["number"] for p in small_only], [1, 2])

        large_only = filter_prs(prs, min_loc=1000)
        self.assertEqual([p["number"] for p in large_only], [3])

    def test_analyze_records_multi_dimensional(self):
        # Two PRs in Sep 2026: one <1000 LoC, one >=1000 LoC
        prs = [
            {
                "number": 1,
                "title": "Small fix",
                "author": "alice",
                "createdAt": "2026-09-10T10:00:00Z",
                "mergedAt": "2026-09-10T11:00:00Z",
                "total_loc": 200,
                "listed_reviewers": [{"login": "bob", "requestedAt": "2026-09-10T10:00:00Z"}],
                "approvals": [{"reviewer": "bob", "approvedAt": "2026-09-10T10:30:00Z"}],
                "timeline_events": [
                    {"type": "pr_created", "timestamp": "2026-09-10T10:00:00Z", "author": "alice", "role": "author"},
                    {"type": "reviewer_requested", "timestamp": "2026-09-10T10:00:00Z", "author": "alice", "reviewer": "bob", "role": "author"},
                    {"type": "review", "timestamp": "2026-09-10T10:30:00Z", "author": "bob", "state": "APPROVED", "role": "reviewer"},
                ],
            },
            {
                "number": 2,
                "title": "Large refactor",
                "author": "alice",
                "createdAt": "2026-09-15T10:00:00Z",
                "mergedAt": "2026-09-15T16:00:00Z",
                "total_loc": 2500,
                "listed_reviewers": [{"login": "carol", "requestedAt": "2026-09-15T10:00:00Z"}],
                "approvals": [{"reviewer": "carol", "approvedAt": "2026-09-15T14:00:00Z"}],
                "timeline_events": [
                    {"type": "pr_created", "timestamp": "2026-09-15T10:00:00Z", "author": "alice", "role": "author"},
                    {"type": "reviewer_requested", "timestamp": "2026-09-15T10:00:00Z", "author": "alice", "reviewer": "carol", "role": "author"},
                    {"type": "review", "timestamp": "2026-09-15T14:00:00Z", "author": "carol", "state": "APPROVED", "role": "reviewer"},
                ],
            },
        ]

        analysis = analyze_records(
            prs,
            interval="month",
            group_dimensions=["interval", "size"],
            loc_split=1000,
        )

        groups = analysis["groups"]
        self.assertEqual(len(groups), 2)

        # PR 1: <1000 LoC, Added -> LGTM is 0.5 hours
        g1 = groups[("2026-09", "0_1000")]
        self.assertEqual(len(g1["prs"]), 1)
        self.assertAlmostEqual(g1["added_to_lgtm_durations"][0], 0.5)

        # PR 2: >=1000 LoC, Added -> LGTM is 4.0 hours
        g2 = groups[("2026-09", "1_1000")]
        self.assertEqual(len(g2["prs"]), 1)
        self.assertAlmostEqual(g2["added_to_lgtm_durations"][0], 4.0)

    def test_percentile_and_stats(self):
        self.assertEqual(percentile([], 90), 0.0)
        self.assertEqual(percentile([10.0], 90), 10.0)

        data = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        self.assertAlmostEqual(percentile(data, 50), 5.5)
        self.assertAlmostEqual(percentile(data, 90), 9.1)

        stats = calc_stats(data)
        self.assertEqual(stats["count"], 10)
        self.assertEqual(stats["median"], 5.5)
        self.assertEqual(stats["p90"], 9.1)

    def test_format_duration(self):
        self.assertEqual(format_duration(0.0), "0m")
        self.assertEqual(format_duration(0.25), "15m")
        self.assertEqual(format_duration(1.0), "1h")
        self.assertEqual(format_duration(2.5), "2h 30m")
        self.assertEqual(format_duration(25.0), "1d 1h")
        self.assertEqual(format_duration(48.0), "2d")

    def test_bot_detection(self):
        self.assertTrue(is_bot("gemini-code-assist"))
        self.assertTrue(is_bot("google-claude-agent"))
        self.assertTrue(is_bot("dependabot[bot]"))
        self.assertTrue(is_bot("github-actions[bot]"))
        self.assertTrue(is_bot("google-cla"))
        self.assertFalse(is_bot("jacobsimionato"))
        self.assertFalse(is_bot(None))


if __name__ == "__main__":
    unittest.main()
