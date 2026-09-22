# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for JSON payload autofixer."""

import unittest
from a2ui.core import A2uiParseError
from a2ui.parser.payload_fixer import (
    _remove_trailing_commas,
    parse_and_fix,
)


class TestPayloadFixer(unittest.TestCase):
    """Unit test suite for payload_fixer."""

    def test_unescaped_backslashes_error_hint(self):
        """Verify invalid backslashes (e.g. LaTeX) produce an actionable error hint."""
        invalid_json = r'{"formula": "\approx \Delta x"}'
        with self.assertRaises(A2uiParseError) as ctx:
            parse_and_fix(invalid_json)
        self.assertIn('Help: Unescaped backslash found', str(ctx.exception))
        self.assertIn(
            'In JSON strings, all backslashes must be escaped', str(ctx.exception)
        )

    def test_fix_trailing_commas(self):
        """Verify trailing commas in objects and arrays are cleanly removed."""
        trailing_comma_json = r'{"a": [1, 2, ], "b": {"k": "v", }, }'
        fixed = _remove_trailing_commas(trailing_comma_json)
        self.assertNotIn(', ]', fixed)
        self.assertNotIn(', }', fixed)

    def test_parse_and_fix_recovers_trailing_commas(self):
        """Verify parse_and_fix recovers payloads with trailing commas."""
        corrupt_payload = (
            r'[{"version": "v0.9", "createSurface": {"surfaceId": "default",'
            r' "components": ['
            r'{"id": "t1", "component": "Text", "text": "Hello world",},'
            r']}}]'
        )
        res = parse_and_fix(corrupt_payload)
        self.assertEqual(len(res), 1)
        components = res[0]['createSurface']['components']
        self.assertEqual(components[0]['text'], 'Hello world')

    def test_normalize_version_without_v(self):
        """Verify version strings missing the leading 'v' (e.g. '0.9') are normalized."""
        payload = '[{"version": "0.9", "createSurface": {"surfaceId": "s1"}}]'
        res = parse_and_fix(payload)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["version"], "v0.9")

    def test_normalize_version_1_0(self):
        """Verify version '1.0' is normalized to 'v1.0'."""
        payload = '[{"version": "1.0", "createSurface": {"surfaceId": "s1"}}]'
        res = parse_and_fix(payload)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["version"], "v1.0")

    def test_inject_missing_version_with_target(self):
        """Verify missing version is injected when target_version is specified."""
        payload = '[{"createSurface": {"surfaceId": "s1"}}]'
        res = parse_and_fix(payload, target_version="0.9.1")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["version"], "v0.9.1")

    def test_preserve_existing_valid_version(self):
        """Verify existing valid version strings starting with 'v' are preserved."""
        payload = '[{"version": "v0.9", "createSurface": {"surfaceId": "s1"}}]'
        res = parse_and_fix(payload, target_version="0.9.1")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["version"], "v0.9")

    def test_v08_target_version_does_not_inject_version(self):
        """Verify target_version='0.8' does not inject a version property."""
        payload = '[{"beginRendering": {"surfaceId": "s1"}}]'
        res = parse_and_fix(payload, target_version="0.8")
        self.assertEqual(len(res), 1)
        self.assertNotIn("version", res[0])
