"""Тесты конфигурационного файла INI (этап 1)."""

import pytest

import config
from conftest import write_ini


def test_load_valid(tmp_path, simple_repo):
    """Корректный файл читается, значения разбираются."""
    depth = 4
    path = write_ini(tmp_path, repository=simple_repo, max_depth=depth,
                     ascii_tree="off")
    settings = config.load(path)
    assert settings.package == "A"
    assert settings.repository == simple_repo
    assert settings.test_mode is True
    assert settings.ascii_tree is False
    assert settings.max_depth == depth


def test_describe_lists_all_parameters(tmp_path, simple_repo):
    """Вывод ключ-значение содержит все параметры."""
    settings = config.load(write_ini(tmp_path, repository=simple_repo))
    text = "\n".join(settings.describe())
    for key in config.REQUIRED:
        assert key in text
    assert "test_mode = on" in text


def test_missing_file(tmp_path):
    """Несуществующий файл конфигурации -- ошибка."""
    with pytest.raises(config.ConfigError, match="не найден"):
        config.load(str(tmp_path / "none.ini"))


def test_missing_section(tmp_path):
    """Файл без секции [visualizer] -- ошибка."""
    path = tmp_path / "c.ini"
    path.write_text("[other]\nx = 1\n", encoding="utf-8")
    with pytest.raises(config.ConfigError, match="нет секции"):
        config.load(str(path))


def test_missing_keys(tmp_path):
    """Нехватка обязательных параметров -- ошибка со списком."""
    path = tmp_path / "c.ini"
    path.write_text("[visualizer]\npackage = A\n", encoding="utf-8")
    with pytest.raises(config.ConfigError, match="не хватает"):
        config.load(str(path))


def test_empty_package(tmp_path, simple_repo):
    """Пустое имя пакета -- ошибка."""
    path = write_ini(tmp_path, repository=simple_repo, package="")
    with pytest.raises(config.ConfigError, match="имя пакета"):
        config.load(path)


@pytest.mark.parametrize("value", ["maybe", "", "2"])
def test_bad_bool(tmp_path, simple_repo, value):
    """Неверное значение режима -- ошибка."""
    path = write_ini(tmp_path, repository=simple_repo, test_mode=value)
    with pytest.raises(config.ConfigError, match="ожидается on или off"):
        config.load(path)


@pytest.mark.parametrize("value, message", [
    ("ноль", "целое число"),
    ("0", "не меньше"),
    ("-2", "не меньше"),
])
def test_bad_depth(tmp_path, simple_repo, value, message):
    """Неверная глубина анализа -- ошибка."""
    path = write_ini(tmp_path, repository=simple_repo, max_depth=value)
    with pytest.raises(config.ConfigError, match=message):
        config.load(path)


def test_missing_test_repository(tmp_path):
    """Нет файла тестового репозитория -- ошибка."""
    path = write_ini(tmp_path, repository=str(tmp_path / "none.txt"))
    with pytest.raises(config.ConfigError, match="тестового репозитория"):
        config.load(path)


def test_url_accepted(tmp_path):
    """В обычном режиме URL принимается без проверки файла."""
    path = write_ini(tmp_path, test_mode="off",
                     repository="http://example.org/Packages.gz")
    assert config.load(path).repository.startswith("http://")


def test_bad_source_without_url(tmp_path):
    """Не URL и не существующий файл -- ошибка."""
    path = write_ini(tmp_path, test_mode="off", repository="nope.gz")
    with pytest.raises(config.ConfigError, match="ожидается URL"):
        config.load(path)
