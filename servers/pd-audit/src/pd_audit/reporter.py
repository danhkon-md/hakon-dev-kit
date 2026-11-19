import json
from pathlib import Path
from pd_audit.models import AuditReport

METRIC_LABELS: dict[str, str] = {
    "char_length": "Longitud (caracteres)",
    "patch_lines": "Líneas por parche",
    "object_count": "Objetos (#X obj)",
    "connection_count": "Conexiones (#X connect)",
}


def to_json(report: AuditReport, indent: int = 2) -> str:
    """Serializa el reporte de auditoría a JSON formateado."""
    return json.dumps(report.to_dict(), indent=indent, ensure_ascii=False)


def save_json(report: AuditReport, output_path: Path) -> None:
    """Guarda el reporte de auditoría en formato JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(to_json(report) + "\n", encoding="utf-8")


def to_markdown(report: AuditReport) -> str:
    """Genera un reporte limpio en Markdown con resumen, estadísticas, duplicados y errores."""
    lines: list[str] = [
        "# Reporte de Auditoría JSONL — Pure Data",
        "",
        f"**Archivo auditado:** `{report.source_file}`",
        "",
        "## 1. Resumen General",
        "",
        "| Métrica | Valor |",
        "| :--- | ---: |",
        f"| Total de entradas procesadas | {report.total_lines} |",
        f"| Parches válidos | {report.valid_entries} |",
        f"| Parches inválidos | {report.invalid_entries} |",
        f"| Tasa de validez | {report.validity_rate:.2f}% |",
        f"| Entradas duplicadas exactas (JSON) | {report.exact_duplicate_entries} ({len(report.exact_duplicate_groups)} grupos) |",
        f"| Parches duplicados normalizados (Pd) | {report.patch_duplicate_entries} ({len(report.patch_duplicate_groups)} grupos) |",
        f"| Total de hallazgos (ERROR / WARNING) | {len(report.issues)} |",
        f"| Modo de deduplicación (limpieza) | `{report.cleaning.dedupe_mode}` |",
        f"| Líneas de entrada (limpieza) | {report.cleaning.input_lines} |",
        f"| Líneas conservadas (limpias) | {report.cleaning.kept_lines} |",
        f"| Descartadas por error | {report.cleaning.discarded_by_error} |",
        f"| Descartadas por duplicado | {report.cleaning.discarded_by_duplicate} |",
    ]
    if report.cleaning.clean_output_path:
        lines.append(
            f"| Archivo limpio exportado | `{report.cleaning.clean_output_path}` |"
        )

    lines.extend([
        "",
        "## 2. Estadísticas de Longitud y Complejidad",
        "",
        "| Dimensión | Mín | Máx | Media | Mediana | P95 |",
        "| :--- | ---: | ---: | ---: | ---: | ---: |",
    ])

    for key, label in METRIC_LABELS.items():
        stats = report.length_stats.get(key)
        if stats:
            lines.append(
                f"| {label} | {stats.min:.2f} | {stats.max:.2f} | "
                f"{stats.mean:.2f} | {stats.median:.2f} | {stats.p95:.2f} |"
            )

    lines.extend(["", "## 3. Detección de Duplicados", ""])

    if not report.exact_duplicate_groups and not report.patch_duplicate_groups:
        lines.append("No se detectaron entradas ni parches duplicados.")
    else:
        lines.extend([
            "| Tipo | Hash ID | Líneas afectadas |",
            "| :--- | :--- | :--- |",
        ])
        for group in report.exact_duplicate_groups:
            line_list = ", ".join(str(ln) for ln in group.lines)
            lines.append(f"| Exacto (JSON) | `{group.hash_id}` | {line_list} |")
        for group in report.patch_duplicate_groups:
            line_list = ", ".join(str(ln) for ln in group.lines)
            lines.append(f"| Parche normalizado | `{group.hash_id}` | {line_list} |")

    lines.extend(["", "## 4. Hallazgos de Validación Sintáctica", ""])

    if not report.issues:
        lines.append("No se encontraron errores ni advertencias de sintaxis.")
    else:
        lines.extend([
            "| Línea | Severidad | Código | Descripción |",
            "| ---: | :--- | :--- | :--- |",
        ])
        for issue in report.issues:
            safe_msg = issue.message.replace("|", "\\|")
            lines.append(
                f"| {issue.line_number} | **{issue.severity}** | `{issue.code}` | {safe_msg} |"
            )

    return "\n".join(lines) + "\n"


def save_markdown(report: AuditReport, output_path: Path) -> None:
    """Guarda el reporte de auditoría en formato Markdown."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(to_markdown(report), encoding="utf-8")
