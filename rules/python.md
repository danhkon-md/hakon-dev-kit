---
trigger: glob
globs: "**/*.py, **/pyproject.toml, **/uv.lock"
description: Convenciones Python del kit (uv, pytest, type hints, pathlib)
---
# Reglas Python

## Entornos y dependencias
- Usa `uv` para todo: `uv init`, `uv add`, `uv sync`, `uv run`. No crees entornos con `venv`/`pip` manualmente.
- Versiona `uv.lock`; no lo edites a mano ni lo añadas a `.gitignore`.
- Para ejecutar código o pruebas usa siempre `uv run <comando>`, nunca el Python del sistema.

## Código
- Escribe Python 3 moderno con *type hints* estrictos en funciones públicas, métodos y valores de retorno.
- Usa `pathlib` en lugar de `os.path`.
- Mantén los módulos pequeños, desacoplados y fáciles de leer.

## Estructura
- `src/` para el código principal (como paquete, no como módulos sueltos), `tests/` para pruebas con `pytest`, `scripts/` para utilidades.
- Configura `[tool.pytest.ini_options]` con `pythonpath = ["src"]` y `testpaths = ["tests"]`.
- Incluye siempre un `README.md` actualizado con instalación y uso.

## Entorno local
- El entorno de referencia es macOS Apple Silicon. Si la app procesa audio, video o archivos locales, aprovecha herramientas nativas de macOS y aceleración por hardware cuando corresponda.
