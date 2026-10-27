"""Источники данных о зависимостях пакетов.

Два источника с одинаковым интерфейсом:

* :class:`AptRepository` -- реальный репозиторий Ubuntu: файл
  ``Packages`` (при необходимости сжатый gzip), который берётся
  по URL или из локального файла и разбирается вручную;
* :class:`TestRepository` -- текстовое описание графа, где пакеты
  названы большими латинскими буквами.

Готовые менеджеры пакетов и сторонние библиотеки не используются:
формат разбирается своим кодом.
"""

import gzip
import os
import urllib.error
import urllib.request

PACKAGE_FIELD = "Package:"
PROVIDES_FIELD = "Provides:"
DEPENDS_FIELDS = ("Depends:", "Pre-Depends:")
ALTERNATIVE = "|"
COMMENT = "#"
SEPARATOR = ":"
GZIP_MAGIC = b"\x1f\x8b"
TIMEOUT_SECONDS = 30
URL_PREFIXES = ("http://", "https://")


class RepositoryError(Exception):
    """Ошибка получения данных о зависимостях."""


def clean_dependency(item):
    """Очистить одну зависимость от версий и альтернатив.

    ``"libc6 (>= 2.34) | libc6-udeb"`` -> ``"libc6"``.
    """
    name = item.split(ALTERNATIVE)[0].strip()
    name = name.split("(")[0].strip()
    name = name.split("[")[0].strip()
    return name.split(SEPARATOR)[0].strip()


def parse_dependency_line(line):
    """Разобрать строку поля Depends в список имён пакетов."""
    names = []
    for item in line.split(","):
        name = clean_dependency(item)
        if name and name not in names:
            names.append(name)
    return names


def fetch_bytes(source):
    """Прочитать файл Packages по URL или из локального файла."""
    try:
        if source.startswith(URL_PREFIXES):
            with urllib.request.urlopen(
                    source, timeout=TIMEOUT_SECONDS) as response:
                data = response.read()
        else:
            with open(source, "rb") as file:
                data = file.read()
    except (urllib.error.URLError, OSError, ValueError) as exc:
        raise RepositoryError(
            f"не удалось получить данные из '{source}': {exc}") from exc
    if data[:len(GZIP_MAGIC)] == GZIP_MAGIC:
        return gzip.decompress(data)
    return data


class AptRepository:
    """Репозиторий Ubuntu: разбор файла Packages."""

    def __init__(self, source):
        """Запомнить URL или путь к файлу Packages."""
        self.source = source
        self.depends = {}
        self.provides = {}
        self.loaded = False

    def load(self):
        """Скачать и разобрать индекс пакетов (один раз)."""
        if self.loaded:
            return
        text = fetch_bytes(self.source).decode("utf-8", errors="replace")
        self._parse(text)
        self.loaded = True
        if not self.depends:
            raise RepositoryError(
                f"в '{self.source}' не найдено ни одного пакета")

    def _parse(self, text):
        """Разобрать текст индекса на пакеты и их зависимости."""
        name = None
        deps = []
        for line in text.splitlines():
            if not line.strip():
                self._store(name, deps)
                name, deps = None, []
            elif line.startswith(PACKAGE_FIELD):
                name = line[len(PACKAGE_FIELD):].strip()
            elif line.startswith(DEPENDS_FIELDS):
                deps.extend(parse_dependency_line(
                    line.split(SEPARATOR, 1)[1]))
            elif line.startswith(PROVIDES_FIELD) and name:
                self._store_provides(name, line)
        self._store(name, deps)

    def _store(self, name, deps):
        """Сохранить зависимости пакета, не теряя порядок."""
        if name and name not in self.depends:
            self.depends[name] = list(dict.fromkeys(deps))

    def _store_provides(self, name, line):
        """Запомнить виртуальные пакеты, которые даёт этот пакет."""
        for virtual in parse_dependency_line(
                line.split(SEPARATOR, 1)[1]):
            self.provides.setdefault(virtual, name)

    def resolve(self, package):
        """Вернуть настоящее имя пакета или ``None``."""
        self.load()
        if package in self.depends:
            return package
        return self.provides.get(package)

    def contains(self, package):
        """Есть ли такой пакет (или виртуальный пакет) в индексе."""
        return self.resolve(package) is not None

    def direct(self, package):
        """Прямые зависимости пакета."""
        real = self.resolve(package)
        if real is None:
            raise RepositoryError(
                f"пакет '{package}' не найден в репозитории")
        return list(self.depends[real])


class TestRepository:
    """Тестовый репозиторий: граф из текстового файла.

    Формат строки: ``A: B C`` или ``A: B, C``. Пустые строки и
    строки, начинающиеся с ``#``, пропускаются.
    """

    def __init__(self, path):
        """Прочитать описание графа из файла ``path``."""
        self.path = path
        self.depends = {}
        self._read()

    def _read(self):
        """Загрузить файл описания графа."""
        if not os.path.isfile(self.path):
            raise RepositoryError(
                f"файл тестового репозитория '{self.path}' не найден")
        with open(self.path, encoding="utf-8") as file:
            for number, line in enumerate(file, start=1):
                self._add_line(number, line)

    def _add_line(self, number, line):
        """Разобрать одну строку описания графа."""
        text = line.split(COMMENT)[0].strip()
        if not text:
            return
        if SEPARATOR not in text:
            raise RepositoryError(
                f"{self.path}, строка {number}: ожидается "
                f"'ПАКЕТ: ЗАВИСИМОСТИ'")
        name, _, rest = text.partition(SEPARATOR)
        names = [item for item in rest.replace(",", " ").split() if item]
        self.depends[name.strip()] = list(dict.fromkeys(names))

    def contains(self, package):
        """Есть ли пакет в описании графа."""
        return package in self.depends

    def direct(self, package):
        """Прямые зависимости пакета."""
        if package not in self.depends:
            raise RepositoryError(
                f"пакет '{package}' не найден в тестовом репозитории")
        return list(self.depends[package])


def create(config):
    """Создать источник данных по конфигурации."""
    if config.test_mode:
        return TestRepository(config.repository)
    return AptRepository(config.repository)
