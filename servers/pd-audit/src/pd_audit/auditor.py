import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any

from pd_audit.models import (
    AuditReport,
    CleaningSummary,
    DedupeMode,
    DistributionStats,
    DuplicateGroup,
    PatchMetrics,
    ValidationIssue,
)
from pd_audit.validator import validate_pd_patch

CANDIDATE_PATCH_KEYS: tuple[str, ...] = (
    "patch",
    "output",
    "completion",
    "response",
    "code",
    "text",
    "content",
)


def extract_patch_from_record(record: dict[str, Any], patch_key: str | None = None) -> str | None:
    """Extrae el texto del parche Pure Data desde varios esquemas comunes de JSONL."""
    if patch_key:
        val = record.get(patch_key)
        return val if isinstance(val, str) else None

    for key in CANDIDATE_PATCH_KEYS:
        val = record.get(key)
        if isinstance(val, str) and val.strip():
            return val

    messages = record.get("messages")
    if isinstance(messages, list):
        for msg in reversed(messages):
            if isinstance(msg, dict) and msg.get("role") == "assistant":
                content = msg.get("content")
                if isinstance(content, str) and content.strip():
                    return content

    return None


def compute_distribution(values: list[int | float]) -> DistributionStats:
    """Calcula min, max, media, mediana y percentil 95 de una serie numérica."""
    if not values:
        return DistributionStats(min=0.0, max=0.0, mean=0.0, median=0.0, p95=0.0)

    sorted_vals = sorted(float(v) for v in values)
    count = len(sorted_vals)
    p95_idx = min(count - 1, max(0, math.ceil(0.95 * count) - 1))

    return DistributionStats(
        min=sorted_vals[0],
        max=sorted_vals[-1],
        mean=statistics.fmean(sorted_vals),
        median=statistics.median(sorted_vals),
        p95=sorted_vals[p95_idx],
    )


def _short_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def audit_jsonl_file(
    path: Path,
    patch_key: str | None = None,
    clean_out: Path | None = None,
    dedupe_by: DedupeMode = "normalized",
) -> AuditReport:
    """Audita un archivo JSONL de parches Pure Data y retorna un AuditReport completo."""
    if not path.exists():
        raise FileNotFoundError(f"El archivo '{path}' no existe.")

    if clean_out is not None and clean_out.resolve() == path.resolve():
        raise ValueError("El archivo --clean-out no puede ser el mismo archivo de entrada.")

    issues: list[ValidationIssue] = []
    metrics_list: list[PatchMetrics] = []
    exact_hash_map: dict[str, list[int]] = {}
    patch_hash_map: dict[str, list[int]] = {}

    kept_raw_lines: list[str] = []
    seen_clean_hashes: set[str] = set()
    discarded_by_error = 0
    discarded_by_duplicate = 0

    total_lines = 0
    valid_entries = 0
    invalid_entries = 0

    with path.open("r", encoding="utf-8") as fh:
        for line_number, raw_line in enumerate(fh, start=1):
            stripped = raw_line.strip()
            if not stripped:
                continue

            total_lines += 1

            try:
                record = json.loads(stripped)
            except json.JSONDecodeError as exc:
                invalid_entries += 1
                discarded_by_error += 1
                issues.append(
                    ValidationIssue(
                        line_number=line_number,
                        code="INVALID_JSON",
                        severity="ERROR",
                        message=f"JSON malformado en línea {line_number}: {exc.msg}.",
                    )
                )
                continue

            if not isinstance(record, dict):
                invalid_entries += 1
                discarded_by_error += 1
                issues.append(
                    ValidationIssue(
                        line_number=line_number,
                        code="JSON_NOT_OBJECT",
                        severity="ERROR",
                        message=f"Se esperaba un objeto JSON en la línea {line_number}.",
                    )
                )
                continue

            canonical_json = json.dumps(record, sort_keys=True, ensure_ascii=False)
            exact_hash = _short_sha256(canonical_json)
            exact_hash_map.setdefault(exact_hash, []).append(line_number)

            patch_text = extract_patch_from_record(record, patch_key=patch_key)
            if patch_text is None:
                invalid_entries += 1
                discarded_by_error += 1
                issues.append(
                    ValidationIssue(
                        line_number=line_number,
                        code="MISSING_PATCH_FIELD",
                        severity="ERROR",
                        message=(
                            f"No se encontró campo de parche Pure Data en la línea {line_number}."
                            + (f" (llave buscada: '{patch_key}')" if patch_key else "")
                        ),
                    )
                )
                continue

            val_result = validate_pd_patch(patch_text, line_number=line_number)
            issues.extend(val_result.issues)

            norm_hash = _short_sha256(val_result.normalized_patch)
            if val_result.normalized_patch:
                patch_hash_map.setdefault(norm_hash, []).append(line_number)

            if val_result.is_valid:
                valid_entries += 1
                dedupe_hash = exact_hash if dedupe_by == "exact" else norm_hash
                if dedupe_hash in seen_clean_hashes:
                    discarded_by_duplicate += 1
                else:
                    seen_clean_hashes.add(dedupe_hash)
                    kept_raw_lines.append(stripped)
            else:
                invalid_entries += 1
                discarded_by_error += 1

            metrics_list.append(
                PatchMetrics(
                    line_number=line_number,
                    char_length=len(patch_text),
                    patch_lines=val_result.patch_lines,
                    object_count=val_result.object_count,
                    connection_count=val_result.connection_count,
                    is_valid=val_result.is_valid,
                )
            )

    if clean_out is not None:
        clean_out.parent.mkdir(parents=True, exist_ok=True)
        clean_out.write_text(
            "\n".join(kept_raw_lines) + ("\n" if kept_raw_lines else ""),
            encoding="utf-8",
        )

    exact_duplicates = [
        DuplicateGroup(kind="exact_json", hash_id=h, lines=lines)
        for h, lines in exact_hash_map.items()
        if len(lines) > 1
    ]

    patch_duplicates = [
        DuplicateGroup(kind="normalized_patch", hash_id=h, lines=lines)
        for h, lines in patch_hash_map.items()
        if len(lines) > 1
    ]

    length_stats = {
        "char_length": compute_distribution([m.char_length for m in metrics_list]),
        "patch_lines": compute_distribution([m.patch_lines for m in metrics_list]),
        "object_count": compute_distribution([m.object_count for m in metrics_list]),
        "connection_count": compute_distribution([m.connection_count for m in metrics_list]),
    }

    cleaning = CleaningSummary(
        dedupe_mode=dedupe_by,
        input_lines=total_lines,
        kept_lines=len(kept_raw_lines),
        discarded_by_error=discarded_by_error,
        discarded_by_duplicate=discarded_by_duplicate,
        clean_output_path=str(clean_out) if clean_out else None,
    )

    return AuditReport(
        source_file=str(path),
        total_lines=total_lines,
        valid_entries=valid_entries,
        invalid_entries=invalid_entries,
        exact_duplicate_groups=exact_duplicates,
        patch_duplicate_groups=patch_duplicates,
        length_stats=length_stats,
        issues=issues,
        cleaning=cleaning,
    )
