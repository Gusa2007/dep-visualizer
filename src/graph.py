"""Построение графа зависимостей и операции над ним.

Граф строится обходом в ширину (BFS) без рекурсии, с учётом
максимальной глубины. Циклические зависимости не приводят к
зацикливанию: каждый пакет обрабатывается один раз, а сами циклы
находятся отдельно и выводятся пользователю.
"""

from collections import deque

from repository import RepositoryError

ROOT_DEPTH = 0
WHITE, GREY, BLACK = 0, 1, 2


class Graph:
    """Граф зависимостей: вершины-пакеты и рёбра-зависимости."""

    def __init__(self, root):
        """Создать граф с корневым пакетом ``root``."""
        self.root = root
        self.edges = {root: []}
        self.depth = {root: ROOT_DEPTH}
        self.missing = {}

    @property
    def nodes(self):
        """Список вершин в порядке появления."""
        return list(self.edges)

    def children(self, package):
        """Прямые зависимости пакета внутри графа."""
        return self.edges.get(package, [])

    def add_edge(self, parent, child, depth):
        """Добавить ребро parent -> child."""
        if child not in self.edges[parent]:
            self.edges[parent].append(child)
        if child not in self.edges:
            self.edges[child] = []
            self.depth[child] = depth
            return True
        return False

    def count_edges(self):
        """Общее число рёбер графа."""
        return sum(len(children) for children in self.edges.values())


def build(repo, root, max_depth):
    """Построить граф зависимостей пакета ``root`` обходом в ширину."""
    graph = Graph(root)
    queue = deque([(root, ROOT_DEPTH)])
    while queue:
        package, depth = queue.popleft()
        if depth >= max_depth:
            continue
        for child in dependencies(repo, graph, package):
            if graph.add_edge(package, child, depth + 1):
                queue.append((child, depth + 1))
    return graph


def dependencies(repo, graph, package):
    """Прямые зависимости пакета; отсутствующие запоминаются."""
    try:
        return repo.direct(package)
    except RepositoryError as exc:
        graph.missing[package] = str(exc)
        return []


def find_cycles(graph):
    """Найти циклы обходом в глубину без рекурсии.

    Возвращает список циклов; каждый цикл -- список пакетов,
    где последний элемент совпадает с первым.
    """
    color = {node: WHITE for node in graph.nodes}
    cycles = []
    for start in graph.nodes:
        if color[start] != WHITE:
            continue
        stack = [(start, iter(graph.children(start)))]
        color[start] = GREY
        path = [start]
        walk(graph, stack, path, color, cycles)
    return cycles


def walk(graph, stack, path, color, cycles):
    """Один проход обхода в глубину для поиска циклов."""
    while stack:
        node, children = stack[-1]
        child = next(children, None)
        if child is None:
            color[node] = BLACK
            stack.pop()
            path.pop()
            continue
        if color.get(child) == GREY:
            cycles.append(path[path.index(child):] + [child])
        elif color.get(child) == WHITE:
            color[child] = GREY
            path.append(child)
            stack.append((child, iter(graph.children(child))))


def install_order(graph):
    """Порядок загрузки: зависимости раньше зависящих пакетов.

    Используется алгоритм Кана. Если из-за цикла ни один пакет не
    готов, цикл разрывается: берётся самый глубокий из оставшихся
    пакетов, при равной глубине -- первый по алфавиту.
    Возвращает пару (порядок, список разорванных пакетов).
    """
    waiting = {node: set(graph.children(node)) for node in graph.nodes}
    order = []
    broken = []
    while waiting:
        ready = sorted(name for name, deps in waiting.items() if not deps)
        if not ready:
            ready = [deepest(graph, waiting)]
            broken.append(ready[0])
        for name in ready:
            order.append(name)
            del waiting[name]
        for deps in waiting.values():
            deps.difference_update(ready)
    return order, broken


def deepest(graph, waiting):
    """Самый глубокий из оставшихся пакетов (для разрыва цикла)."""
    return sorted(waiting, key=lambda name: (-graph.depth[name], name))[0]
