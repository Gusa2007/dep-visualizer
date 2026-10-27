"""Тесты порядка загрузки зависимостей (этап 4)."""

import graph as graph_module
from test_graph import build


def test_dependencies_first(tmp_path):
    """Зависимости идут раньше зависящих пакетов."""
    built = build(tmp_path, "A: B C\nB: D\nC: D E\nD:\nE:\n")
    order, broken = graph_module.install_order(built)
    assert broken == []
    assert order.index("D") < order.index("B")
    assert order.index("B") < order.index("A")
    assert order[-1] == "A"


def test_order_contains_all_nodes(tmp_path):
    """В порядке загрузки есть все вершины графа и без повторов."""
    built = build(tmp_path, "A: B C\nB: D\nC: D\nD:\n")
    order, _ = graph_module.install_order(built)
    assert sorted(order) == sorted(built.nodes)
    assert len(order) == len(set(order))


def test_cycle_is_broken(tmp_path):
    """Цикл разрывается, порядок всё равно строится."""
    built = build(tmp_path, "A: B\nB: C\nC: A\n")
    order, broken = graph_module.install_order(built)
    assert sorted(order) == ["A", "B", "C"]
    assert len(broken) == len(["разорванный пакет"])


def test_single_package(tmp_path):
    """Пакет без зависимостей: порядок из одного элемента."""
    built = build(tmp_path, "A:\n")
    assert graph_module.install_order(built) == (["A"], [])
