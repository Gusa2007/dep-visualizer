#!/bin/sh
# Этап 3: граф зависимостей на разных тестовых репозиториях.
cd "$(dirname "$0")/.." || exit 1
for name in test_single test_simple test_cycle test_deep; do
    echo "== examples/$name.ini"
    ./run.sh --config "examples/$name.ini"
done
echo "== реальный репозиторий"
./run.sh --config examples/apt_curl.ini
