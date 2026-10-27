"""Точка входа: визуализатор графа зависимостей пакетов Ubuntu."""

import argparse
import sys

import config
import graph as graph_module
import render
import repository

DEFAULT_CONFIG = "examples/test_simple.ini"
EXIT_OK = 0
EXIT_ERROR = 1
SEPARATOR = "-" * 60


def parse_args(argv=None):
    """Разобрать аргументы командной строки."""
    parser = argparse.ArgumentParser(
        prog="dep-visualizer",
        description="Визуализатор графа зависимостей пакетов Ubuntu")
    parser.add_argument(
        "--config", default=DEFAULT_CONFIG, metavar="PATH",
        help=f"путь к INI-файлу конфигурации (по умолчанию "
             f"{DEFAULT_CONFIG})")
    parser.add_argument(
        "--order", action="store_true",
        help="вывести порядок загрузки зависимостей")
    return parser.parse_args(argv)


def print_settings(settings):
    """Вывести все настраиваемые параметры (ключ-значение)."""
    print("Параметры конфигурации:")
    for line in settings.describe():
        print(f"  {line}")
    print(SEPARATOR)


def print_direct(repo, settings):
    """Вывести прямые зависимости заданного пакета."""
    direct = repo.direct(settings.package)
    print(f"Прямые зависимости пакета '{settings.package}' "
          f"({len(direct)}):")
    for name in direct:
        print(f"  {name}")
    print(SEPARATOR)


def print_graph_info(built):
    """Вывести размер графа, циклы и ненайденные пакеты."""
    print(f"Граф: вершин {len(built.nodes)}, "
          f"рёбер {built.count_edges()}")
    for cycle in graph_module.find_cycles(built):
        print("Цикл: " + " -> ".join(cycle))
    for name, reason in built.missing.items():
        print(f"Пропущено: {reason}")
    print(SEPARATOR)


def print_order(built):
    """Вывести порядок загрузки зависимостей."""
    order, broken = graph_module.install_order(built)
    print("Порядок загрузки (зависимости раньше зависящих):")
    for number, name in enumerate(order, start=1):
        print(f"  {number:>3}. {name}")
    if broken:
        print("Циклы разорваны на пакетах: " + ", ".join(broken))
    print(SEPARATOR)


def print_views(built, settings):
    """Вывести описание графа и, если задано, ASCII-дерево."""
    print("Описание графа на языке Graphviz:")
    print(render.to_dot(built))
    print(SEPARATOR)
    if settings.ascii_tree:
        print("Дерево зависимостей:")
        print(render.to_ascii(built))
        print(SEPARATOR)


def run(args):
    """Выполнить все шаги работы визуализатора."""
    settings = config.load(args.config)
    print_settings(settings)
    repo = repository.create(settings)
    print_direct(repo, settings)
    built = graph_module.build(repo, settings.package,
                               settings.max_depth)
    print_graph_info(built)
    if args.order:
        print_order(built)
    print_views(built, settings)


def main(argv=None):
    """Запустить приложение и вернуть код завершения."""
    args = parse_args(argv)
    try:
        run(args)
    except (config.ConfigError, repository.RepositoryError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return EXIT_ERROR
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
