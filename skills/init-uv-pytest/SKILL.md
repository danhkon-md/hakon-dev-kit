---
name: init-uv-pytest
description: Inicializa un proyecto Python moderno con uv, configura pytest como dependencia de desarrollo, crea la estructura src/, tests/ y scripts/, y ejecuta una prueba inicial de verificación. Úsala siempre que se pida crear, iniciar o estructurar un proyecto Python desde cero.
---

# Inicialización de Proyecto Python con uv y pytest

Ejecuta estos pasos en orden dentro de la raíz del workspace actual. Si un paso falla, detente, corrige y vuelve a intentarlo; no entregues un proyecto a medio configurar.

1. **Verifica herramientas**
   - Ejecuta `uv --version`. Se requiere uv ≥ 0.13.7.
   - Si no está instalado, detente e indica cómo hacerlo (`brew install uv` en macOS).

2. **Inicializa el proyecto sin sobrescribir**
   - Si ya existe `pyproject.toml`, no ejecutes `uv init`: salta al paso 3.
   - Ejecuta `uv init --no-workspace`. En uv ≥ 0.13 genera:
     - `.python-version`, `pyproject.toml` y `README.md` (solo si no existen)
     - `src/<nombre_del_proyecto>/__init__.py` con `main()` y una entrada en `[project.scripts]`
   - **No borres ni muevas ese paquete generado.** Es el paquete real del proyecto y `uv_build` falla si desaparece (`Expected a Python module at: src/<paquete>/__init__.py`).
   - Si necesitas un layout sin paquete generado, no borres la carpeta sin antes declarar el módulo en `pyproject.toml`:
     ```toml
     [tool.uv.build-backend]
     module-name = ["<paquete>"]
     ```

3. **Fija la versión de Python**
   - Conserva la versión que haya escrito `uv init` en `.python-version`.
   - Si no existe, ejecuta `uv python pin 3.12` (o la versión que pida el usuario) para que todo el equipo resuelva igual.

4. **Instala pytest como dependencia de desarrollo**
   - `uv add --dev pytest`
   - Confirma que `pyproject.toml` contiene un grupo `[dependency-groups]` con `dev = ["pytest>=..."]`.

5. **Crea la estructura estándar**
   - Asegura que existan `src/`, `tests/`, `scripts/` y un `tests/__init__.py` vacío.
   - Añade la configuración de pytest a `pyproject.toml`:
     ```toml
     [tool.pytest.ini_options]
     pythonpath = ["src"]
     testpaths = ["tests"]
     ```
   - Crea un `.gitignore` si no existe, con `.venv/`, `__pycache__/`, `*.py[cod]`, `.pytest_cache/`, `.env` y `.DS_Store`.

6. **Genera código y prueba base**
   - Crea `src/<paquete>/core.py` con una función mínima tipada:
     ```python
     def saludar(nombre: str) -> str:
         return f"¡Hola, {nombre}!"
     ```
   - Crea `tests/test_core.py` importando desde el paquete:
     ```python
     from <paquete>.core import saludar

     def test_saludar() -> None:
         assert saludar("Ana") == "¡Hola, Ana!"
     ```
   - No dejes `src/core.py` suelto: choca con el layout de paquete y con las reglas Python del kit.

7. **Valida el entorno**
   - Ejecuta `uv run pytest -v`.
   - Confirma `PASSED` y código de salida 0. Si falla, revisa imports y estructura antes de continuar.

8. **Cierra la tarea**
   - Actualiza `README.md` con instalación (`uv sync`), ejecución de pruebas (`uv run pytest -v`) y estructura del proyecto.
   - Entrega un resumen breve de los archivos creados y el comando exacto para correr pruebas en el futuro.
