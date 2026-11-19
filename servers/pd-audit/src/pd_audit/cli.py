import argparse
import sys
from pathlib import Path
from typing import Sequence

from pd_audit.auditor import audit_jsonl_file
from pd_audit.reporter import save_json, save_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pd-audit",
        description="Audita archivos JSONL de entrenamiento para Pure Data (duplicados, sintaxis y estadísticas).",
    )
    parser.add_argument(
        "input_file",
        type=Path,
        help="Ruta al archivo .jsonl de entrada.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Ruta donde exportar el reporte en formato JSON.",
    )
    parser.add_argument(
        "--md-out",
        type=Path,
        default=None,
        help="Ruta donde exportar el reporte en formato Markdown.",
    )
    parser.add_argument(
        "--patch-key",
        type=str,
        default=None,
        help="Nombre explícito de la llave JSON que contiene el parche Pure Data.",
    )
    parser.add_argument(
        "--clean-out",
        type=Path,
        default=None,
        help="Ruta donde exportar el dataset JSONL limpio.",
    )
    parser.add_argument(
        "--dedupe-by",
        choices=["exact", "normalized"],
        default="normalized",
        help="Criterio de deduplicación para el filtrado limpio (por defecto: normalized).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Devuelve código de salida 1 si hay entradas inválidas o duplicadas.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    input_path: Path = args.input_file
    if not input_path.exists():
        print(f"Error: El archivo '{input_path}' no existe.", file=sys.stderr)
        return 2

    report = audit_jsonl_file(
        input_path,
        patch_key=args.patch_key,
        clean_out=args.clean_out,
        dedupe_by=args.dedupe_by,
    )

    if args.json_out is not None:
        save_json(report, args.json_out)
    if args.md_out is not None:
        save_markdown(report, args.md_out)

    print(
        f"[pd-audit] Archivo: {report.source_file} | "
        f"Total: {report.total_lines} | "
        f"Válidos: {report.valid_entries} ({report.validity_rate:.2f}%) | "
        f"Inválidos: {report.invalid_entries} | "
        f"Duplicados (parche): {report.patch_duplicate_entries} | "
        f"Limpieza ({report.cleaning.dedupe_mode}): "
        f"{report.cleaning.kept_lines}/{report.cleaning.input_lines} conservados "
        f"(err={report.cleaning.discarded_by_error}, dup={report.cleaning.discarded_by_duplicate})"
    )

    if args.clean_out is not None:
        print(f"[pd-audit] Dataset limpio exportado en: {args.clean_out}")
    if args.json_out is not None:
        print(f"[pd-audit] Reporte JSON exportado en: {args.json_out}")
    if args.md_out is not None:
        print(f"[pd-audit] Reporte Markdown exportado en: {args.md_out}")

    if args.strict and (
        report.invalid_entries > 0
        or report.exact_duplicate_entries > 0
        or report.patch_duplicate_entries > 0
    ):
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
