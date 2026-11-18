---
trigger: always_on
---
# Reglas Base del Proyecto

## 1. Idioma y Estilo de Trabajo
- Responde siempre en español con explicaciones técnicas directas y sin relleno.
- Antes de crear archivos o modificar arquitectura, presenta siempre un **Implementation Plan** (`/plan`) y espera aprobación.
- Al finalizar cada tarea, entrega un **Walkthrough** breve con los comandos exactos para ejecutar y verificar los cambios.

## 2. Stack Técnico (macOS Apple Silicon)
- **Python y Entornos:** Usa `uv` para gestionar entornos virtuales y paquetes (`uv init`, `uv add`, `uv run`). Escribe Python 3 moderno con *type hints* estrictos y `pathlib` en lugar de `os.path`.
- **Interfaces Web (cuando aplique):** Prioriza HTML5, CSS limpio y JavaScript vanilla (o FastAPI/Flask ligero) sin frameworks pesados innecesarios. Diseña las interfaces en **Light Mode** por defecto, con alto contraste, jerarquía clara y estética minimalista funcional.
- **Multimedia y Sistema:** Si la app procesa audio, video o archivos locales, aprovecha herramientas nativas de macOS y aceleración por hardware cuando corresponda.

## 3. Estructura del Código
- Organiza el proyecto en `src/` (código principal), `tests/` (pruebas con `pytest`) y `scripts/` (utilidades).
- Mantén los módulos pequeños, desacoplados y fáciles de leer.
- Incluye siempre un `README.md` actualizado con pasos de instalación y uso.

## 4. Seguridad y Límites
- No ejecutes comandos destructivos (`rm -rf`, cambios fuera de la carpeta del proyecto) ni modifiques configuraciones globales sin confirmación explícita.
- Nunca escribas llaves API, tokens o contraseñas en el código; usa `.env` y agrégalo a `.gitignore`.
