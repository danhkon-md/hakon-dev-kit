# pd-audit-mcp

Servidor MCP (stdio) que audita y limpia datasets `.jsonl` de entrenamiento para **Pure Data (Pd)**.

## Herramientas

| Herramienta | Parámetros | Descripción |
|---|---|---|
| `auditar_dataset_pd` | `ruta_jsonl` | Analiza sintaxis de parches, duplicados exactos/normalizados y estadísticas. |
| `limpiar_dataset_pd` | `ruta_entrada`, `ruta_salida`, `dedupe_by` (`normalized`\|`exact`) | Descarta entradas con errores y duplicados; exporta un JSONL limpio. |

## Uso manual

```bash
uv run --frozen --directory . python -m pd_audit.mcp_server
```

Antigravity lanza este comando automáticamente vía `mcp_config.json` del plugin.
El entorno virtual se crea en `${PLUGIN_DATA}/venv` (no en la raíz del plugin, que es de solo lectura al instalarse).

## CLI equivalente

```bash
uv run python -m pd_audit.cli --help
```

## Procedencia

Este paquete es una copia de `pd_audit` del proyecto `mi-primera-app`.
Si el original cambia, sincroniza esta carpeta antes de publicar una nueva versión del plugin.
