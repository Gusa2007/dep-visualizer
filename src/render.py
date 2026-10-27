"""Представление графа зависимостей: Graphviz и ASCII-дерево."""

BRANCH = "├── "
LAST_BRANCH = "└── "
PIPE = "│   "
SPACE = "    "
CYCLE_MARK = " (цикл)"
REPEAT_MARK = " (...)"
INDENT = "    "


def escape(name):
    """Экранировать имя пакета для языка диаграмм."""
    return name.replace('"', '\\"')


def to_dot(graph):
    """Построить описание графа на языке Graphviz (DOT)."""
    lines = ["digraph dependencies {", f'{INDENT}rankdir="LR";',
             f'{INDENT}node [shape=box, fontname="Courier"];',
             f'{INDENT}"{escape(graph.root)}" [style=filled, '
             f'fillcolor="#d6e9c6"];']
    for parent in graph.nodes:
        if not graph.children(parent):
            lines.append(f'{INDENT}"{escape(parent)}";')
        for child in graph.children(parent):
            lines.append(
                f'{INDENT}"{escape(parent)}" -> "{escape(child)}";')
    lines.append("}")
    return "\n".join(lines)


def child_entries(graph, package, prefix, path, shown):
    """Подготовить строки-ветви для детей одного пакета.

    Возвращает список кортежей (пакет, префикс детей, путь, строка).
    Пакет из текущего пути помечается как цикл, уже показанный --
    как повтор; такие ветви дальше не раскрываются.
    """
    entries = []
    children = graph.children(package)
    for number, child in enumerate(children, start=1):
        last = number == len(children)
        connector = LAST_BRANCH if last else BRANCH
        mark = ""
        if child in path:
            mark = CYCLE_MARK
        elif child in shown:
            mark = REPEAT_MARK
        line = prefix + connector + child + mark
        child_prefix = prefix + (SPACE if last else PIPE)
        entries.append((None if mark else child, child_prefix,
                        path + (child,), line))
    return entries


def to_ascii(graph):
    """Построить ASCII-дерево зависимостей обходом без рекурсии."""
    lines = [graph.root]
    shown = {graph.root}
    stack = list(reversed(child_entries(
        graph, graph.root, "", (graph.root,), shown)))
    while stack:
        package, prefix, path, line = stack.pop()
        lines.append(line)
        if package is None:
            continue
        shown.add(package)
        stack.extend(reversed(child_entries(
            graph, package, prefix, path, shown)))
    return "\n".join(lines)
