#!/bin/sh
# Запуск визуализатора. Все аргументы передаются приложению.
cd "$(dirname "$0")" || exit 1
PYTHON="${PYTHON:-python3}"
exec "$PYTHON" src/main.py "$@"
