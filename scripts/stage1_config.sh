#!/bin/sh
# Этап 1: вывод всех параметров конфигурации и обработка ошибок.
cd "$(dirname "$0")/.." || exit 1
for name in test_simple test_cycle test_deep test_single; do
    echo "== examples/$name.ini"
    ./run.sh --config "examples/$name.ini"
done
echo "== ошибки конфигурации =="
for name in bad_depth bad_mode bad_missing bad_repo; do
    echo "-- examples/$name.ini"
    ./run.sh --config "examples/$name.ini"
done
echo "-- несуществующий файл"
./run.sh --config examples/none.ini
