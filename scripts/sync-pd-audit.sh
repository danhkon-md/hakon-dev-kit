#!/usr/bin/env bash
# Sincroniza el paquete pd_audit desde el proyecto de origen al bundle del plugin.
# Uso:
#   ./scripts/sync-pd-audit.sh
#   PD_AUDIT_SRC=/otra/ruta/src/pd_audit ./scripts/sync-pd-audit.sh
set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="${PD_AUDIT_SRC:-$HOME/Proyectos/mi-primera-app/src/pd_audit}"
DEST="$PLUGIN_ROOT/servers/pd-audit/src/pd_audit"

if [[ ! -d "$SRC" ]]; then
  echo "error: no existe el origen: $SRC" >&2
  echo "Define PD_AUDIT_SRC con la ruta correcta." >&2
  exit 1
fi

if ! command -v rsync >/dev/null 2>&1; then
  echo "error: rsync no está instalado." >&2
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "error: uv no está instalado." >&2
  exit 1
fi

mkdir -p "$DEST"
rsync -a --delete \
  --exclude '__pycache__/' \
  --exclude '*.py[cod]' \
  "$SRC"/ "$DEST"/

echo "Sincronizado: $SRC -> $DEST"

(
  cd "$PLUGIN_ROOT/servers/pd-audit"
  uv lock
)

if command -v agy >/dev/null 2>&1; then
  (
    cd "$PLUGIN_ROOT"
    agy plugin validate --strict .
  )
else
  echo "aviso: agy no está en PATH; se omite la validación." >&2
fi

echo "OK: bundle actualizado y lock regenerado."
