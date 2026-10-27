#!/bin/sh
# Этап 4: порядок загрузки зависимостей и сравнение с apt.
cd "$(dirname "$0")/.." || exit 1
for name in test_simple test_cycle test_deep; do
    echo "== examples/$name.ini"
    ./run.sh --order --config "examples/$name.ini"
done
echo "== реальный пакет curl"
./run.sh --order --config examples/apt_curl.ini
echo "== для сравнения: apt-cache depends curl"
apt-cache depends curl 2>/dev/null || echo "apt-cache недоступен"
