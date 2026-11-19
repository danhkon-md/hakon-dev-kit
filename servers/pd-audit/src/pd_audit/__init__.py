"""Herramienta CLI para auditar datasets JSONL de parches Pure Data."""

from pd_audit.auditor import audit_jsonl_file
from pd_audit.models import (
    AuditReport,
    CleaningSummary,
    DedupeMode,
    DistributionStats,
    DuplicateGroup,
    PatchMetrics,
    ValidationIssue,
)
from pd_audit.reporter import save_json, save_markdown, to_json, to_markdown
from pd_audit.validator import validate_pd_patch

__all__ = [
    "AuditReport",
    "CleaningSummary",
    "DedupeMode",
    "DistributionStats",
    "DuplicateGroup",
    "PatchMetrics",
    "ValidationIssue",
    "audit_jsonl_file",
    "save_json",
    "save_markdown",
    "to_json",
    "to_markdown",
    "validate_pd_patch",
]
