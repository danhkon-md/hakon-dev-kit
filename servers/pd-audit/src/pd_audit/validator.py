import re
from dataclasses import dataclass
from pd_audit.models import ValidationIssue

INDEXABLE_X_TYPES: frozenset[str] = frozenset({
    "obj",
    "msg",
    "floatatom",
    "symbolatom",
    "listbox",
    "text",
    "scalar",
    "array",
})

FENCED_BLOCK_RE = re.compile(r"```(?:pd|puredata)?\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)


@dataclass(slots=True)
class PatchValidationResult:
    is_valid: bool
    object_count: int
    connection_count: int
    patch_lines: int
    normalized_patch: str
    issues: list[ValidationIssue]


def strip_markdown_fence(raw_text: str) -> tuple[str, bool]:
    """Extrae el contenido de un bloque cercado Markdown si existe."""
    match = FENCED_BLOCK_RE.search(raw_text)
    if match:
        return match.group(1).strip(), True
    return raw_text.strip(), False


def split_pd_statements(patch_text: str) -> tuple[list[str], bool]:
    """Divide un parche Pure Data en sentencias terminadas en ';', respetando '\\;'."""
    statements: list[str] = []
    current: list[str] = []
    i = 0
    length = len(patch_text)

    while i < length:
        ch = patch_text[i]
        if ch == "\\" and i + 1 < length and patch_text[i + 1] == ";":
            current.append("\\;")
            i += 2
            continue
        if ch == ";":
            stmt = " ".join("".join(current).strip().split())
            if stmt:
                statements.append(stmt)
            current = []
        else:
            current.append(ch)
        i += 1

    trailing = "".join(current).strip()
    has_unterminated = bool(trailing)
    return statements, has_unterminated


def _is_number(token: str) -> bool:
    try:
        float(token)
        return True
    except ValueError:
        return False


def _is_int(token: str) -> bool:
    try:
        int(token)
        return True
    except ValueError:
        return False


def validate_pd_patch(raw_patch: str, line_number: int = 1) -> PatchValidationResult:
    """Valida la sintaxis y estructura básica de un parche Pure Data."""
    issues: list[ValidationIssue] = []
    cleaned_patch, had_fence = strip_markdown_fence(raw_patch)

    if had_fence:
        issues.append(
            ValidationIssue(
                line_number=line_number,
                code="MARKDOWN_FENCE_WRAPPED",
                severity="WARNING",
                message="El parche está envuelto en un bloque Markdown (```); se recomienda texto Pd puro.",
            )
        )

    if not cleaned_patch:
        issues.append(
            ValidationIssue(
                line_number=line_number,
                code="EMPTY_PATCH",
                severity="ERROR",
                message="El parche Pure Data está vacío.",
            )
        )
        return PatchValidationResult(
            is_valid=False,
            object_count=0,
            connection_count=0,
            patch_lines=0,
            normalized_patch="",
            issues=issues,
        )

    patch_lines = len([ln for ln in cleaned_patch.splitlines() if ln.strip()])
    statements, has_unterminated = split_pd_statements(cleaned_patch)

    if has_unterminated:
        issues.append(
            ValidationIssue(
                line_number=line_number,
                code="MISSING_SEMICOLON",
                severity="ERROR",
                message="El parche contiene una sentencia sin punto y coma ';' final.",
            )
        )

    if not statements:
        issues.append(
            ValidationIssue(
                line_number=line_number,
                code="NO_STATEMENTS",
                severity="ERROR",
                message="No se encontraron sentencias Pure Data válidas terminadas en ';'.",
            )
        )
        return PatchValidationResult(
            is_valid=False,
            object_count=0,
            connection_count=0,
            patch_lines=patch_lines,
            normalized_patch="",
            issues=issues,
        )

    # 1. Validar cabecera #N canvas
    first_tokens = statements[0].split()
    if len(first_tokens) < 2 or first_tokens[0] != "#N" or first_tokens[1] != "canvas":
        issues.append(
            ValidationIssue(
                line_number=line_number,
                code="MISSING_ROOT_CANVAS",
                severity="ERROR",
                message="El parche debe comenzar con una declaración '#N canvas <x> <y> <w> <h> <font>;'.",
            )
        )
    elif len(first_tokens) < 7 or not all(_is_int(tok) for tok in first_tokens[2:7]):
        issues.append(
            ValidationIssue(
                line_number=line_number,
                code="INVALID_CANVAS_ARGS",
                severity="ERROR",
                message=f"Argumentos inválidos en '#N canvas': '{statements[0]};' (se esperan 5 enteros x y w h font).",
            )
        )

    canvas_stack: list[int] = [0]
    strict_obj_count = 0
    connection_count = 0
    seen_connections: set[tuple[int, int, int, int, int]] = set()

    for idx, stmt in enumerate(statements):
        tokens = stmt.split()
        if not tokens:
            continue

        prefix = tokens[0]
        if prefix not in {"#N", "#X", "#A"}:
            issues.append(
                ValidationIssue(
                    line_number=line_number,
                    code="UNKNOWN_DIRECTIVE",
                    severity="ERROR",
                    message=f"Directiva desconocida '{prefix}' en sentencia #{idx + 1}: '{stmt};'.",
                )
            )
            continue

        if prefix == "#N":
            if len(tokens) < 2 or tokens[1] != "canvas":
                issues.append(
                    ValidationIssue(
                        line_number=line_number,
                        code="INVALID_N_DIRECTIVE",
                        severity="ERROR",
                        message=f"Directiva #N inválida en sentencia #{idx + 1}: '{stmt};'.",
                    )
                )
            else:
                if idx > 0:
                    if len(tokens) < 7 or not all(_is_int(tok) for tok in tokens[2:6]):
                        issues.append(
                            ValidationIssue(
                                line_number=line_number,
                                code="INVALID_CANVAS_ARGS",
                                severity="ERROR",
                                message=f"Subpatch '#N canvas' con argumentos inválidos: '{stmt};'.",
                            )
                        )
                    canvas_stack.append(0)
            continue

        if prefix == "#X":
            if len(tokens) < 2:
                issues.append(
                    ValidationIssue(
                        line_number=line_number,
                        code="INCOMPLETE_X_DIRECTIVE",
                        severity="ERROR",
                        message=f"Sentencia '#X' incompleta en #{idx + 1}: '{stmt};'.",
                    )
                )
                continue

            kind = tokens[1]

            if kind == "obj":
                strict_obj_count += 1
                canvas_stack[-1] += 1
                if len(tokens) < 5:
                    issues.append(
                        ValidationIssue(
                            line_number=line_number,
                            code="INVALID_OBJ_SYNTAX",
                            severity="ERROR",
                            message=f"Sentencia '#X obj' requiere coordenadas x, y y nombre de objeto: '{stmt};'.",
                        )
                    )
                elif not (_is_number(tokens[2]) and _is_number(tokens[3])):
                    issues.append(
                        ValidationIssue(
                            line_number=line_number,
                            code="INVALID_OBJ_COORDS",
                            severity="ERROR",
                            message=f"Coordenadas no numéricas en '#X obj': '{stmt};'.",
                        )
                    )

            elif kind in INDEXABLE_X_TYPES:
                canvas_stack[-1] += 1
                if len(tokens) < 4 or not (_is_number(tokens[2]) and _is_number(tokens[3])):
                    issues.append(
                        ValidationIssue(
                            line_number=line_number,
                            code=f"INVALID_{kind.upper()}_SYNTAX",
                            severity="ERROR",
                            message=f"Coordenadas o sintaxis inválida en '#X {kind}': '{stmt};'.",
                        )
                    )

            elif kind == "restore":
                if len(canvas_stack) <= 1:
                    issues.append(
                        ValidationIssue(
                            line_number=line_number,
                            code="UNMATCHED_RESTORE",
                            severity="ERROR",
                            message=f"'#X restore' sin subpatch '#N canvas' correspondiente: '{stmt};'.",
                        )
                    )
                else:
                    canvas_stack.pop()
                    canvas_stack[-1] += 1

            elif kind == "connect":
                connection_count += 1
                if len(tokens) != 6 or not all(_is_int(tok) for tok in tokens[2:6]):
                    issues.append(
                        ValidationIssue(
                            line_number=line_number,
                            code="INVALID_CONNECT_SYNTAX",
                            severity="ERROR",
                            message=f"'#X connect' requiere exactamente 4 enteros (src outlet dst inlet): '{stmt};'.",
                        )
                    )
                    continue

                src_obj, src_out, dst_obj, dst_in = (int(tok) for tok in tokens[2:6])
                if min(src_obj, src_out, dst_obj, dst_in) < 0:
                    issues.append(
                        ValidationIssue(
                            line_number=line_number,
                            code="NEGATIVE_CONNECT_INDEX",
                            severity="ERROR",
                            message=f"Índices negativos en '#X connect': '{stmt};'.",
                        )
                    )
                    continue

                current_canvas_nodes = canvas_stack[-1]
                if src_obj >= current_canvas_nodes or dst_obj >= current_canvas_nodes:
                    issues.append(
                        ValidationIssue(
                            line_number=line_number,
                            code="CONNECT_INDEX_OUT_OF_RANGE",
                            severity="ERROR",
                            message=(
                                f"Conexión fuera de rango en '{stmt};': "
                                f"referencia objeto {max(src_obj, dst_obj)}, pero solo existen {current_canvas_nodes} objetos."
                            ),
                        )
                    )

                if src_obj == dst_obj:
                    issues.append(
                        ValidationIssue(
                            line_number=line_number,
                            code="SELF_CONNECTION",
                            severity="WARNING",
                            message=f"Auto-conexión detectada en objeto {src_obj}: '{stmt};'.",
                        )
                    )

                conn_key = (len(canvas_stack), src_obj, src_out, dst_obj, dst_in)
                if conn_key in seen_connections:
                    issues.append(
                        ValidationIssue(
                            line_number=line_number,
                            code="DUPLICATE_CONNECTION",
                            severity="WARNING",
                            message=f"Conexión duplicada dentro del mismo canvas: '{stmt};'.",
                        )
                    )
                seen_connections.add(conn_key)

    if len(canvas_stack) > 1:
        issues.append(
            ValidationIssue(
                line_number=line_number,
                code="UNCLOSED_SUBPATCH",
                severity="ERROR",
                message=f"Quedaron {len(canvas_stack) - 1} subparches '#N canvas' sin cerrar con '#X restore'.",
            )
        )

    if strict_obj_count == 0:
        issues.append(
            ValidationIssue(
                line_number=line_number,
                code="NO_OBJECTS_DEFINED",
                severity="ERROR",
                message="El parche no define ningún objeto '#X obj'.",
            )
        )

    has_errors = any(issue.severity == "ERROR" for issue in issues)
    normalized = "\n".join(f"{s};" for s in statements)

    return PatchValidationResult(
        is_valid=not has_errors,
        object_count=strict_obj_count,
        connection_count=connection_count,
        patch_lines=patch_lines,
        normalized_patch=normalized,
        issues=issues,
    )
