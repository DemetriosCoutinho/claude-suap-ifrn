#!/usr/bin/env bash
# Verifica e instala dependências Python do plugin claude-suap-ifrn.
# Idempotente: só roda pip se algum import falhar.
set -e

PLUGIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if ! python3 -c "import pypdf, playwright, keyring" 2>/dev/null; then
  echo "[claude-suap-ifrn] Instalando dependências Python..."
  if command -v uv >/dev/null 2>&1; then
    uv pip install -r "$PLUGIN_DIR/requirements.txt"
  else
    python3 -m pip install -r "$PLUGIN_DIR/requirements.txt"
  fi
fi

# Verifica se o browser Chromium do Playwright está disponível
if ! python3 -m playwright install --dry-run chromium 2>/dev/null | grep -q "chromium"; then
  echo "[claude-suap-ifrn] Instalando Chromium para Playwright..."
  python3 -m playwright install chromium
fi
