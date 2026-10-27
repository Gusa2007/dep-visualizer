"""Тесты источников данных о зависимостях (этап 2)."""

import gzip

import pytest

import repository


@pytest.mark.parametrize("item, expected", [
    ("libc6 (>= 2.34)", "libc6"),
    ("libcurl4t64 | libcurl4", "libcurl4t64"),
    ("python3:any", "python3"),
    ("gcc [amd64]", "gcc"),
    ("  zlib1g  ", "zlib1g"),
])
def test_clean_dependency(item, expected):
    """Версии, альтернативы и архитектуры отбрасываются."""
    assert repository.clean_dependency(item) == expected


def test_parse_dependency_line():
    """Строка Depends разбирается в список имён без повторов."""
    line = " libc6 (>= 2.34), libssl3 | libssl1.1, libc6"
    assert repository.parse_dependency_line(line) == ["libc6", "libssl3"]


def test_apt_direct(packages_file):
    """Прямые зависимости пакета читаются из файла Packages."""
    repo = repository.AptRepository(packages_file)
    assert repo.direct("curl") == ["libc6", "libcurl4t64", "zlib1g"]
    assert repo.direct("libc6") == []


def test_apt_virtual_package(packages_file):
    """Виртуальный пакет из поля Provides находится."""
    repo = repository.AptRepository(packages_file)
    assert repo.contains("libcurl4")
    assert repo.direct("libcurl4") == ["libc6", "zlib1g"]


def test_apt_unknown_package(packages_file):
    """Неизвестный пакет -- ошибка."""
    repo = repository.AptRepository(packages_file)
    with pytest.raises(repository.RepositoryError, match="не найден"):
        repo.direct("nope")


def test_apt_gzip(tmp_path, packages_file):
    """Сжатый gzip индекс распаковывается автоматически."""
    with open(packages_file, "rb") as file:
        data = file.read()
    path = tmp_path / "Packages.gz"
    path.write_bytes(gzip.compress(data))
    repo = repository.AptRepository(str(path))
    assert repo.direct("curl") == ["libc6", "libcurl4t64", "zlib1g"]


def test_apt_bad_source(tmp_path):
    """Недоступный источник -- ошибка."""
    repo = repository.AptRepository(str(tmp_path / "none.gz"))
    with pytest.raises(repository.RepositoryError, match="не удалось"):
        repo.load()


def test_apt_empty_index(tmp_path):
    """Пустой индекс -- ошибка."""
    path = tmp_path / "Packages"
    path.write_text("", encoding="utf-8")
    repo = repository.AptRepository(str(path))
    with pytest.raises(repository.RepositoryError, match="ни одного"):
        repo.load()


def test_test_repository(simple_repo):
    """Тестовый репозиторий читает граф из файла."""
    repo = repository.TestRepository(simple_repo)
    assert repo.direct("A") == ["B", "C"]
    assert repo.direct("D") == []
    assert repo.contains("E")


def test_test_repository_unknown(simple_repo):
    """Неизвестный пакет тестового репозитория -- ошибка."""
    repo = repository.TestRepository(simple_repo)
    with pytest.raises(repository.RepositoryError, match="не найден"):
        repo.direct("Z")


def test_test_repository_bad_line(tmp_path):
    """Строка без двоеточия -- ошибка с номером строки."""
    path = tmp_path / "repo.txt"
    path.write_text("A: B\nплохая строка\n", encoding="utf-8")
    with pytest.raises(repository.RepositoryError, match="строка 2"):
        repository.TestRepository(str(path))


def test_create_by_config(simple_repo, packages_file):
    """Источник выбирается по режиму из конфигурации."""
    class Fake:
        """Минимальная замена конфигурации."""

        def __init__(self, repo, mode):
            """Запомнить путь и режим."""
            self.repository = repo
            self.test_mode = mode

    assert isinstance(repository.create(Fake(simple_repo, True)),
                      repository.TestRepository)
    assert isinstance(repository.create(Fake(packages_file, False)),
                      repository.AptRepository)
