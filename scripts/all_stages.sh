#!/bin/sh
# Последовательный запуск демонстраций всех этапов.
cd "$(dirname "$0")" || exit 1
for script in stage1_config.sh stage2_direct.sh stage3_graph.sh \
              stage4_order.sh stage5_visual.sh; do
    echo "######## $script"
    sh "./$script"
done
