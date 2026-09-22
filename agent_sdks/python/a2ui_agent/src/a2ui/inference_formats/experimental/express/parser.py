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

import re
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
        permissive_root: bool = False,
        coerce_primitives: bool = False,
    ):
        """Initializes the Express parser with a catalog schema and target version.

        Args:
            catalog: Catalog or A2uiCatalog schema helper.
            surface_id: Surface identifier for compiled messages.
            version: Target A2UI protocol version ("v0.9", "v0.9.1", or "v1.0").
            permissive_root: Whether to auto-promote unassigned components to 'root'.
            coerce_primitives: Whether to coerce primitive property types using catalog schemas.
        """
        self.catalog = catalog
        self.surface_id = surface_id
        self.version = version
        self.permissive_root = permissive_root
        self.coerce_primitives = coerce_primitives

    def _looks_like_express_dsl(self, text: str) -> bool:
        """Heuristic check whether text represents Express DSL rather than JSON or markdown text."""
        trimmed = text.strip()
        if not trimmed:
            return False
        # If it is raw JSON, do not treat as Express DSL
        if (trimmed.startswith("{") and trimmed.endswith("}")) or (
            trimmed.startswith("[") and trimmed.endswith("]")
        ):
            return False

        # Common Express DSL statement markers
        if re.search(
            r"^\s*(root\s*=|surface\s*\(|deleteSurface\s*\(|\$/)",
            trimmed,
            re.MULTILINE,
        ):
            return True

        # Check if it starts with any component name from the catalog followed by '('
        from a2ui.schema.schema_helper import CatalogSchemaHelper

        helper = CatalogSchemaHelper(self.catalog)
        for comp in helper.components:
            if re.search(rf"^\s*{re.escape(comp)}\s*\(", trimmed, re.MULTILINE):
                return True
        return False

    def has_format_content(self, content: str, *, complete: bool = False) -> bool:
        """Checks whether the given content string contains A2UI Express sentinel tags.

        Args:
            content: The text content to inspect.
            complete: Whether to require both opening and closing sentinel tags.

        Returns:
            True if Express format tags are detected; False otherwise.
        """
        if complete:
            if (
                A2UI_INFERENCE_OPEN_TAG in content
                and A2UI_INFERENCE_CLOSE_TAG in content
            ):
                return True
            if "<a2ui-express" in content.lower() and "</a2ui-express>" in content.lower():
                return True
        else:
            if (
                A2UI_INFERENCE_OPEN_TAG[:-1] in content
                or "<a2ui-express" in content.lower()
            ):
                return True

        if self.permissive_root:
            if "```a2ui" in content.lower() or "```express" in content.lower():
                return True
            for match in re.finditer(r"```(?:\w+)?\s*\n(.*?)\n```", content, re.DOTALL):
                if self._looks_like_express_dsl(match.group(1)):
                    return True
            if self._looks_like_express_dsl(content):
                return True
        return False

    def unwrap(self, content: str) -> List[ResponsePart]:
        """Unwraps/tokenizes the response content into raw Express DSL parts."""
        from a2ui.parser.lexer import BlockLexer

        lexer = BlockLexer(
            open_tag=A2UI_INFERENCE_OPEN_TAG,
            close_tag=A2UI_INFERENCE_CLOSE_TAG,
            string_delimiters={"'", '"'},
            single_line_comments={"#"},
        )
        parts = lexer.tokenize(content)
        if any(p.a2ui_raw is not None for p in parts):
            return parts

        if self.permissive_root:
            alt_lexer = BlockLexer(
                open_tag="<a2ui-express>",
                close_tag="</a2ui-express>",
                string_delimiters={"'", '"'},
                single_line_comments={"#"},
            )
            alt_parts = alt_lexer.tokenize(content)
            if any(p.a2ui_raw is not None for p in alt_parts):
                return alt_parts

            for match in re.finditer(r"```(?:\w+)?\s*\n(.*?)\n```", content, re.DOTALL):
                block = match.group(1).strip()
                if self._looks_like_express_dsl(block):
                    return [ResponsePart(a2ui_raw=block, is_final=True)]

            if self._looks_like_express_dsl(content):
                return [ResponsePart(a2ui_raw=content.strip(), is_final=True)]

        return parts

    def compile(
        self, format_content: str, *, is_final: bool = True
    ) -> List[dict[str, Any]]:
        """Compiles raw Express DSL to structured A2UI messages."""
        from a2ui.parser.errors import A2uiCompilationError

        compiler = ExpressCompiler(
            self.catalog,
            version=self.version,
            permissive_root=self.permissive_root,
            coerce_primitives=self.coerce_primitives,
        )
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
