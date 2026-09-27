#!/usr/bin/env bash
# Envoltorio de scripts/asdd_verify.py. Uso: ./scripts/asdd-verify.sh <feature> <TXX> -- <comando>
exec python3 "$(dirname "$0")/asdd_verify.py" "$@"
