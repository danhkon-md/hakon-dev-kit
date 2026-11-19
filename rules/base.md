---
trigger: always_on
---
# Flujo General de Trabajo

## Idioma y estilo
- Responde siempre en español, con explicaciones técnicas directas y sin relleno.

## Antes de editar
- Antes de crear archivos o modificar la arquitectura, presenta un **Implementation Plan** y espera aprobación explícita.

## Al cerrar una tarea
- Entrega un **Walkthrough** breve: qué cambió, por qué, y los comandos exactos para ejecutarlo y verificarlo.

## Límites
- No ejecutes comandos destructivos (`rm -rf`, cambios fuera de la carpeta del proyecto) ni modifiques configuraciones globales sin confirmación explícita.
- Nunca escribas llaves API, tokens o contraseñas en el código; usa `.env` y agrégalo a `.gitignore`.
