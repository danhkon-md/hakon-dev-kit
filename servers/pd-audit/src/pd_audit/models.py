from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Severity = Literal["ERROR", "WARNING"]
DuplicateKind = Literal["exact_json", "normalized_patch"]
DedupeMode = Literal["exact", "normalized"]


@dataclass(slots=True)
class CleaningSummary:
    dedupe_mode: DedupeMode
    input_lines: int
    kept_lines: int
    discarded_by_error: int
    discarded_by_duplicate: int
    clean_output_path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ValidationIssue:
    line_number: int
    code: str
    severity: Severity
    message: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class PatchMetrics:
    line_number: int
    char_length: int
    patch_lines: int
    object_count: int
    connection_count: int
    is_valid: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DistributionStats:
    min: float
    max: float
    mean: float
    median: float
    p95: float

    def to_dict(self) -> dict[str, float]:
        return {
            "min": round(self.min, 2),
            "max": round(self.max, 2),
            "mean": round(self.mean, 2),
            "median": round(self.median, 2),
            "p95": round(self.p95, 2),
        }


@dataclass(slots=True)
class DuplicateGroup:
    kind: DuplicateKind
    hash_id: str
    lines: list[int]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class AuditReport:
    source_file: str
    total_lines: int
    valid_entries: int
    invalid_entries: int
    exact_duplicate_groups: list[DuplicateGroup] = field(default_factory=list)
    patch_duplicate_groups: list[DuplicateGroup] = field(default_factory=list)
    length_stats: dict[str, DistributionStats] = field(default_factory=dict)
    issues: list[ValidationIssue] = field(default_factory=list)
    cleaning: CleaningSummary = field(
        default_factory=lambda: CleaningSummary(
            dedupe_mode="normalized",
            input_lines=0,
            kept_lines=0,
            discarded_by_error=0,
            discarded_by_duplicate=0,
        )
    )

    @property
    def validity_rate(self) -> float:
        if self.total_lines == 0:
            return 0.0
        return round((self.valid_entries / self.total_lines) * 100.0, 2)

    @property
    def exact_duplicate_entries(self) -> int:
        return sum(len(group.lines) - 1 for group in self.exact_duplicate_groups)

    @property
    def patch_duplicate_entries(self) -> int:
        return sum(len(group.lines) - 1 for group in self.patch_duplicate_groups)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_file": self.source_file,
            "summary": {
                "total_lines": self.total_lines,
                "valid_entries": self.valid_entries,
                "invalid_entries": self.invalid_entries,
                "validity_rate_pct": self.validity_rate,
                "exact_duplicate_groups": len(self.exact_duplicate_groups),
                "exact_duplicate_entries": self.exact_duplicate_entries,
                "patch_duplicate_groups": len(self.patch_duplicate_groups),
                "patch_duplicate_entries": self.patch_duplicate_entries,
                "total_issues": len(self.issues),
            },
            "length_stats": {
                metric: stats.to_dict() for metric, stats in self.length_stats.items()
            },
            "duplicates": {
                "exact_json": [g.to_dict() for g in self.exact_duplicate_groups],
                "normalized_patch": [g.to_dict() for g in self.patch_duplicate_groups],
            },
            "cleaning": self.cleaning.to_dict(),
            "issues": [issue.to_dict() for issue in self.issues],
        }
