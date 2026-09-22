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

import json
import logging
import re
from typing import Any, Dict, List, Optional
from a2ui.core import A2uiParseError


logger = logging.getLogger(__name__)


def parse_and_fix(
    payload: str, target_version: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Validates and applies autofixes to a raw JSON string and returns the parsed payload.

    Args:
      payload: The raw JSON string from the LLM.
      target_version: Optional canonical protocol version to normalize or inject if missing.

    Returns:
      A parsed and potentially fixed payload (list of dicts).
    """
    normalized_payload = _normalize_smart_quotes(payload)
    try:
        a2ui_json = _parse(normalized_payload, target_version=target_version)
        return a2ui_json
    except (
        json.JSONDecodeError,
        ValueError,
        A2uiParseError,
    ) as e:
        logger.warning(f"Initial A2UI payload validation failed: {e}")
        updated_payload = _remove_trailing_commas(normalized_payload)
        a2ui_json = _parse(updated_payload, target_version=target_version)
        return a2ui_json


def _normalize_version(
    msg: Dict[str, Any], target_version: Optional[str] = None
) -> None:
    """Auto-heals the protocol version on an A2UI message dictionary."""
    canonical_target = None
    if target_version and target_version not in ("0.8", "v0.8"):
        canonical_target = (
            target_version if target_version.startswith("v") else f"v{target_version}"
        )

    ver = msg.get("version")
    if ver is not None and isinstance(ver, str):
        # Normalize numeric versions (e.g. "0.9", "0.9.1", "1.0") to include the 'v' prefix
        if not ver.startswith("v"):
            msg["version"] = f"v{ver}"
    elif ver is None and canonical_target:
        msg["version"] = canonical_target


def _parse(
    payload: str, target_version: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Parses the payload and returns a list of A2UI JSON objects."""
    try:
        a2ui_json = json.loads(payload)
        if not isinstance(a2ui_json, list):
            logger.info(
                "Received a single JSON object, wrapping in a list for validation."
            )
            a2ui_json = [a2ui_json]
        for item in a2ui_json:
            if isinstance(item, dict):
                _normalize_version(item, target_version=target_version)
        return a2ui_json
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}")
        hint = ""
        if "Invalid \\escape" in e.msg:
            hint = (
                f" - Help: Unescaped backslash found at line {e.lineno}, col"
                f" {e.colno}. In JSON strings, all backslashes must be escaped"
                " as '\\\\' (e.g. '\\\\approx', '\\\\alpha')."
            )
        raise A2uiParseError(f"Failed to parse JSON: {e}{hint}") from e


def _normalize_smart_quotes(json_str: str) -> str:
    """Replaces smart (curly) quotes with standard straight quotes."""
    return (
        json_str.replace("\u201C", '"')
        .replace("\u201D", '"')
        .replace("\u2018", "'")
        .replace("\u2019", "'")
    )


def _remove_trailing_commas(json_str: str) -> str:
    """Attempts to remove trailing commas from a JSON string.

    Args:
      json_str: The raw JSON string from the LLM.

    Returns:
      A potentially fixed JSON string.
    """
    # Fix trailing commas: identifying commas followed by optional whitespace and a closing bracket (]) or brace (}).
    fixed_json = re.sub(r",(?=\s*[\]}])", "", json_str)

    if fixed_json != json_str:
        logger.warning("Detected trailing commas in LLM output; applied autofix.")

    return fixed_json
