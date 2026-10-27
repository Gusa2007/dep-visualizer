"""Чтение и проверка конфигурационного файла формата INI.

Все настраиваемые пользователем параметры задаются в INI-файле,
секция ``[visualizer]``. Любая ошибка (нет файла, нет секции,
нет обязательного параметра, неверное значение) сообщается
исключением :class:`ConfigError` с понятным текстом.
"""

import configparser
import os
from dataclasses import dataclass

SECTION = "visualizer"
PACKAGE = "package"
REPOSITORY = "repository"
TEST_MODE = "test_mode"
ASCII_TREE = "ascii_tree"
MAX_DEPTH = "max_depth"
REQUIRED = (PACKAGE, REPOSITORY, TEST_MODE, ASCII_TREE, MAX_DEPTH)
TRUE_VALUES = ("1", "on", "true", "yes", "да")
FALSE_VALUES = ("0", "off", "false", "no", "нет")
MIN_DEPTH = 1
URL_PREFIXES = ("http://", "https://")


class ConfigError(Exception):
    """Ошибка конфигурационного файла."""


@dataclass(frozen=True)
class Config:
    """Параметры работы визуализатора."""

    package: str
    repository: str
    test_mode: bool
    ascii_tree: bool
    max_depth: int

    def describe(self):
        """Вернуть параметры в формате ключ-значение."""
        return [
            f"{PACKAGE} = {self.package}",
            f"{REPOSITORY} = {self.repository}",
            f"{TEST_MODE} = {on_off(self.test_mode)}",
            f"{ASCII_TREE} = {on_off(self.ascii_tree)}",
            f"{MAX_DEPTH} = {self.max_depth}",
        ]


def on_off(value):
    """Представить логическое значение как on или off."""
    return "on" if value else "off"


def parse_bool(key, text):
    """Разобрать логический параметр (on/off, true/false, 1/0)."""
    value = text.strip().lower()
    if value in TRUE_VALUES:
        return True
    if value in FALSE_VALUES:
        return False
    raise ConfigError(
        f"параметр '{key}': ожидается on или off, получено '{text}'")


def parse_depth(text):
    """Разобрать максимальную глубину анализа."""
    try:
        depth = int(text.strip())
    except ValueError as exc:
        raise ConfigError(
            f"параметр '{MAX_DEPTH}': ожидается целое число, "
            f"получено '{text}'") from exc
    if depth < MIN_DEPTH:
        raise ConfigError(
            f"параметр '{MAX_DEPTH}': глубина должна быть не меньше "
            f"{MIN_DEPTH}, получено {depth}")
    return depth


def check_repository(repository, test_mode):
    """Проверить путь к тестовому репозиторию или URL."""
    if test_mode:
        if not os.path.isfile(repository):
            raise ConfigError(
                f"параметр '{REPOSITORY}': файл тестового репозитория "
                f"'{repository}' не найден")
        return
    if repository.startswith(URL_PREFIXES):
        return
    if not os.path.isfile(repository):
        raise ConfigError(
            f"параметр '{REPOSITORY}': ожидается URL или путь к файлу "
            f"Packages, получено '{repository}'")


def read_section(path):
    """Прочитать секцию визуализатора из INI-файла."""
    if not os.path.isfile(path):
        raise ConfigError(f"файл конфигурации '{path}' не найден")
    parser = configparser.ConfigParser(inline_comment_prefixes=(";", "#"))
    try:
        parser.read(path, encoding="utf-8")
    except configparser.Error as exc:
        raise ConfigError(f"не удалось разобрать '{path}': {exc}") from exc
    if not parser.has_section(SECTION):
        raise ConfigError(f"в файле '{path}' нет секции [{SECTION}]")
    section = parser[SECTION]
    missing = [key for key in REQUIRED if key not in section]
    if missing:
        raise ConfigError(
            f"в секции [{SECTION}] не хватает параметров: "
            f"{', '.join(missing)}")
    return section


def load(path):
    """Загрузить конфигурацию из INI-файла ``path``."""
    section = read_section(path)
    package = section[PACKAGE].strip()
    if not package:
        raise ConfigError(f"параметр '{PACKAGE}': имя пакета не задано")
    repository = section[REPOSITORY].strip()
    test_mode = parse_bool(TEST_MODE, section[TEST_MODE])
    check_repository(repository, test_mode)
    return Config(
        package=package,
        repository=repository,
        test_mode=test_mode,
        ascii_tree=parse_bool(ASCII_TREE, section[ASCII_TREE]),
        max_depth=parse_depth(section[MAX_DEPTH]),
    )
