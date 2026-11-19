# Hakon Dev Kit

Plugin para **Google Antigravity** con reglas de trabajo, una skill de inicialización de proyectos Python y un servidor MCP para auditar datasets JSONL de Pure Data.

## Instalación

```bash
agy plugin install https://github.com/danko/hakon-dev-kit
```

Requisitos:

- Antigravity con soporte de plugins.
- `uv` ≥ 0.13.7 en el `PATH`. El servidor MCP lo necesita para arrancar.
- Python ≥ 3.10 para el servidor MCP. Si no hay uno compatible, `uv` descarga automáticamente un intérprete la primera vez.

## Componentes

| Componente | Ruta | Comportamiento |
|---|---|---|
| Regla de flujo | `rules/base.md` | `always_on`: idioma, planificación previa, walkthrough y límites de seguridad. |
| Reglas Python | `rules/python.md` | `glob` sobre `**/*.py, **/pyproject.toml, **/uv.lock`: uv, pytest, type hints, `pathlib`, estructura. |
| Reglas de UI | `rules/ui-light-mode.md` | `glob` sobre `**/*.html, **/*.css, **/*.js`: Light Mode minimalista. |
| Skill | `skills/init-uv-pytest/SKILL.md` | Inicializa un proyecto con `uv` + `pytest` y valida con una prueba. Invocable como `/init-uv-pytest`. |
| Servidor MCP | `servers/pd-audit/` | Herramientas `auditar_dataset_pd` y `limpiar_dataset_pd`. |

## Servidor MCP `pd-audit`

```json
{
  "mcpServers": {
    "pd-audit": {
      "command": "uv",
      "args": [
        "run", "--frozen",
        "--directory", "${PLUGIN_ROOT}/servers/pd-audit",
        "python", "-m", "pd_audit.mcp_server"
      ],
      "env": {
        "UV_PROJECT_ENVIRONMENT": "${PLUGIN_DATA}/venv"
      },
      "timeoutSeconds": 300
    }
  }
}
```

- `${PLUGIN_ROOT}` y `${PLUGIN_DATA}` los resuelve Antigravity; no hay rutas absolutas.
- El plugin instalado es de solo lectura, por eso el entorno virtual se crea en `${PLUGIN_DATA}/venv`.
- `--frozen` usa `servers/pd-audit/uv.lock` sin modificarlo.
- `timeoutSeconds: 300` da margen para auditar JSONL de entrenamiento grandes.
- Antigravity expone los servidores de plugins con el nombre `<plugin-name>_<server-name>`, es decir `hakon-dev-kit_pd-audit`. Los nombres de las herramientas no cambian.

### Herramientas

| Herramienta | Parámetros |
|---|---|
| `auditar_dataset_pd` | `ruta_jsonl` |
| `limpiar_dataset_pd` | `ruta_entrada`, `ruta_salida`, `dedupe_by` (`normalized` \| `exact`) |

## Estructura

```
hakon-dev-kit/
├── plugin.json
├── mcp_config.json
├── README.md
├── LICENSE
├── assets/logo.svg
├── rules/
│   ├── base.md
│   ├── python.md
│   └── ui-light-mode.md
├── skills/init-uv-pytest/SKILL.md
├── scripts/sync-pd-audit.sh
└── servers/pd-audit/
    ├── pyproject.toml
    ├── uv.lock
    └── src/pd_audit/
```

## Desarrollo

Validar el plugin:

```bash
agy plugin validate --strict .
```

Probar el servidor MCP manualmente:

```bash
UV_PROJECT_ENVIRONMENT=/tmp/pd-audit-venv \
  uv run --frozen --directory servers/pd-audit python -m pd_audit.mcp_server
```

## Nota de mantenimiento

`servers/pd-audit/src/pd_audit/` es una copia del paquete `pd_audit` del proyecto `mi-primera-app`. Para actualizarla:

```bash
./scripts/sync-pd-audit.sh
# o con otra ruta de origen:
PD_AUDIT_SRC=/ruta/a/src/pd_audit ./scripts/sync-pd-audit.sh
```

El script copia el paquete, regenera `servers/pd-audit/uv.lock` y ejecuta `agy plugin validate --strict` si está disponible.

## Licencia

MIT. Ver [LICENSE](LICENSE).
