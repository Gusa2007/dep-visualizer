#!/bin/sh
# Этап 5: визуализация графа для трёх пакетов и сравнение с apt.
cd "$(dirname "$0")/.." || exit 1
for name in apt_curl apt_nano apt_git; do
    echo "== examples/$name.ini"
    ./run.sh --config "examples/$name.ini"
done
echo "== тестовые репозитории"
./run.sh --config examples/test_cycle.ini
echo "== для сравнения: apt-cache dotty curl"
apt-cache dotty curl 2>/dev/null | head -10 || echo "apt-cache недоступен"
