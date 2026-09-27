#!/usr/bin/env bash
# Inicializa ASDD en un repo creado desde la plantilla asdd_template.
# Requiere GitHub CLI (gh) autenticado: gh auth login
set -euo pipefail

echo "→ Creando label asdd-bypass (si no existe)…"
gh label create asdd-bypass \
  --color B60205 \
  --description "Salta ASDD. Solo el responsable. Último recurso. Exige '## Motivo del bypass'." \
  2>/dev/null || echo "  (ya existía)"

echo "→ Dando permisos de ejecución a los hooks…"
chmod +x .claude/hooks/*.py .github/scripts/*.py

echo "→ Comprobando dependencias locales…"
command -v python3 >/dev/null && echo "  python3 OK" || echo "  ⚠ falta python3 (necesario para los hooks)"
command -v gh >/dev/null && echo "  gh OK" || echo "  ⚠ falta gh (necesario para que el guard detecte asdd-bypass)"

echo
echo "Listo. Pasos manuales recomendados en GitHub (Settings):"
echo "  1. Branches → regla de protección para 'main': Require a pull request + Require status checks → 'Agentic Spec-Driven Development'."
echo "  2. Revisa que Actions esté habilitado."
