"""Тесты построения графа зависимостей (этап 3)."""

import graph as graph_module
import repository


def build(tmp_path, text, root="A", depth=10):
    """Построить граф по текстовому описанию репозитория."""
    path = tmp_path / "repo.txt"
    path.write_text(text, encoding="utf-8")
    repo = repository.TestRepository(str(path))
    return graph_module.build(repo, root, depth)


def test_transitive_dependencies(tmp_path):
    """В граф попадают и косвенные зависимости."""
    built = build(tmp_path, "A: B\nB: C\nC:\n")
    assert built.nodes == ["A", "B", "C"]
    assert built.children("A") == ["B"]
    assert built.count_edges() == len(["A->B", "B->C"])


def test_depth_limit(tmp_path):
    """Глубина анализа ограничивает обход."""
    text = "A: B\nB: C\nC: D\nD:\n"
    assert build(tmp_path, text, depth=1).nodes == ["A", "B"]
    assert build(tmp_path, text, depth=2).nodes == ["A", "B", "C"]


def test_depth_recorded(tmp_path):
    """Для каждой вершины известна её глубина."""
    built = build(tmp_path, "A: B\nB: C\nC:\n")
    assert built.depth == {"A": 0, "B": 1, "C": 2}


def test_shared_dependency_once(tmp_path):
    """Общая зависимость появляется в графе один раз."""
    built = build(tmp_path, "A: B C\nB: D\nC: D\nD:\n")
    assert built.nodes.count("D") == len(["D"])
    assert built.count_edges() == len(
        ["A->B", "A->C", "B->D", "C->D"])


def test_cycle_does_not_hang(tmp_path):
    """Цикл не приводит к зацикливанию обхода."""
    built = build(tmp_path, "A: B\nB: C\nC: A\n")
    assert set(built.nodes) == {"A", "B", "C"}


def test_find_cycles(tmp_path):
    """Цикл находится и возвращается как список пакетов."""
    built = build(tmp_path, "A: B\nB: C\nC: A D\nD:\n")
    cycles = graph_module.find_cycles(built)
    assert cycles == [["A", "B", "C", "A"]]


def test_no_cycles(tmp_path):
    """В дереве без циклов циклы не находятся."""
    built = build(tmp_path, "A: B C\nB: D\nC: D\nD:\n")
    assert graph_module.find_cycles(built) == []


def test_self_loop(tmp_path):
    """Зависимость пакета от себя -- тоже цикл."""
    built = build(tmp_path, "A: A B\nB:\n")
    assert graph_module.find_cycles(built) == [["A", "A"]]


def test_missing_dependency(tmp_path):
    """Отсутствующий в репозитории пакет запоминается."""
    built = build(tmp_path, "A: B\n")
    assert "B" in built.missing
    assert built.children("B") == []
