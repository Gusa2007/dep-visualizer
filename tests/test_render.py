"""Тесты визуализации графа (этап 5)."""

import render
from test_graph import build


def test_dot_header_and_edges(tmp_path):
    """Описание на языке Graphviz содержит рёбра графа."""
    built = build(tmp_path, "A: B\nB:\n")
    text = render.to_dot(built)
    assert text.startswith("digraph dependencies {")
    assert '"A" -> "B";' in text
    assert text.rstrip().endswith("}")


def test_dot_lists_leaf_nodes(tmp_path):
    """Вершины без зависимостей тоже попадают в описание."""
    built = build(tmp_path, "A: B\nB:\n")
    assert '"B";' in render.to_dot(built)


def test_ascii_tree(tmp_path):
    """ASCII-дерево отражает структуру зависимостей."""
    built = build(tmp_path, "A: B C\nB: D\nC:\nD:\n")
    assert render.to_ascii(built).splitlines() == [
        "A",
        "├── B",
        "│   └── D",
        "└── C",
    ]


def test_ascii_marks_repeat(tmp_path):
    """Повторная зависимость помечается и не раскрывается."""
    built = build(tmp_path, "A: B C\nB: D\nC: D\nD:\n")
    lines = render.to_ascii(built).splitlines()
    assert lines[-1].endswith("D (...)")


def test_ascii_marks_cycle(tmp_path):
    """Цикл помечается в дереве."""
    built = build(tmp_path, "A: B\nB: A\n")
    assert render.to_ascii(built).splitlines()[-1].endswith("A (цикл)")


def test_escape_quotes(tmp_path):
    """Кавычки в имени пакета экранируются."""
    assert render.escape('a"b') == 'a\\"b'
