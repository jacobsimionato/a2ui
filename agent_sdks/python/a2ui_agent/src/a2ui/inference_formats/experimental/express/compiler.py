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
    ):
        """Initializes the compiler with the specified catalog.

        Args:
            catalog: A Catalog or an A2uiCatalog.
            version: Target A2UI protocol version ("v0.9", "v0.9.1", or "v1.0").
        """
        self.helper = CatalogSchemaHelper(catalog)
        self.version = version

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
        top_level_components = []

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
                    if self.helper.is_component(call_name):
                        if current_scope is None:
                            current_scope = _SurfaceScope(
                                surface_id=surface_id, catalog_id=catalog_id
                            )
                            scopes.append(current_scope)
                        top_level_components.append(parsed_val)
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
                    if isinstance(parsed_val, dict) and self.helper.is_component(
                        parsed_val.get("call", "")
                    ):
                        clean_var = var_name.lstrip("$").lstrip("/")
                        current_scope.raw_symbols[clean_var] = parsed_val
                        current_scope.raw_symbols[var_name] = parsed_val
                    else:
                        current_scope.data_path_assignments[var_name] = parsed_val
                else:
                    current_scope.raw_symbols[var_name] = parsed_val

        # Detect implicit root from top-level component statements
        if top_level_components:
            if current_scope is None:
                current_scope = _SurfaceScope(
                    surface_id=surface_id, catalog_id=catalog_id
                )
                scopes.append(current_scope)
            if "root" not in current_scope.raw_symbols:
                if len(top_level_components) == 1:
                    current_scope.raw_symbols["root"] = top_level_components[0]
                else:
                    current_scope.raw_symbols["root"] = {
                        "call": "Column",
                        "args": [top_level_components],
                    }

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
                if scope.data_path_assignments:
                    result_messages.append({
                        "version": target_version,
                        SurfaceOperation.UPDATE_DATA: {
                            "surfaceId": scope_surf_id,
                            "path": "/",
                            "value": data_model,
                        },
                    })
                    continue
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

    def _detect_and_unpack_kv_args(
        self, comp_name: str, var_name: str, args: list[Any], kwargs: dict[str, Any]
    ) -> tuple[Optional[str], list[Any], dict[str, Any]]:
        """Permissively detects and unpacks alternating key-value argument sequences.

        Handles small model patterns like:
        TextField("usernameField", "label", "Username", "value", {"path": ...})
        or Button("signInButton", "label", "Sign In", "event", {...})
        or TextField("usernameField", label="Username", ...)
        """
        extracted_id = None
        new_kwargs = dict(kwargs)

        # 1. Check for explicit id in kwargs
        for id_key in ("id", "componentId", "component_id"):
            if id_key in new_kwargs:
                extracted_id = str(new_kwargs.pop(id_key))
                break

        if not args:
            return extracted_id, args, new_kwargs

        properties = self.helper.get_component_properties(comp_name)
        non_check_props = [p for p in properties if p != "checks"]
        first_prop = non_check_props[0] if non_check_props else None

        is_anon_or_inline = var_name.startswith("_anon_comp_") or var_name.startswith("_inline_")

        # 2. Check if args[0] is an explicit component ID because first_prop is already in kwargs
        if (
            is_anon_or_inline
            and not extracted_id
            and len(args) >= 1
            and isinstance(args[0], str)
            and first_prop
            and any(
                self.helper.get_canonical_property_name(comp_name, k) == first_prop
                for k in new_kwargs
            )
        ):
            extracted_id = str(args[0])
            args = args[1:]

        if not args or len(args) < 2:
            return extracted_id, args, new_kwargs

        def is_prop_cand(val: Any) -> bool:
            if not isinstance(val, str):
                return False
            canon = self.helper.get_canonical_property_name(comp_name, val)
            if canon is not None:
                return True
            return val.lower() in (
                "label", "text", "value", "type", "variant", "placeholder",
                "event", "action", "child", "children", "items", "icon", "url",
                "src", "checked", "weight", "axis", "align", "justify"
            )

        # Case A: arg[0] is ID, followed by key-value pairs (len is odd >= 3)
        if len(args) >= 3 and len(args) % 2 == 1 and isinstance(args[0], str):
            if is_prop_cand(args[1]) and (
                (len(args) == 3 and not is_prop_cand(args[0]))
                or (len(args) >= 5 and is_prop_cand(args[3]))
            ):
                id_val = str(args[0])
                for i in range(1, len(args), 2):
                    new_kwargs[str(args[i])] = args[i + 1]
                return id_val or extracted_id, [], new_kwargs

        # Case B: no ID, alternating key-value pairs (len is even >= 4)
        if len(args) >= 4 and len(args) % 2 == 0 and isinstance(args[0], str):
            if is_prop_cand(args[0]) and is_prop_cand(args[2]):
                for i in range(0, len(args), 2):
                    new_kwargs[str(args[i])] = args[i + 1]
                return extracted_id, [], new_kwargs

        return extracted_id, args, new_kwargs

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
        # Follow variable aliases (e.g. root = productList)
        resolved_ast = ast
        while isinstance(resolved_ast, dict) and "variable" in resolved_ast:
            var_target = resolved_ast["variable"]
            if var_target in raw_symbols:
                resolved_ast = raw_symbols[var_target]
            elif var_target.lstrip("$").lstrip("/") in raw_symbols:
                resolved_ast = raw_symbols[var_target.lstrip("$").lstrip("/")]
            else:
                break

        if not isinstance(resolved_ast, dict) or "call" not in resolved_ast:
            return None

        raw_call = resolved_ast["call"]
        comp_name = self.helper.get_canonical_component_name(raw_call)
        if not comp_name or comp_name not in self.helper.components:
            # Not a component, could be a standalone action/helper; skip writing as component
            return None

        args = list(resolved_ast.get("args", []))
        kwargs = dict(resolved_ast.get("kwargs", {}))

        id_override, args, kwargs = self._detect_and_unpack_kv_args(comp_name, var_name, args, kwargs)
        if id_override and (var_name.startswith("_anon_comp_") or var_name.startswith("_inline_")):
            var_name = id_override

        properties = self.helper.get_component_properties(comp_name)
        comp_dict = {"id": var_name, "component": comp_name}

        # Sibling path tracking for check rules
        sibling_value_path = None

        non_check_properties = [p for p in properties if p != "checks"]
        raw_checks = []

        # Special case: List($/path, template, "direction")
        if comp_name == "List" and len(args) >= 2:
            first_arg = args[0]
            second_arg = args[1]
            if isinstance(first_arg, dict) and "path" in first_arg:
                template_comp_id = self._compile_value(second_arg, raw_symbols, ctx)
                args = [
                    {"path": first_arg["path"], "componentId": template_comp_id},
                    *args[2:],
                ]

        # Special case: Variadic children for components with ChildList (Column, Row, etc.)
        child_list_prop = None
        for p in non_check_properties:
            if self.helper.get_property_type(comp_name, p) == "ChildList":
                child_list_prop = p
                break

        if child_list_prop and child_list_prop == non_check_properties[0]:
            if args:
                first_arg = args[0]
                is_template = (
                    isinstance(first_arg, dict)
                    and (
                        "path" in first_arg
                        or "componentId" in first_arg
                        or first_arg.get("call") == "_template"
                    )
                )
                if not isinstance(first_arg, list) and not is_template:
                    if (
                        len(args) == 2
                        and isinstance(args[1], (int, float))
                        and "weight" in non_check_properties
                    ):
                        args = [[first_arg], args[1]]
                    else:
                        packed = []
                        non_packed = []
                        for a in args:
                            if _is_check_expression(a):
                                non_packed.append(a)
                            elif isinstance(a, list):
                                packed.extend(a)
                            else:
                                packed.append(a)
                        args = [packed] + non_packed

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

            is_action_arg = (
                isinstance(arg, dict)
                and (
                    "event" in arg
                    or "functionCall" in arg
                    or (
                        "call" in arg
                        and not self.helper.is_component(arg["call"])
                    )
                )
            )

            if prop_idx < len(non_check_properties):
                curr_prop = non_check_properties[prop_idx]
                curr_prop_type = self.helper.get_property_type(comp_name, curr_prop)

                if is_action_arg and curr_prop_type != "Action":
                    action_prop = None
                    for p_cand in non_check_properties[prop_idx:]:
                        if (
                            self.helper.get_property_type(comp_name, p_cand)
                            == "Action"
                        ):
                            action_prop = p_cand
                            break
                    if action_prop:
                        prop_arg_pairs.append((action_prop, arg, action_prop))
                        prop_idx += 1
                        continue

                prop_arg_pairs.append((curr_prop, arg, curr_prop))
                prop_idx += 1

        for k, v in kwargs.items():
            if _is_check_expression(v):
                if isinstance(v, list):
                    raw_checks.extend(v)
                else:
                    raw_checks.append(v)
                continue
            canon_k = self.helper.get_canonical_property_name(comp_name, k)
            if canon_k is None or canon_k not in properties:
                raise ExpressUnknownPropertyError(comp_name, k, properties)
            prop_arg_pairs.append((canon_k, v, k))

        seen_properties = set()
        for prop_name, arg, orig_name in prop_arg_pairs:
            canon_p = (
                self.helper.get_canonical_property_name(comp_name, prop_name)
                or prop_name
            )
            if canon_p in seen_properties:
                raise ExpressDuplicatePropertyError(comp_name, prop_name)
            seen_properties.add(canon_p)
            prop_name = canon_p
            if arg == {"skipped": True}:
                comp_dict[prop_name] = None
                continue

            prop_type = self.helper.get_property_type(comp_name, prop_name)
            mapped_val = self._compile_value(
                arg,
                raw_symbols,
                ctx,
                is_action=(
                    prop_name in ["action", "submitAction"]
                    or prop_type == "Action"
                ),
            )

            known_ids = set(raw_symbols.keys()) | {
                c.get("id") for c in ctx.extra_components
            }

            # Auto-wrap string child to Text component if property expects Child and was passed as label/text synonym
            if prop_type == "Child":
                if (
                    isinstance(mapped_val, str)
                    and mapped_val not in known_ids
                    and not mapped_val.startswith("_inline_")
                    and orig_name.lower() in ("label", "text", "title")
                ):
                    ctx.inline_counter += 1
                    inline_id = f"_inline_{ctx.inline_counter}"
                    ctx.extra_components.append({
                        "id": inline_id,
                        "component": "Text",
                        "text": mapped_val,
                    })
                    mapped_val = inline_id

            # Auto-wrap string items in ChildList to Text component
            if prop_type == "ChildList" and isinstance(mapped_val, list):
                wrapped_list = []
                for item in mapped_val:
                    if (
                        isinstance(item, str)
                        and item not in known_ids
                        and not item.startswith("_inline_")
                        and (" " in item or "\n" in item)
                    ):
                        ctx.inline_counter += 1
                        inline_id = f"_inline_{ctx.inline_counter}"
                        ctx.extra_components.append({
                            "id": inline_id,
                            "component": "Text",
                            "text": item,
                        })
                        wrapped_list.append(inline_id)
                    else:
                        wrapped_list.append(item)
                mapped_val = wrapped_list

            # Handle Tabs component tabs array
            if (
                comp_name == "Tabs"
                and prop_name == "tabs"
                and isinstance(mapped_val, list)
            ):
                fixed_tabs = []
                for tab_item in mapped_val:
                    if isinstance(tab_item, str):
                        ctx.inline_counter += 1
                        inline_id = f"_inline_{ctx.inline_counter}"
                        ctx.extra_components.append({
                            "id": inline_id,
                            "component": "Text",
                            "text": tab_item,
                        })
                        fixed_tabs.append({"title": tab_item, "child": inline_id})
                    elif isinstance(tab_item, dict):
                        tab_dict = dict(tab_item)
                        if "content" in tab_dict and "child" not in tab_dict:
                            c_val = tab_dict.pop("content")
                            tab_dict["child"] = (
                                c_val[0]
                                if isinstance(c_val, list) and c_val
                                else c_val
                            )
                        if "child" not in tab_dict or not tab_dict["child"]:
                            ctx.inline_counter += 1
                            inline_id = f"_inline_{ctx.inline_counter}"
                            ctx.extra_components.append({
                                "id": inline_id,
                                "component": "Text",
                                "text": tab_dict.get("title", ""),
                            })
                            tab_dict["child"] = inline_id
                        fixed_tabs.append(tab_dict)
                    else:
                        fixed_tabs.append(tab_item)
                mapped_val = fixed_tabs

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
                lower_map = {e.lower(): e for e in enum_vals}
                mapped_lower = mapped_val.lower()
                enum_synonyms = {
                    "password": "obscured",
                    "text": "shortText",
                    "multiline": "longText",
                    "textarea": "longText",
                    "int": "number",
                    "integer": "number",
                    "numeric": "number",
                    "horizontal": "row",
                    "vertical": "column",
                    "left": "start",
                    "right": "end",
                    "center": "center",
                }
                if mapped_lower in lower_map:
                    mapped_val = lower_map[mapped_lower]
                elif (
                    mapped_lower in enum_synonyms
                    and enum_synonyms[mapped_lower].lower() in lower_map
                ):
                    mapped_val = lower_map[enum_synonyms[mapped_lower].lower()]
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

        # Provide sensible defaults for missing required properties (e.g. Slider value/max)
        if comp_name == "Slider":
            if "value" not in comp_dict or comp_dict["value"] is None:
                comp_dict["value"] = 0
            if "max" not in comp_dict or comp_dict["max"] is None:
                comp_dict["max"] = 100

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
                clean_ref = ref_name.lstrip("$").lstrip("/")
                lookup_key = (
                    ref_name
                    if ref_name in raw_symbols
                    else (clean_ref if clean_ref in raw_symbols else None)
                )
                if lookup_key:
                    symbol_val = raw_symbols[lookup_key]
                    if (
                        isinstance(symbol_val, dict)
                        and self.helper.is_component(symbol_val.get("call", ""))
                    ):
                        return lookup_key
                    return self._compile_value(symbol_val, raw_symbols, ctx, is_action)
                return clean_ref or ref_name
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
                raw_call = val["call"]
                canon_comp = self.helper.get_canonical_component_name(raw_call)

                # Is it an inline component constructor?
                if canon_comp and canon_comp in self.helper.components:
                    ctx.inline_counter += 1
                    inline_id = f"_inline_{ctx.inline_counter}"
                    val_copy = dict(val)
                    val_copy["call"] = canon_comp
                    compiled_inline = self._compile_ast_node(
                        inline_id, val_copy, raw_symbols, ctx
                    )
                    if compiled_inline:
                        ctx.extra_components.append(compiled_inline)
                    return compiled_inline.get("id", inline_id) if compiled_inline else inline_id

                canon_fn = self.helper.get_canonical_function_name(raw_call)
                fn_name = canon_fn or raw_call
                fn_args = val["args"]

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
                    if not isinstance(path_val, dict) or "path" not in path_val:
                        raise ValueError(
                            "The first argument to _template must be a dynamic data"
                            f" binding path (prefixed by $), got: {fn_args[0]}"
                        )
                    comp_id_val = self._compile_value(
                        fn_args[1], raw_symbols, ctx, is_action
                    )
                    return {"path": path_val["path"], "componentId": comp_id_val}

                # Is it a reserved Event signature?
                if fn_name == "Event":
                    compiled_event_name = (
                        self._compile_value(fn_args[0], raw_symbols, ctx, is_action)
                        if len(fn_args) > 0
                        else ""
                    )
                    raw_context = (
                        self._compile_value(fn_args[1], raw_symbols, ctx, is_action)
                        if len(fn_args) > 1
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

            if (
                is_action
                and isinstance(val, dict)
                and "name" in val
                and "event" not in val
                and "functionCall" not in val
            ):
                compiled_context = {}
                raw_ctx = val.get("context", {})
                if isinstance(raw_ctx, dict):
                    for ck, cv in raw_ctx.items():
                        compiled_context[ck] = self._compile_value(
                            cv, raw_symbols, ctx, is_action=False
                        )
                return {
                    "event": {
                        "name": str(val["name"]),
                        "context": compiled_context,
                    }
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

        if isinstance(val, str):
            if val.startswith("${") and val.endswith("}"):
                inner = val[2:-1].strip()
                if inner.startswith(("/", "$")) and not any(
                    ch in inner for ch in " (),'\":\n\t"
                ):
                    clean_inner = "/" + inner.lstrip("/").lstrip("$")
                    return {"path": clean_inner}
            if val.startswith("$/") and not any(ch in val for ch in " (),'\":\n\t"):
                return {"path": "/" + val[2:].lstrip("/")}
            return val

        return val
