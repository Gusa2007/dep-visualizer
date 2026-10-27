"""Точка входа: визуализатор графа зависимостей пакетов Ubuntu."""

import argparse
import sys

import config

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
    return parser.parse_args(argv)


def print_settings(settings):
    """Вывести все настраиваемые параметры (ключ-значение)."""
    print("Параметры конфигурации:")
    for line in settings.describe():
        print(f"  {line}")
    print(SEPARATOR)


def run(args):
    """Выполнить все шаги работы визуализатора."""
    settings = config.load(args.config)
    print_settings(settings)


def main(argv=None):
    """Запустить приложение и вернуть код завершения."""
    args = parse_args(argv)
    try:
        run(args)
    except config.ConfigError as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return EXIT_ERROR
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
