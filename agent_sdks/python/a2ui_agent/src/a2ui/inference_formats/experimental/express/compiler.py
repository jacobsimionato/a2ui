# Copyright 2024 Google LLC
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

"""Compilation engine for A2UI Express.

Tokenizes, lexes, and parses A2UI Express plain-text statements into a clean
AST, compiling it directly into standard A2UI v1.0 JSON messages.

The grammar for A2UI Express is defined in Express.g4.
"""

import json
import re
from typing import Any, Optional, Union
from antlr4 import InputStream, CommonTokenStream
from a2ui.core.catalog import Catalog
from a2ui.schema.catalog import A2uiCatalog
from .generated.express_lexer import ExpressLexer
from .generated.express_parser import ExpressParser
from .visitor import ExpressAstVisitor, ExpressErrorListener
from .schema_helper import CatalogSchemaHelper
from .constants import SurfaceOperation
from .errors import (
    ExpressCompilerError,
    ExpressUnknownPropertyError,
    ExpressDuplicatePropertyError,
    ExpressInvalidParamError,
    ExpressDuplicateParamError,
    ExpressForbiddenDatabindingError,
    ExpressUndefinedRootError,
    ExpressUndefinedChildError,
)


def _set_nested_path(d: dict, path_str: str, val: Any) -> None:
    """Populates a nested dictionary path from a JSON pointer-like string.

    Args:
        d: The target dictionary to mutate.
        path_str: The data path string (e.g. "$/user/name").
        val: The value to set at the specified path.
    """
    if path_str.startswith("$/"):
        clean_path = path_str[2:]
    elif path_str.startswith("$"):
        clean_path = path_str[1:]
    else:
        clean_path = path_str

    if not clean_path:
        return

    keys = clean_path.split("/")
    current = d
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    current[keys[-1]] = val


def _schema_allows_databinding(schema: Any) -> bool:
    """Recursively checks if a property's schema allows a dynamic DataBinding ref.

    Args:
        schema: The JSON schema dict for the target property.

    Returns:
        True if the schema permits dynamic databinding; False otherwise.
    """
    if not isinstance(schema, dict):
        return False
    if "$ref" in schema:
        ref = schema["$ref"]
        if isinstance(ref, str) and ("DataBinding" in ref or "Dynamic" in ref):
            return True
    if "properties" in schema and "path" in schema["properties"]:
        if "componentId" not in schema["properties"]:
            return True
    if "items" in schema:
        if _schema_allows_databinding(schema["items"]):
            return True
    for key in ["allOf", "oneOf", "anyOf"]:
        if key in schema and isinstance(schema[key], list):
            for sub in schema[key]:
                if _schema_allows_databinding(sub):
                    return True
    return False


def _has_databinding(v: Any) -> bool:
    """Recursively checks if a value structure contains a dynamic DataBinding ($path) ref.

    Args:
        v: The value (dict, list, or primitive) to inspect.

    Returns:
        True if a dynamic DataBinding is found; False otherwise.
    """
    if isinstance(v, dict):
        if "call" in v or "event" in v or "functionCall" in v:
            return False
        if "path" in v and "componentId" not in v:
            return True
        return any(_has_databinding(x) for x in v.values())
    if isinstance(v, list):
        return any(_has_databinding(x) for x in v)
    return False


def _schema_expects_option_objects(schema: Any) -> bool:
    """Checks if a property's schema expects a list of objects with label/value properties."""
    if not isinstance(schema, dict):
        return False
    if "items" in schema:
        items_schema = schema["items"]

        def has_label_value(sub: Any) -> bool:
            if not isinstance(sub, dict):
                return False
            if (
                "properties" in sub
                and "label" in sub["properties"]
                and "value" in sub["properties"]
            ):
                return True
            for k in ["allOf", "oneOf", "anyOf"]:
                if k in sub and isinstance(sub[k], list):
                    if any(has_label_value(s) for s in sub[k]):
                        return True
            return False

        return has_label_value(items_schema)
    for key in ["allOf", "oneOf", "anyOf"]:
        if key in schema and isinstance(schema[key], list):
            if any(_schema_expects_option_objects(sub) for sub in schema[key]):
                return True
    return False


def _is_check_expression(val: Any) -> bool:
    """Checks if a parsed AST value represents a validation check expression."""
    if isinstance(val, dict) and "check" in val:
        return True
    if isinstance(val, list) and val:
        return all(_is_check_expression(item) for item in val)
    return False


# ANTLR-generated lexer, parser, and custom visitor are used for compilation.


class _CompileContext:
    """Holds mutable state for a single compiler execution thread."""

    def __init__(self):
        self.extra_components: list[dict] = []
        self.inline_counter: int = 0
        self.active_value_path: Optional[dict] = None


class _SurfaceScope:
    """Holds symbols and data path assignments for a target surface scope."""

    def __init__(self, surface_id: str, catalog_id: Optional[str] = None):
        self.surface_id = surface_id
        self.catalog_id = catalog_id
        self.raw_symbols: dict[str, Any] = {}
        self.data_path_assignments: dict[str, Any] = {}


class ExpressCompiler:
    """Compilation pipeline for A2UI Express.

    Resolves positional parameters dynamically, flattens variable references into
    an adjacency list widget tree, and constructs valid A2UI v1.0 JSON payloads.

    Attributes:
        helper: A CatalogSchemaHelper loaded with the target catalog definition.
    """

    def __init__(
        self,
        catalog: Union[Catalog[Any, Any], A2uiCatalog],
        version: str = "v1.0",
        permissive_root: bool = False,
        coerce_primitives: bool = False,
    ):
        """Initializes the compiler with the specified catalog.

        Args:
            catalog: A Catalog or an A2uiCatalog.
            version: Target A2UI protocol version ("v0.9", "v0.9.1", or "v1.0").
            permissive_root: Whether to auto-promote unassigned components to 'root'.
            coerce_primitives: Whether to coerce primitive property types using catalog schemas.
        """
        self.helper = CatalogSchemaHelper(catalog)
        self.version = version
        self.permissive_root = permissive_root
        self.coerce_primitives = coerce_primitives

    def _get_expected_primitive_type(
        self, schema: Optional[dict[str, Any]]
    ) -> Optional[str]:
        """Resolves expected primitive type (number, integer, boolean, string) from a schema."""
        if not isinstance(schema, dict):
            return None
        t = schema.get("type")
        if t in ("integer", "number", "boolean", "string"):
            return t
        ref = schema.get("$ref")
        if isinstance(ref, str):
            if "DynamicNumber" in ref or "Number" in ref:
                return "number"
            if "DynamicInteger" in ref or "Integer" in ref:
                return "integer"
            if "DynamicBoolean" in ref or "Boolean" in ref:
                return "boolean"
            if "DynamicString" in ref or "String" in ref:
                return "string"
        for k in ("anyOf", "oneOf", "allOf"):
            if k in schema and isinstance(schema[k], list):
                for sub in schema[k]:
                    sub_t = self._get_expected_primitive_type(sub)
                    if sub_t:
                        return sub_t
        return None

    def _coerce_property_value(
        self, comp_name: str, prop_name: str, val: Any
    ) -> Any:
        """Coerces property value (numbers, booleans) based on catalog schema."""
        prop_schema = self.helper.get_property_schema(comp_name, prop_name)
        if isinstance(val, str) and (val.startswith("$/") or val.startswith("$")):
            if self.permissive_root and prop_schema and _schema_allows_databinding(prop_schema):
                clean_path = val[2:] if val.startswith("$/") else val[1:]
                return {"path": "/" + clean_path.lstrip("/")}
            return val
        expected_type = self._get_expected_primitive_type(prop_schema)
        if expected_type in ("number", "integer"):
            if isinstance(val, str):
                try:
                    cleaned = val.strip()
                    if cleaned.endswith("%"):
                        cleaned = cleaned[:-1].strip()
                    if cleaned.startswith("+"):
                        cleaned = cleaned[1:].strip()
                    if expected_type == "integer":
                        return int(float(cleaned))
                    else:
                        if "." in cleaned or "e" in cleaned.lower():
                            return float(cleaned)
                        else:
                            return int(cleaned)
                except (ValueError, TypeError):
                    pass
            elif (
                isinstance(val, float)
                and expected_type == "integer"
                and val.is_integer()
            ):
                return int(val)
        elif expected_type == "boolean":
            if isinstance(val, str):
                cleaned = val.strip().lower()
                if cleaned in ("true", "1"):
                    return True
                elif cleaned in ("false", "0"):
                    return False
        return val

    def _normalize_colons_in_call_args(self, text: str) -> str:
        """Normalizes syntax in Express DSL for permissive parsing."""
        import json

        # 1. Leading /path = -> $/path =
        text = re.sub(r"(?m)^(\s*)(/[a-zA-Z0-9_./]+)\s*=", r"\1$\2 =", text)

        # 2. Quoted "${/path}" and unquoted ${/path}, ${.name} -> $/path, $name
        text = re.sub(r'["\']\$\{/([a-zA-Z0-9_./]+)\}["\']', r'$/\1', text)
        text = re.sub(r'["\']\$\{([a-zA-Z0-9_./]+)\}["\']', r'$\1', text)
        text = re.sub(r"\$\{/([a-zA-Z0-9_./]+)\}", r"$/\1", text)
        text = re.sub(r"\$\{([a-zA-Z0-9_./]+)\}", r"$\1", text)
        text = re.sub(r"\$\{\.([a-zA-Z0-9_]+)\}", r"$\1", text)
        text = re.sub(r"\$\.([a-zA-Z0-9_]+)", r"$\1", text)

        # 3. Strip JSX expression wrappers: { `...` } -> `...`
        text = re.sub(r"\{\s*(`[^`]*`|\"[^\"]*\")\s*\}", r"\1", text)

        # 4. Strip pseudo message wrappers
        text = re.sub(r"(?m)^\s*createSurface\([^)]*\)\s*$", "", text)
        text = re.sub(r"updateComponents\s*\(\s*(root\s*=)", r"\1", text)

        # 4. Handle root concatenation (root = root + Component or root += Component)
        if re.search(r"(?m)^\s*root\s*(?:=\s*root\s*\+|\+=)\s*", text):
            child_counter = 0
            child_vars = []

            def _repl_concat(m: re.Match) -> str:
                nonlocal child_counter
                child_counter += 1
                v = f"_concat_child_{child_counter}"
                child_vars.append(v)
                return f"{v} = "

            text = re.sub(r"(?m)^\s*root\s*(?:=\s*root\s*\+|\+=)\s*", _repl_concat, text)
            if child_vars:
                text = re.sub(r"(?m)^\s*root\s*=\s*Surface\([^)]*\)\s*$", "", text)
                text = text.rstrip() + f"\nroot = Column([{','.join(child_vars)}])\n"

        # 5. Bracketed kwargs: Component([ key = val ]) -> Component(key = val)
        text = re.sub(
            r"\(\[\s*([A-Za-z_][A-Za-z0-9_]*\s*[:=][^\]]*)\]\)",
            r"(\1)",
            text,
            flags=re.DOTALL,
        )

        if self.permissive_root:
            # 6. Dotted component or subcomponent calls: e.g. Tabs.Tab(...) -> Tab(...)
            text = re.sub(r"\b[A-Za-z_][A-Za-z0-9_]*\.([A-Za-z_][A-Za-z0-9_]*)\(", r"\1(", text)


        out = []
        i = 0
        n = len(text)
        stack = []
        in_string = False
        string_char = ""
        triple_string = False

        while i < n:
            if not in_string and (i + 2 < n) and (text[i : i + 3] in ('"""', "'''")):
                in_string = True
                string_char = text[i : i + 3]
                triple_string = True
                out.append('"""')
                i += 3
                continue
            elif in_string and triple_string:
                if text[i : i + 3] == string_char:
                    in_string = False
                    triple_string = False
                    out.append('"""')
                    i += 3
                    continue
                else:
                    out.append(text[i])
                    i += 1
                    continue
            elif not in_string and text[i] == "`":  # backtick template string
                j = i + 1
                content = []
                while j < n and text[j] != "`":
                    if text[j] == "\\" and j + 1 < n:
                        content.append(text[j : j + 2])
                        j += 2
                    else:
                        content.append(text[j])
                        j += 1
                if j < n:
                    j += 1
                out.append(json.dumps("".join(content)))
                i = j
                continue
            elif not in_string and text[i] == "'":  # single-quoted string
                j = i + 1
                content = []
                while j < n and text[j] != "'":
                    if text[j] == "\\" and j + 1 < n:
                        content.append(text[j : j + 2])
                        j += 2
                    else:
                        content.append(text[j])
                        j += 1
                if j < n:
                    j += 1
                out.append(json.dumps("".join(content)))
                i = j
                continue
            elif not in_string and text[i] == '"':
                in_string = True
                string_char = '"'
                triple_string = False
                out.append(text[i])
                i += 1
                continue
            elif in_string and not triple_string:
                if text[i] == "\\" and i + 1 < n:
                    out.append(text[i : i + 2])
                    i += 2
                    continue
                elif text[i] == string_char:
                    in_string = False
                out.append(text[i])
                i += 1
                continue

            if text[i] == "#" or (text[i] == "/" and i + 1 < n and text[i + 1] == "/"):
                while i < n and text[i] != "\n":
                    out.append(text[i])
                    i += 1
                continue

            matching_open = {")": "(", "]": "[", "}": "{"}
            closing_map = {"(": ")", "[": "]", "{": "}"}
            ch = text[i]
            if ch in ("(", "{", "["):
                stack.append(ch)
                out.append(ch)
            elif ch in (")", "]", "}"):
                target_open = matching_open[ch]
                if target_open in stack:
                    while stack and stack[-1] != target_open:
                        unclosed = stack.pop()
                        out.append(closing_map[unclosed])
                    if stack and stack[-1] == target_open:
                        stack.pop()
                    out.append(ch)
                else:
                    # Unmatched closing delimiter; ignore in permissive mode
                    pass
            elif ch == ":" and stack and stack[-1] == "(":
                out.append("=")
            elif ch == "=" and stack and stack[-1] == "{":
                out.append(":")
            else:
                out.append(ch)
            i += 1
        while stack:
            open_delim = stack.pop()
            out.append(closing_map[open_delim])
        return "".join(out)

    def compile(
        self,
        dsl_text: str,
        surface_id: str = "default_surface",
        catalog_id: str = "",
        is_final: bool = True,
        version: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Compiles plain A2UI Express DSL into standard A2UI wire JSON.

        Args:
            dsl_text: The source A2UI Express DSL text block.
            surface_id: The unique identifier for the compiled user interface surface.
            catalog_id: The URI/identifier of the schema catalog to reference.
            is_final: Whether this is the final compilation pass.
            version: Target version override ("v0.9", "v0.9.1", or "v1.0").

        Returns:
            A list of standard A2UI wire JSON message dicts.

        Raises:
            ValueError: If the root component variable is missing or unsupported features are used.
            ExpressCompilerError: If a component property, parameter, databinding, or reference is invalid.
        """
        target_version = version or self.version
        ctx = _CompileContext()
        # Detect if sentinel tags exist in the input
        has_sentinels = "<a2ui>" in dsl_text
        lines = []
        inside_a2ui = not has_sentinels
        for line in dsl_text.splitlines():
            trimmed = line.strip()
            if "<a2ui>" in trimmed:
                inside_a2ui = True
                line = line.replace("<a2ui>", "")
                trimmed = line.strip()
            if "</a2ui>" in trimmed:
                inside_a2ui = False
                line = line.split("</a2ui>")[0]
                if line.strip():
                    lines.append(line)
                continue
            if inside_a2ui:
                lines.append(line)

        dsl_body = "\n".join(lines)

        trimmed_body = dsl_body.strip()
        if trimmed_body.startswith("```"):
            fence_lines = trimmed_body.splitlines()
            if fence_lines and fence_lines[0].strip().startswith("```"):
                fence_lines = fence_lines[1:]
            if fence_lines and fence_lines[-1].strip() == "```":
                fence_lines = fence_lines[:-1]
            dsl_body = "\n".join(fence_lines)

        if self.permissive_root:
            dsl_body = self._normalize_colons_in_call_args(dsl_body)

        # Use ANTLR to parse and construct the AST
        input_stream = InputStream(dsl_body)
        lexer = ExpressLexer(input_stream)
        error_listener = ExpressErrorListener()
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)

        token_stream = CommonTokenStream(lexer)
        parser = ExpressParser(token_stream)
        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)

        try:
            tree = parser.program()
            if is_final and error_listener.errors:
                line, col, msg, is_lexer = error_listener.errors[0]
                err = SyntaxError(f"Syntax error at line {line}:{col}: {msg}")
                err.lineno = line
                err.offset = col
                err._is_lexer = is_lexer
                raise err

            visitor = ExpressAstVisitor(
                first_error_line=error_listener.errors[0][0]
                if error_listener.errors
                else None
            )
            statements = visitor.visit(tree)
        except Exception as e:
            if not is_final:
                statements = []
            else:
                if isinstance(e, SyntaxError) and getattr(e, "_is_lexer", False):
                    raise e
                raise ValueError(f"Failed to parse expression: {e}") from e

        scopes: list[_SurfaceScope] = []
        current_scope: Optional[_SurfaceScope] = None
        target_delete_surface_id = None
        standalone_function_calls = []

        for stmt in statements:
            stmt_type, *stmt_args = stmt
            if stmt_type == "EXPR":
                parsed_val = stmt_args[0]
                if isinstance(parsed_val, dict) and parsed_val.get("call") == "surface":
                    args = parsed_val.get("args", [])
                    kwargs = parsed_val.get("kwargs", {})
                    target_surf = (
                        kwargs.get("surfaceId")
                        if isinstance(kwargs, dict)
                        and isinstance(kwargs.get("surfaceId"), str)
                        else (
                            args[0]
                            if isinstance(args, list)
                            and args
                            and isinstance(args[0], str)
                            else surface_id
                        )
                    )
                    target_cat = (
                        kwargs.get("catalogId")
                        if isinstance(kwargs, dict)
                        and isinstance(kwargs.get("catalogId"), str)
                        else (
                            args[1]
                            if isinstance(args, list)
                            and len(args) > 1
                            and isinstance(args[1], str)
                            else catalog_id
                        )
                    )

                    current_scope = _SurfaceScope(
                        surface_id=target_surf, catalog_id=target_cat
                    )
                    scopes.append(current_scope)
                elif (
                    isinstance(parsed_val, dict)
                    and parsed_val.get("call") == "deleteSurface"
                ):
                    args = parsed_val.get("args", [])
                    kwargs = parsed_val.get("kwargs", {})
                    if isinstance(args, list) and args and isinstance(args[0], str):
                        target_delete_surface_id = args[0]
                    elif isinstance(kwargs, dict) and isinstance(
                        kwargs.get("surfaceId"), str
                    ):
                        target_delete_surface_id = kwargs["surfaceId"]
                elif isinstance(parsed_val, dict) and "call" in parsed_val:
                    call_name = parsed_val["call"]
                    matched_comp = None
                    if call_name in self.helper.components:
                        matched_comp = call_name
                    elif self.permissive_root:
                        for c in self.helper.components:
                            if c.lower() == call_name.lower():
                                matched_comp = c
                                break

                    if self.permissive_root and matched_comp:
                        parsed_val["call"] = matched_comp
                        if current_scope is None:
                            current_scope = _SurfaceScope(
                                surface_id=surface_id, catalog_id=catalog_id
                            )
                            scopes.append(current_scope)
                        if "root" not in current_scope.raw_symbols:
                            current_scope.raw_symbols["root"] = parsed_val
                        else:
                            current_scope.raw_symbols[
                                f"comp_{len(current_scope.raw_symbols)}"
                            ] = parsed_val
                    else:
                        standalone_function_calls.append((parsed_val, current_scope))
            elif stmt_type == "ASSIGN":
                var_name, parsed_val = stmt_args
                if current_scope is None:
                    current_scope = _SurfaceScope(
                        surface_id=surface_id, catalog_id=catalog_id
                    )
                    scopes.append(current_scope)
                if var_name.startswith("$"):
                    current_scope.data_path_assignments[var_name] = parsed_val
                else:
                    current_scope.raw_symbols[var_name] = parsed_val

        if target_delete_surface_id is not None:
            return [{
                "version": target_version,
                SurfaceOperation.DELETE: {"surfaceId": target_delete_surface_id},
            }]

        if standalone_function_calls:
            if target_version in ("v0.9", "v0.9.1"):
                raise ValueError(
                    "Standalone function calls are not supported in A2UI"
                    f" {target_version}"
                )
            first_call, call_scope = standalone_function_calls[0]
            ctx.inline_counter += 1
            raw_syms = call_scope.raw_symbols if call_scope else {}
            compiled_val = self._compile_value(
                first_call, raw_syms, ctx, is_action=False
            )

            return [{
                "version": target_version,
                "functionCallId": f"call_{ctx.inline_counter}",
                SurfaceOperation.CALL_FUNC: {
                    "call": compiled_val.get("call"),
                    "args": compiled_val.get("args", {}),
                },
            }]

        if not scopes:
            raise ExpressUndefinedRootError("root")

        result_messages = []

        for scope in scopes:
            scope_surf_id = scope.surface_id
            scope_cat_id = (
                scope.catalog_id
                or catalog_id
                or self.helper.catalog.get("catalogId", "https://a2ui.org/catalog.json")
            )

            # Compile data model paths
            data_model = {}
            for path_name, ast_val in scope.data_path_assignments.items():
                compiled_val = self._compile_value(ast_val, scope.raw_symbols, ctx)
                _set_nested_path(data_model, path_name, compiled_val)

            if "root" not in scope.raw_symbols:
                if self.permissive_root and len(scope.raw_symbols) == 1:
                    single_key = next(iter(scope.raw_symbols))
                    scope.raw_symbols["root"] = scope.raw_symbols.pop(single_key)
                elif scope.data_path_assignments:
                    result_messages.append({
                        "version": target_version,
                        SurfaceOperation.UPDATE_DATA: {
                            "surfaceId": scope_surf_id,
                            "path": "/",
                            "value": data_model,
                        },
                    })
                    continue
                else:
                    raise ExpressUndefinedRootError("root")

            compiled_components = []
            for var_name, ast in scope.raw_symbols.items():
                comp_dict = self._compile_ast_node(
                    var_name, ast, scope.raw_symbols, ctx
                )
                if comp_dict:
                    compiled_components.append(comp_dict)

            compiled_components.extend(ctx.extra_components)
            ctx.extra_components = []

            if target_version in ("v0.9", "v0.9.1"):
                result_messages.extend([
                    {
                        "version": target_version,
                        SurfaceOperation.CREATE: {
                            "surfaceId": scope_surf_id,
                            "catalogId": scope_cat_id,
                        },
                    },
                    {
                        "version": target_version,
                        SurfaceOperation.UPDATE_COMPONENTS: {
                            "surfaceId": scope_surf_id,
                            "components": compiled_components,
                        },
                    },
                ])
                if data_model:
                    result_messages.append({
                        "version": target_version,
                        SurfaceOperation.UPDATE_DATA: {
                            "surfaceId": scope_surf_id,
                            "path": "/",
                            "value": data_model,
                        },
                    })
            else:
                envelope = {
                    "version": target_version,
                    SurfaceOperation.CREATE: {
                        "surfaceId": scope_surf_id,
                        "catalogId": scope_cat_id,
                        "components": compiled_components,
                    },
                }
                if data_model:
                    envelope[SurfaceOperation.CREATE]["dataModel"] = data_model
                result_messages.append(envelope)

        return result_messages

    def _compile_ast_node(
        self, var_name: str, ast: Any, raw_symbols: dict, ctx: _CompileContext
    ) -> Optional[dict]:
        """Compiles a single variable's AST node into standard component format.

        Args:
            var_name: The variable identifier (which becomes the component ID).
            ast: The parsed expression AST node.
            raw_symbols: A dictionary containing all other parsed variables.
            ctx: The active compiler execution context.

        Returns:
            The compiled component JSON dictionary, or None if it is not a component.
        """
        if not isinstance(ast, dict) or "call" not in ast:
            return None

        comp_name = ast["call"]
        args = ast.get("args", [])
        kwargs = ast.get("kwargs", {})

        if comp_name not in self.helper.components and self.permissive_root:
            if comp_name.lower() in ("component", "yourcomponent") and args and isinstance(args[0], str):
                target_name = args[0]
                for c in self.helper.components:
                    if c.lower() == target_name.lower():
                        comp_name = c
                        ast["call"] = c
                        args = args[1:]
                        ast["args"] = args
                        break
            elif comp_name.lower() in (
                "container",
                "yourcontainer",
                "topcomponent",
                "box",
                "group",
                "wrapper",
                "surface",
                "view",
                "section",
                "mainlayout",
                "yourcolumn",
            ):
                if "Column" in self.helper.components:
                    comp_name = "Column"
                    ast["call"] = "Column"
                elif "Row" in self.helper.components:
                    comp_name = "Row"
                    ast["call"] = "Row"
            elif comp_name.lower() == "numberfield":
                comp_name = "TextField"
                ast["call"] = "TextField"
                if "variant" not in kwargs:
                    kwargs["variant"] = "number"

            for c in self.helper.components:
                if c.lower() == comp_name.lower():
                    comp_name = c
                    ast["call"] = c
                    break

        if self.permissive_root and comp_name in ("Column", "Row") and len(args) > 1:
            args = [args]
            ast["args"] = args

        if self.permissive_root and comp_name == "List":
            data_arg = kwargs.pop("data", kwargs.pop("items", kwargs.pop("elements", None)))
            template_arg = kwargs.pop("template", kwargs.pop("item", None))
            if data_arg and template_arg and "children" not in kwargs:
                kwargs["children"] = {"call": "_template", "args": [data_arg, template_arg]}
            elif data_arg and "children" not in kwargs:
                kwargs["children"] = data_arg

        if self.permissive_root and comp_name == "ChoicePicker":
            if "value" not in kwargs and "values" not in kwargs:
                kwargs["value"] = []
            if "options" not in kwargs:
                kwargs["options"] = []

        if self.permissive_root and comp_name == "Card":
            if len(args) > 1 and "child" not in kwargs:
                args = [{"call": "Column", "args": [args], "kwargs": {}}]
                ast["args"] = args
            if "child" not in kwargs and "children" not in kwargs:
                if len(kwargs) == 1:
                    kw_k, kw_v = next(iter(kwargs.items()))
                    if kw_k.lower() in ("title", "header", "heading") and isinstance(kw_v, str):
                        kwargs = {"child": {"call": "Text", "args": [], "kwargs": {"text": kw_v, "variant": "h2"}}}
                    elif kw_k.lower() == "children":
                        if isinstance(kw_v, list):
                            kwargs = {"child": {"call": "Column", "args": [kw_v], "kwargs": {}}}
                        else:
                            kwargs = {"child": kw_v}
                    else:
                        kwargs = {"child": kw_v}
                    ast["kwargs"] = kwargs
                elif len(kwargs) > 1:
                    card_children = []
                    for k, v in kwargs.items():
                        if k.lower() in ("title", "header", "heading") and isinstance(v, str):
                            card_children.append({"call": "Text", "args": [], "kwargs": {"text": v, "variant": "h2"}})
                        elif k.lower() == "children" and isinstance(v, list):
                            card_children.extend(v)
                        else:
                            card_children.append(v)
                    kwargs = {"child": {"call": "Column", "args": [card_children], "kwargs": {}}}
                    ast["kwargs"] = kwargs
            elif len(kwargs) > 1:
                card_children = []
                for k, v in kwargs.items():
                    if k.lower() in ("title", "header", "heading") and isinstance(v, str):
                        card_children.append({"call": "Text", "args": [], "kwargs": {"text": v, "variant": "h2"}})
                    elif k.lower() == "child":
                        card_children.append(v)
                    elif k.lower() == "children" and isinstance(v, list):
                        card_children.extend(v)
                    else:
                        card_children.append(v)
                kwargs = {"child": {"call": "Column", "args": [card_children], "kwargs": {}}}
                ast["kwargs"] = kwargs

        if self.permissive_root and comp_name == "Modal":
            if "content" not in kwargs and "child" not in kwargs and "children" not in kwargs:
                if len(args) > 0:
                    kwargs["content"] = args[0]
            if "trigger" not in kwargs:
                kwargs["trigger"] = {
                    "call": "Button",
                    "args": [],
                    "kwargs": {
                        "child": {"call": "Text", "args": [], "kwargs": {"text": "Open"}},
                        "action": {"call": "Event", "args": ["openModal"], "kwargs": {}},
                    },
                }


        if comp_name not in self.helper.components:
            # Not a component, could be a standalone action/helper; skip writing as component
            return None

        properties = self.helper.get_component_properties(comp_name)
        comp_dict = {"id": var_name, "component": comp_name}

        # Sibling path tracking for check rules
        sibling_value_path = None

        non_check_properties = [p for p in properties if p != "checks"]
        raw_checks = []

        # Collect (prop_name, arg_val) pairs from positional and keyword args
        prop_arg_pairs = []
        prop_idx = 0
        for arg in args:
            if _is_check_expression(arg):
                if isinstance(arg, list):
                    raw_checks.extend(arg)
                else:
                    raw_checks.append(arg)
                continue

            if prop_idx < len(non_check_properties):
                prop_arg_pairs.append((non_check_properties[prop_idx], arg))
                prop_idx += 1

        for k, v in kwargs.items():
            if _is_check_expression(v):
                if isinstance(v, list):
                    raw_checks.extend(v)
                else:
                    raw_checks.append(v)
                continue
            prop_arg_pairs.append((k, v))

        seen_properties = set()
        for prop_name, arg in prop_arg_pairs:
            if prop_name not in properties and (
                self.coerce_primitives or self.permissive_root
            ):
                for p in properties:
                    if p.lower() == prop_name.lower():
                        prop_name = p
                        break
                if prop_name not in properties:
                    aliases = {
                        "src": "url",
                        "values": "value",
                        "items": "children" if "children" in properties else None,
                        "title": (
                            "label"
                            if "label" in properties
                            else (
                                "text"
                                if "text" in properties
                                else ("child" if "child" in properties else None)
                            )
                        ),
                        "label": (
                            "text"
                            if "text" in properties
                            else ("child" if "child" in properties else None)
                        ),
                        "text": (
                            "label"
                            if "label" in properties
                            else ("child" if "child" in properties else None)
                        ),
                        "name": (
                            "text"
                            if "text" in properties
                            else ("label" if "label" in properties else None)
                        ),
                        "children": (
                            "content"
                            if "content" in properties
                            else ("child" if "child" in properties else None)
                        ),
                        "child": (
                            "content"
                            if "content" in properties
                            else ("children" if "children" in properties else None)
                        ),
                        "content": "child" if "child" in properties else None,
                    }
                    alias_target = aliases.get(prop_name.lower())
                    if alias_target and alias_target in properties and alias_target not in seen_properties:
                        prop_name = alias_target

                if prop_name not in properties and self.permissive_root:
                    if (
                        prop_name.lower() in ("placeholder", "hint", "help")
                        and "label" in properties
                        and "label" not in seen_properties
                    ):
                        prop_name = "label"
                    elif prop_name.lower() == "id":
                        if isinstance(arg, str) and comp_dict.get("id", "").startswith("_inline_"):
                            comp_dict["id"] = arg
                        continue
                    elif prop_name.lower() in (
                        "title",
                        "name",
                        "key",
                        "placeholder",
                        "hint",
                        "help",
                        "style",
                        "spacing",
                        "padding",
                        "margin",
                        "color",
                        "width",
                        "height",
                        "elevation",
                        "direction",
                        "numeric",
                        "required",
                        "min",
                        "max",
                        "step",
                        "disabled",
                        "group",
                        "default",
                        "visible",
                    ):
                        continue

            if prop_name not in properties:
                raise ExpressUnknownPropertyError(comp_name, prop_name, properties)
            if prop_name in seen_properties:
                raise ExpressDuplicatePropertyError(comp_name, prop_name)
            seen_properties.add(prop_name)
            if arg == {"skipped": True}:
                comp_dict[prop_name] = None
                continue

            mapped_val = self._compile_value(
                arg,
                raw_symbols,
                ctx,
                is_action=(prop_name in ["action", "submitAction"]),
            )
            mapped_val = self._coerce_property_value(comp_name, prop_name, mapped_val)
            if self.permissive_root and prop_name in ("child", "content"):
                if isinstance(mapped_val, list):
                    if len(mapped_val) == 1:
                        mapped_val = mapped_val[0]
                    elif len(mapped_val) > 1:
                        ctx.inline_counter += 1
                        col_id = f"_inline_{ctx.inline_counter}"
                        ctx.extra_components.append({
                            "id": col_id,
                            "component": "Column",
                            "children": mapped_val,
                        })
                        mapped_val = col_id
                if (
                    isinstance(mapped_val, str)
                    and not mapped_val.startswith("_inline_")
                    and mapped_val not in raw_symbols
                ):
                    ctx.inline_counter += 1
                    inline_id = f"_inline_{ctx.inline_counter}"
                    ctx.extra_components.append({
                        "id": inline_id,
                        "component": "Text",
                        "text": mapped_val,
                    })
                    mapped_val = inline_id
            if (
                self.permissive_root
                and prop_name == "children"
                and not isinstance(mapped_val, list)
                and not (
                    isinstance(mapped_val, dict)
                    and "componentId" in mapped_val
                    and "path" in mapped_val
                )
            ):
                mapped_val = [mapped_val]
            prop_schema = self.helper.get_property_schema(comp_name, prop_name)
            if prop_schema and not _schema_allows_databinding(prop_schema):
                if _has_databinding(mapped_val):
                    raise ExpressForbiddenDatabindingError(comp_name, prop_name)
                if isinstance(mapped_val, list) and _schema_expects_option_objects(
                    prop_schema
                ):
                    mapped_val = [
                        {"label": opt, "value": opt} if isinstance(opt, str) else opt
                        for opt in mapped_val
                    ]
            enum_vals = self.helper.get_property_enum(comp_name, prop_name)
            if enum_vals and isinstance(mapped_val, str):
                matched_enum = None
                for ev in enum_vals:
                    if ev == mapped_val or (
                        self.coerce_primitives and ev.lower() == mapped_val.lower()
                    ):
                        matched_enum = ev
                        break
                if matched_enum is not None:
                    mapped_val = matched_enum
                else:
                    raise ValueError(
                        f"Value '{mapped_val}' is not a valid enum choice for"
                        f" property '{prop_name}' of component '{comp_name}'."
                        f" Allowed values are: {enum_vals}"
                    )
            comp_dict[prop_name] = mapped_val

            if (
                prop_name == "value"
                and isinstance(mapped_val, dict)
                and "path" in mapped_val
            ):
                sibling_value_path = mapped_val

        # Set active path for nested check compile resolution
        ctx.active_value_path = sibling_value_path

        # Second pass: compile checks with implicit path injection
        if raw_checks:
            compiled_checks = []
            for rc in raw_checks:
                if isinstance(rc, dict) and "check" in rc:
                    check_name = rc["check"]
                    check_args = rc["args"]
                    compiled_args = {}

                    check_props = self.helper.get_function_properties(check_name)
                    message_val = f"{check_name.capitalize()} check failed"

                    explicit_args = list(check_args)
                    is_value_injected = False

                    # Handle implicit target 'value' injection
                    if check_props and check_props[0] == "value":
                        if (
                            explicit_args
                            and isinstance(explicit_args[0], dict)
                            and "path" in explicit_args[0]
                        ):
                            pass
                        else:
                            if sibling_value_path:
                                compiled_args["value"] = sibling_value_path
                                is_value_injected = True

                    start_prop_idx = 1 if is_value_injected else 0

                    for c_idx, c_arg in enumerate(explicit_args):
                        prop_target_idx = c_idx + start_prop_idx
                        if prop_target_idx < len(check_props):
                            prop_name = check_props[prop_target_idx]
                            prop_schema = self.helper.get_function_property_schema(
                                check_name, prop_name
                            )
                            is_message = False
                            if isinstance(c_arg, str) and prop_schema:
                                expected_type = prop_schema.get("type")
                                if expected_type in ["integer", "number", "boolean"]:
                                    is_message = True

                            if is_message:
                                message_val = c_arg
                                break

                            if isinstance(c_arg, dict) and c_arg.get("skipped"):
                                compiled_args[prop_name] = None
                                continue
                            compiled_args[prop_name] = self._compile_value(
                                c_arg, raw_symbols, ctx
                            )
                        else:
                            if isinstance(c_arg, str):
                                message_val = c_arg

                    compiled_checks.append({
                        "condition": {"call": check_name, "args": compiled_args},
                        "message": message_val,
                    })
            if compiled_checks:
                comp_dict["checks"] = compiled_checks

        if self.permissive_root:
            if comp_name == "Button":
                if "action" not in comp_dict:
                    comp_dict["action"] = {"event": {"name": "click"}}
                if "child" not in comp_dict:
                    ctx.inline_counter += 1
                    btn_text_id = f"_inline_{ctx.inline_counter}"
                    ctx.extra_components.append({
                        "id": btn_text_id,
                        "component": "Text",
                        "text": "Submit",
                    })
                    comp_dict["child"] = btn_text_id
            elif comp_name == "ChoicePicker":
                if "value" not in comp_dict:
                    comp_dict["value"] = []

        ctx.active_value_path = None
        return {k: v for k, v in comp_dict.items() if v is not None}

    def _compile_value(
        self, val: Any, raw_symbols: dict, ctx: _CompileContext, is_action: bool = False
    ) -> Any:
        """Compiles an individual AST node value into valid A2UI equivalents.

        Args:
            val: The parsed AST node value.
            raw_symbols: The parsed global variable symbol table.
            ctx: The active compiler execution context.
            is_action: Whether this value lies inside a component Action field.

        Returns:
            The semantically correct A2UI JSON structure.
        """
        if isinstance(val, dict):
            if "path" in val:
                return val
            if "variable" in val:
                ref_name = val["variable"]
                if ref_name in raw_symbols:
                    symbol_val = raw_symbols[ref_name]
                    if (
                        isinstance(symbol_val, dict)
                        and symbol_val.get("call") in self.helper.components
                    ):
                        return ref_name
                    return self._compile_value(symbol_val, raw_symbols, ctx, is_action)
                return ref_name
            if "check" in val:
                check_name = val["check"]
                check_args = val["args"]

                compiled_args = {}
                check_props = self.helper.get_function_properties(check_name)

                explicit_args = list(check_args)
                is_value_injected = False

                if check_props:
                    if check_props[0] == "value":
                        if not (
                            explicit_args
                            and isinstance(explicit_args[0], dict)
                            and "path" in explicit_args[0]
                        ):
                            if ctx.active_value_path:
                                compiled_args["value"] = ctx.active_value_path
                                is_value_injected = True

                    start_prop_idx = 1 if is_value_injected else 0
                    for c_idx, c_arg in enumerate(explicit_args):
                        prop_target_idx = c_idx + start_prop_idx
                        if prop_target_idx < len(check_props):
                            prop_name = check_props[prop_target_idx]
                            prop_schema = self.helper.get_function_property_schema(
                                check_name, prop_name
                            )
                            is_message = False
                            if isinstance(c_arg, str) and prop_schema:
                                expected_type = prop_schema.get("type")
                                if expected_type in ["integer", "number", "boolean"]:
                                    is_message = True

                            if is_message:
                                break

                            if isinstance(c_arg, dict) and c_arg.get("skipped"):
                                continue
                            compiled_args[prop_name] = self._compile_value(
                                c_arg, raw_symbols, ctx, is_action
                            )

                return {"call": check_name, "args": compiled_args}
            if "call" in val:
                # Nested function call (e.g. formatString or actions)
                fn_name = val["call"]
                fn_args = val["args"]

                # Is it an inline component constructor?
                is_comp = fn_name in self.helper.components
                if not is_comp and self.permissive_root:
                    if (
                        fn_name.lower() in ("component", "yourcomponent")
                        and fn_args
                        and isinstance(fn_args[0], str)
                    ):
                        target_name = fn_args[0]
                        for c in self.helper.components:
                            if c.lower() == target_name.lower():
                                fn_name = c
                                val["call"] = c
                                fn_args = fn_args[1:]
                                val["args"] = fn_args
                                is_comp = True
                                break
                    elif fn_name.lower() in (
                        "container",
                        "yourcontainer",
                        "topcomponent",
                        "box",
                        "group",
                        "wrapper",
                        "surface",
                        "view",
                        "section",
                        "mainlayout",
                        "yourcolumn",
                    ):
                        if "Column" in self.helper.components:
                            fn_name = "Column"
                            val["call"] = "Column"
                            is_comp = True
                        elif "Row" in self.helper.components:
                            fn_name = "Row"
                            val["call"] = "Row"
                            is_comp = True
                    if not is_comp:
                        if fn_name.lower() == "numberfield":
                            fn_name = "TextField"
                            val["call"] = "TextField"
                            is_comp = True
                        else:
                            for c in self.helper.components:
                                if c.lower() == fn_name.lower():
                                    fn_name = c
                                    val["call"] = c
                                    is_comp = True
                                    break

                if is_comp:
                    ctx.inline_counter += 1
                    inline_id = f"_inline_{ctx.inline_counter}"
                    compiled_inline = self._compile_ast_node(
                        inline_id, val, raw_symbols, ctx
                    )
                    if compiled_inline:
                        ctx.extra_components.append(compiled_inline)
                        return compiled_inline.get("id", inline_id)
                    return inline_id

                # Is it a reserved Template signature?
                if fn_name == "_template":
                    if len(fn_args) < 2:
                        raise ValueError(
                            "_template helper requires exactly 2 arguments: path and"
                            " templateComponent."
                        )
                    path_val = self._compile_value(
                        fn_args[0], raw_symbols, ctx, is_action
                    )
                    if isinstance(path_val, str):
                        path_str = path_val.lstrip("$")
                        if not path_str.startswith("/"):
                            path_str = f"/{path_str}"
                        path_val = {"path": path_str}
                    if not isinstance(path_val, dict) or "path" not in path_val:
                        raise ValueError(
                            "The first argument to _template must be a dynamic data"
                            f" binding path (prefixed by $), got: {fn_args[0]}"
                        )
                    comp_id_val = self._compile_value(
                        fn_args[1], raw_symbols, ctx, is_action
                    )
                    if isinstance(comp_id_val, dict) and "id" in comp_id_val:
                        comp_id_val = comp_id_val["id"]
                    return {"path": path_val["path"], "componentId": comp_id_val}

                if self.permissive_root and fn_name.lower() == "tab":
                    tab_kwargs = val.get("kwargs", {})
                    tab_title = (
                        tab_kwargs.get("title")
                        or (fn_args[0] if len(fn_args) > 0 else "Tab")
                    )
                    tab_child = (
                        tab_kwargs.get("child")
                        or tab_kwargs.get("id")
                        or (fn_args[1] if len(fn_args) > 1 else "")
                    )
                    return {
                        "title": self._compile_value(tab_title, raw_symbols, ctx, is_action),
                        "child": self._compile_value(tab_child, raw_symbols, ctx, is_action),
                    }

                # Is it a reserved Event signature?
                if fn_name == "Event":
                    fn_kwargs = val.get("kwargs", {})
                    event_name_arg = (
                        fn_kwargs.get("name")
                        if "name" in fn_kwargs
                        else (fn_args[0] if len(fn_args) > 0 else "")
                    )
                    context_arg = (
                        fn_kwargs.get("context")
                        if "context" in fn_kwargs
                        else (fn_args[1] if len(fn_args) > 1 else {})
                    )
                    compiled_event_name = (
                        self._compile_value(event_name_arg, raw_symbols, ctx, is_action)
                        if event_name_arg
                        else ""
                    )
                    raw_context = (
                        self._compile_value(context_arg, raw_symbols, ctx, is_action)
                        if context_arg
                        else {}
                    )
                    compiled_context = {}
                    if isinstance(raw_context, dict):
                        compiled_context.update(raw_context)
                    elif isinstance(raw_context, list):
                        for item in raw_context:
                            if isinstance(item, dict):
                                compiled_context.update(item)
                    return {
                        "event": {
                            "name": compiled_event_name,
                            "context": compiled_context,
                        }
                    }

                # Is it a regular catalog function?
                if fn_name in self.helper.functions:
                    fn_props = self.helper.get_function_properties(fn_name)
                    fn_kwargs = val.get("kwargs", {})
                    compiled_args = {}
                    for idx, arg in enumerate(fn_args):
                        if idx < len(fn_props):
                            if isinstance(arg, dict) and arg.get("skipped"):
                                continue
                            val_item = self._compile_value(
                                arg, raw_symbols, ctx, is_action
                            )
                            if val_item is not None:
                                compiled_args[fn_props[idx]] = val_item

                    for k, v in fn_kwargs.items():
                        if k not in fn_props:
                            raise ExpressInvalidParamError(fn_name, k, fn_props)
                        if k in compiled_args:
                            raise ExpressDuplicateParamError(fn_name, k)
                        if v == {"skipped": True}:
                            continue
                        val_item = self._compile_value(v, raw_symbols, ctx, is_action)
                        if val_item is not None:
                            compiled_args[k] = val_item

                    # Wrap in functionCall only if inside an action field
                    if is_action:
                        return {
                            "functionCall": {"call": fn_name, "args": compiled_args}
                        }

                    # Otherwise, compile direct dynamic function call expression
                    res_expr = {"call": fn_name, "args": compiled_args}
                    return res_expr

                # Fallback
                return {
                    "call": fn_name,
                    "args": [
                        self._compile_value(a, raw_symbols, ctx, is_action)
                        for a in fn_args
                    ],
                }

            return {
                k: self._compile_value(v, raw_symbols, ctx, is_action)
                for k, v in val.items()
            }

        if isinstance(val, list):
            # If this is a list of elements, compile each element
            compiled_list = []
            for item in val:
                comp_item = self._compile_value(item, raw_symbols, ctx, is_action)
                compiled_list.append(comp_item)
            return compiled_list

        return val
