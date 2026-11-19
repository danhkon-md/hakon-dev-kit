from pathlib import Path
from typing import Any, cast

try:
    from mcp.server.mcpserver import MCPServer as FastMCP
except ImportError:  # pragma: no cover - compatibilidad con mcp < 2.0
    from mcp.server.fastmcp import FastMCP  # type: ignore[no-redef]

from pd_audit.auditor import audit_jsonl_file
from pd_audit.models import DedupeMode

mcp = FastMCP("pd-audit")


@mcp.tool()
def auditar_dataset_pd(ruta_jsonl: str) -> dict[str, Any]:
    """Audita un archivo JSONL de entrenamiento para Pure Data.

    Analiza la sintaxis de cada parche (#N canvas, #X obj, #X connect),
    detecta entradas duplicadas exactas y normalizadas, y calcula estadísticas
    de longitud y complejidad.

    Args:
        ruta_jsonl: Ruta al archivo .jsonl que se desea auditar.

    Returns:
        Diccionario con el resumen de entradas válidas, inválidas, duplicados,
        estadísticas de longitud y listado de hallazgos sintácticos.
    """
    report = audit_jsonl_file(Path(ruta_jsonl))
    return report.to_dict()


@mcp.tool()
def limpiar_dataset_pd(
    ruta_entrada: str,
    ruta_salida: str,
    dedupe_by: str = "normalized",
) -> dict[str, Any]:
    """Filtra errores sintácticos y duplicados de un dataset JSONL de Pure Data.

    Conserva únicamente la primera aparición de cada entrada válida (sin hallazgos
    de severidad ERROR) y guarda el archivo JSONL limpio listo para entrenamiento.

    Args:
        ruta_entrada: Ruta al archivo .jsonl original de entrada.
        ruta_salida: Ruta donde se exportará el archivo .jsonl limpio.
        dedupe_by: Criterio de deduplicación ('normalized' o 'exact').

    Returns:
        Diccionario con las estadísticas de limpieza (líneas de entrada,
        conservadas, descartadas por error o duplicado) y el resumen general.
    """
    if dedupe_by not in ("exact", "normalized"):
        raise ValueError("El parámetro 'dedupe_by' debe ser 'normalized' o 'exact'.")

    mode = cast(DedupeMode, dedupe_by)
    report = audit_jsonl_file(
        Path(ruta_entrada),
        clean_out=Path(ruta_salida),
        dedupe_by=mode,
    )
    return {
        "source_file": report.source_file,
        "clean_output_path": report.cleaning.clean_output_path,
        "cleaning": report.cleaning.to_dict(),
        "summary": report.to_dict()["summary"],
    }


def main() -> None:
    """Inicia el servidor MCP local mediante transporte stdio."""
    mcp.run()


if __name__ == "__main__":
    main()
