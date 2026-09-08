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

"""Parser utilities to extract and compile A2UI Express DSL from LLM responses."""

from typing import Any, List, Union
from a2ui.core.catalog import Catalog
from a2ui.schema.catalog import A2uiCatalog
from a2ui.parser.response_part import ResponsePart
from a2ui.parser.parser import Parser
from google.adk.utils.feature_decorator import experimental
from a2ui.schema.constants import A2UI_INFERENCE_OPEN_TAG, A2UI_INFERENCE_CLOSE_TAG
from .compiler import ExpressCompiler
from .decompiler import _ExpressDecompiler


@experimental
class ExpressParser(Parser):
    """Concrete parser implementation for A2UI Express DSL responses."""

    def __init__(
        self,
        catalog: Union[Catalog[Any, Any], A2uiCatalog],
        surface_id: str = "main",
        version: str = "v1.0",
    ):
        """Initializes the Express parser with a catalog schema and target version.

        Args:
            catalog: Catalog or A2uiCatalog schema helper.
            surface_id: Surface identifier for compiled messages.
            version: Target A2UI protocol version ("v0.9", "v0.9.1", or "v1.0").
        """
        self.catalog = catalog
        self.surface_id = surface_id
        self.version = version

    def has_format_content(self, content: str, *, complete: bool = False) -> bool:
        """Checks whether the given content string contains A2UI Express sentinel tags.

        Args:
            content: The text content to inspect.
            complete: Whether to require both opening and closing sentinel tags.

        Returns:
            True if Express format tags are detected; False otherwise.
        """
        if complete:
            return (
                A2UI_INFERENCE_OPEN_TAG in content
                and A2UI_INFERENCE_CLOSE_TAG in content
            )
        return A2UI_INFERENCE_OPEN_TAG[:-1] in content

    def unwrap(self, content: str) -> List[ResponsePart]:
        """Unwraps/tokenizes the response content into raw Express DSL parts."""
        import re
        from a2ui.parser.lexer import BlockLexer

        lexer = BlockLexer(
            open_tag=A2UI_INFERENCE_OPEN_TAG,
            close_tag=A2UI_INFERENCE_CLOSE_TAG,
            string_delimiters={"'", '"'},
            single_line_comments={"#", "//"},
        )
        parts = lexer.tokenize(content)
        if any(p.a2ui_raw is not None for p in parts):
            return parts

        def looks_like_express(text: str) -> bool:
            if not text or not text.strip():
                return False
            t = text.strip()
            if (t.startswith("[") and t.endswith("]")) or (
                t.startswith("{") and t.endswith("}")
            ):
                try:
                    import json

                    p = json.loads(t)
                    if isinstance(p, dict):
                        p = [p]
                    if isinstance(p, list) and any(
                        isinstance(item, dict)
                        and any(
                            k in item
                            for k in (
                                "createSurface",
                                "updateComponents",
                                "updateDataModel",
                                "deleteSurface",
                            )
                        )
                        for item in p
                    ):
                        return True
                except Exception:
                    pass
            express_pattern = re.compile(
                r"(surface\s*\(|deleteSurface\s*\(|root\s*[=:]|\$[a-zA-Z0-9_/]+\s*[=:]|\b(Column|Row|Card|Text|Button|Tabs|Image|List|Divider|TextField|CheckBox|ChoicePicker|Slider|Modal)\s*\()",
                re.IGNORECASE,
            )
            return bool(express_pattern.search(text))

        # Fallback 1: Extract from markdown code blocks
        code_block_pattern = re.compile(
            r"```(?:a2ui|express|python|json)?\s*\n(.*?)\n```", re.DOTALL | re.IGNORECASE
        )
        matches = list(code_block_pattern.finditer(content))
        for m in matches:
            block = m.group(1).strip()
            if looks_like_express(block):
                result_parts = []
                pre_text = content[:m.start()].strip()
                if pre_text:
                    result_parts.append(ResponsePart(text=pre_text, a2ui_raw=None))
                result_parts.append(ResponsePart(text=None, a2ui_raw=block, is_final=True))
                post_text = content[m.end():].strip()
                if post_text:
                    result_parts.append(ResponsePart(text=post_text, a2ui_raw=None))
                return result_parts

        # Fallback 2: Any code block
        any_code_pattern = re.compile(r"```[a-zA-Z-]*\s*\n(.*?)\n```", re.DOTALL)
        for m in any_code_pattern.finditer(content):
            block = m.group(1).strip()
            if looks_like_express(block):
                result_parts = []
                pre_text = content[:m.start()].strip()
                if pre_text:
                    result_parts.append(ResponsePart(text=pre_text, a2ui_raw=None))
                result_parts.append(ResponsePart(text=None, a2ui_raw=block, is_final=True))
                post_text = content[m.end():].strip()
                if post_text:
                    result_parts.append(ResponsePart(text=post_text, a2ui_raw=None))
                return result_parts

        # Fallback 3: Raw response text without markdown backticks
        if looks_like_express(content):
            m = re.search(
                r"(surface\s*\(|root\s*[=:]|\$[a-zA-Z0-9_/]+\s*[=:]|\b(Column|Row|Card|Text|Button|Tabs|Image|List|Divider|TextField|CheckBox|ChoicePicker|Slider|Modal)\s*\()",
                content,
                re.IGNORECASE,
            )
            if m and m.start() > 0:
                pre_text = content[:m.start()].strip()
                raw_code = content[m.start():].strip()
                result_parts = []
                if pre_text:
                    result_parts.append(ResponsePart(text=pre_text, a2ui_raw=None))
                result_parts.append(ResponsePart(text=None, a2ui_raw=raw_code, is_final=True))
                return result_parts
            return [ResponsePart(text=None, a2ui_raw=content.strip(), is_final=True)]

        return parts

    def compile(
        self, format_content: str, *, is_final: bool = True
    ) -> List[dict[str, Any]]:
        """Compiles raw Express DSL to structured A2UI messages."""
        import json
        from a2ui.parser.errors import A2uiCompilationError

        trimmed = format_content.strip()
        if (trimmed.startswith("[") and trimmed.endswith("]")) or (
            trimmed.startswith("{") and trimmed.endswith("}")
        ):
            try:
                parsed_json = json.loads(trimmed)
                if isinstance(parsed_json, dict):
                    parsed_json = [parsed_json]
                if isinstance(parsed_json, list) and any(
                    isinstance(item, dict)
                    and any(
                        k in item
                        for k in (
                            "createSurface",
                            "updateComponents",
                            "updateDataModel",
                            "deleteSurface",
                        )
                    )
                    for item in parsed_json
                ):
                    return parsed_json
            except json.JSONDecodeError:
                pass

        compiler = ExpressCompiler(self.catalog, version=self.version)
        try:
            return compiler.compile(
                format_content, surface_id=self.surface_id, is_final=is_final
            )
        except (SyntaxError, ValueError) as e:
            orig_err = e
            if isinstance(e, ValueError) and isinstance(e.__cause__, SyntaxError):
                orig_err = e.__cause__
            line = getattr(orig_err, "lineno", None)
            column = getattr(orig_err, "offset", None)
            help_msg = (
                getattr(e, "help_message", None)
                or "Please correct the syntax error in your Express DSL."
            )
            raise A2uiCompilationError(
                message=str(e),
                raw_content=format_content,
                line=line,
                column=column,
                help_message=help_msg,
            ) from e

    def decompile(self, val: Union[dict[str, Any], List[dict[str, Any]]]) -> str:
        """Decompiles a structured A2UI payload into this format's raw notation."""
        return _ExpressDecompiler(self.catalog).decompile(val)

    def wrap_decompiled_blocks(self, blocks: List[str]) -> str:
        """Wraps multiple decompiled blocks with the format's enclosing tags/markers."""
        return _ExpressDecompiler(self.catalog).wrap_decompiled_blocks(blocks)
