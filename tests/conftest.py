"""Общие фикстуры тестов."""

import pytest

PACKAGES_SAMPLE = """Package: curl
Version: 8.5.0
Depends: libc6 (>= 2.34), libcurl4t64 (>= 8.0.0) | libcurl4, zlib1g

Package: libcurl4t64
Version: 8.5.0
Provides: libcurl4
Depends: libc6, zlib1g

Package: libc6
Version: 2.39

Package: zlib1g
Depends: libc6
"""

SIMPLE_GRAPH = """# простое дерево
A: B C
B: D
C: D E
D:
E:
"""


@pytest.fixture
def packages_file(tmp_path):
    """Локальный файл Packages в формате apt."""
    path = tmp_path / "Packages"
    path.write_text(PACKAGES_SAMPLE, encoding="utf-8")
    return str(path)


@pytest.fixture
def simple_repo(tmp_path):
    """Файл тестового репозитория с простым деревом."""
    path = tmp_path / "repo.txt"
    path.write_text(SIMPLE_GRAPH, encoding="utf-8")
    return str(path)


def write_ini(tmp_path, **values):
    """Создать INI-файл с заданными параметрами."""
    defaults = {
        "package": "A",
        "repository": str(tmp_path / "repo.txt"),
        "test_mode": "on",
        "ascii_tree": "on",
        "max_depth": "3",
    }
    defaults.update({key: str(value) for key, value in values.items()})
    lines = "\n".join(f"{key} = {value}"
                      for key, value in defaults.items())
    path = tmp_path / "config.ini"
    path.write_text(f"[visualizer]\n{lines}\n", encoding="utf-8")
    return str(path)
