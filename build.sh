#!/bin/bash
set -e

VENV=".venv"

if [ ! -d "$VENV" ]; then
  echo "Creando entorno virtual..."
  python3 -m venv "$VENV"
fi

source "$VENV/bin/activate"
python generate_site.py
