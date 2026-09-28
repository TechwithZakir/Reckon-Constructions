from collections import defaultdict


def validate_date_range(start_date, end_date):
    if start_date and end_date and end_date < start_date:
        raise ValueError("Planned End Date cannot be before Planned Start Date.")


def has_dependency_cycle(edges):
    graph = defaultdict(list)
    nodes = set()
    for source, target in edges:
        if not source or not target:
            continue
        graph[source].append(target)
        nodes.add(source)
        nodes.add(target)

    visiting = set()
    visited = set()

    def visit(node):
        if node in visiting:
            return True
        if node in visited:
            return False

        visiting.add(node)
        for child in graph[node]:
            if visit(child):
                return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in nodes)
