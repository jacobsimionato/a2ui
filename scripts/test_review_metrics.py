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

"""Unit tests for review metrics calculation and parsing."""

from datetime import datetime
import unittest

from scripts.generate_review_metrics import (
    analyze_prs,
    calc_stats,
    compute_turns,
    filter_prs,
    format_duration,
    get_week_info,
    is_bot,
    percentile,
)
from scripts.pull_review_data import parse_pr_node


class TestReviewMetrics(unittest.TestCase):

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
        self.assertFalse(is_bot("jacobsimionato"))
        self.assertFalse(is_bot("nan-yu"))
        self.assertFalse(is_bot(None))

    def test_get_week_info(self):
        dt = datetime(2026, 9, 22, 12, 0, 0)
        week_key, week_range = get_week_info(dt)
        self.assertEqual(week_key, "2026-W39")
        self.assertIn("Sep 21", week_range)

    def test_compute_turns(self):
        pr = {
            "author": "alice",
            "timeline_events": [
                {
                    "type": "pr_created",
                    "timestamp": "2026-09-20T10:00:00Z",
                    "author": "alice",
                    "role": "author",
                },
                {
                    "type": "reviewer_requested",
                    "timestamp": "2026-09-20T10:15:00Z",
                    "author": "alice",
                    "reviewer": "bob",
                    "role": "author",
                },
                {
                    "type": "comment",
                    "timestamp": "2026-09-20T10:20:00Z",
                    "author": "gemini-code-assist",
                    "role": "bot",
                },
                {
                    "type": "comment",
                    "timestamp": "2026-09-20T11:15:00Z",
                    "author": "bob",
                    "role": "reviewer",
                },
                {
                    "type": "commit",
                    "timestamp": "2026-09-20T12:15:00Z",
                    "author": "alice",
                    "role": "author",
                },
                {
                    "type": "review",
                    "timestamp": "2026-09-20T12:45:00Z",
                    "author": "bob",
                    "state": "APPROVED",
                    "role": "reviewer",
                },
            ],
        }

        rev_turns, auth_turns, per_rev = compute_turns(pr, include_bots=False)

        # First reviewer turn: Bob responds at 11:15 to Alice's reviewer_requested at 10:15 (1.0 hour)
        # Second reviewer turn: Bob approves at 12:45 after Alice's commit at 12:15 (0.5 hour)
        self.assertEqual(len(rev_turns), 2)
        self.assertAlmostEqual(rev_turns[0], 1.0)
        self.assertAlmostEqual(rev_turns[1], 0.5)

        # Author turn: Alice commits at 12:15 after Bob's comment at 11:15 (1.0 hour)
        self.assertEqual(len(auth_turns), 1)
        self.assertAlmostEqual(auth_turns[0], 1.0)

        self.assertIn("bob", per_rev)
        self.assertEqual(len(per_rev["bob"]), 2)

    def test_filter_prs(self):
        prs = [
            {
                "number": 1,
                "author": "alice",
                "createdAt": "2026-09-10T10:00:00Z",
                "listed_reviewers": [{"login": "bob"}],
                "other_reviewers": [],
            },
            {
                "number": 2,
                "author": "charlie",
                "createdAt": "2026-09-15T10:00:00Z",
                "listed_reviewers": [{"login": "dave"}],
                "other_reviewers": [],
            },
        ]

        by_author = filter_prs(prs, author="alice")
        self.assertEqual(len(by_author), 1)
        self.assertEqual(by_author[0]["number"], 1)

        by_reviewer = filter_prs(prs, reviewer="dave")
        self.assertEqual(len(by_reviewer), 1)
        self.assertEqual(by_reviewer[0]["number"], 2)

        by_date = filter_prs(prs, since="2026-09-12")
        self.assertEqual(len(by_date), 1)
        self.assertEqual(by_date[0]["number"], 2)

    def test_parse_pr_node(self):
        node = {
            "number": 100,
            "title": "Test PR",
            "url": "https://github.com/a2ui-project/a2ui/pull/100",
            "createdAt": "2026-09-20T10:00:00Z",
            "mergedAt": "2026-09-20T15:00:00Z",
            "isDraft": False,
            "author": {"login": "author_user"},
            "reviews": {
                "nodes": [
                    {
                        "author": {"login": "rev_user"},
                        "state": "APPROVED",
                        "submittedAt": "2026-09-20T14:00:00Z",
                    }
                ]
            },
            "reviewRequests": {
                "nodes": [
                    {"requestedReviewer": {"login": "rev_user"}}
                ]
            },
            "timelineItems": {
                "nodes": [
                    {
                        "__typename": "ReviewRequestedEvent",
                        "createdAt": "2026-09-20T10:05:00Z",
                        "requestedReviewer": {"login": "rev_user"},
                    },
                    {
                        "__typename": "PullRequestReview",
                        "author": {"login": "rev_user"},
                        "state": "APPROVED",
                        "submittedAt": "2026-09-20T14:00:00Z",
                    },
                ]
            },
        }

        parsed = parse_pr_node(node)
        self.assertEqual(parsed["number"], 100)
        self.assertEqual(parsed["author"], "author_user")
        self.assertEqual(len(parsed["listed_reviewers"]), 1)
        self.assertEqual(parsed["listed_reviewers"][0]["login"], "rev_user")
        self.assertEqual(parsed["listed_reviewers"][0]["requestedAt"], "2026-09-20T10:05:00Z")
        self.assertEqual(len(parsed["approvals"]), 1)
        self.assertEqual(parsed["approvals"][0]["reviewer"], "rev_user")


if __name__ == "__main__":
    unittest.main()
