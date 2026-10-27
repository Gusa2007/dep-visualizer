#!/bin/sh
# Этап 2: прямые зависимости пакетов из репозитория Ubuntu.
cd "$(dirname "$0")/.." || exit 1
for name in apt_curl apt_nano apt_git; do
    echo "== examples/$name.ini"
    ./run.sh --config "examples/$name.ini"
done
echo "== тестовый репозиторий"
./run.sh --config examples/test_simple.ini
