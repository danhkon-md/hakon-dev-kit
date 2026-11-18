---
name: init-uv-pytest
description: Inicializa un proyecto Python moderno con uv, configura pytest como dependencia de desarrollo, crea las carpetas src/ y tests/, y ejecuta una prueba inicial de verificación. Úsala siempre que se pida crear, iniciar o estructurar un proyecto Python desde cero.
---

# Inicialización de Proyecto Python con uv y pytest

Ejecuta estos pasos en orden dentro de la raíz del workspace actual:

1. **Verifica herramientas:** Confirma que `uv` esté disponible ejecutando `uv --version`.
2. **Inicializa el proyecto:** Si no existe `pyproject.toml`, ejecuta `uv init --no-workspace` sin sobrescribir archivos existentes como `GEMINI.md` o `README.md`. Si `uv init` genera un archivo `main.py` o `hello.py` de relleno en la raíz, muévelo o reemplázalo dentro de `src/`.
3. **Instala pytest:** Agrega `pytest` como dependencia de desarrollo ejecutando:
   `uv add --dev pytest`
4. **Crea la estructura estándar:** Asegura que existan las carpetas `src/`, `tests/` y `scripts/`, además de un archivo `tests/__init__.py` vacío para facilitar las importaciones.
5. **Genera código y prueba base:**
   - Crea `src/core.py` con una función mínima tipada (por ejemplo, `def saludar(nombre: str) -> str:`).
   - Crea `tests/test_core.py` importando esa función y validando su resultado con `assert`.
6. **Valida el entorno:** Ejecuta `uv run pytest -v` en la terminal y confirma que la prueba pase con estado `PASSED`.
7. **Entrega el resultado:** Muestra un resumen breve de los archivos creados y el comando exacto para correr pruebas en el futuro.
