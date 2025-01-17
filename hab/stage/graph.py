from collections import defaultdict
from ..util.decs import as_list
from ..util.log import Log

_log = Log('dependency')

class CircularDependencyError(Exception):
    pass

class Node:
    def __init__(self, id):
        self.id = id
        self._dependencies = []

    @property
    def rank(self):
        if self.dependencies:
            return max(d.rank for d in self.dependencies) + 1
        return 0

    def add_dependency(self, node):
        if node not in self._dependencies:
            self._dependencies.append(node)

    @property
    def dependencies(self):
        return self._dependencies

    def __repr__(self):
        return f'<Node: {self.id} deps: {", ".join(d.id for d in self._dependencies)}>'


class DependencyGraph:
    def __init__(self):
        self._nodes = defaultdict(list)

    def _build_nodes(self):
        nodes = { id: Node(id) for id in self._nodes.keys() }
        for parent, node in nodes.items():
            for child in self._nodes[parent]:
                node.add_dependency(nodes.get(child))
        return nodes

    @property
    def nodes(self):
        return self._build_nodes()

    def _has_constaint(self, parent, child, deep=False, root=None):
        if parent is root:
            raise CircularDependencyError('%s can not be a dependency of %s!', parent, child)
        if child in self._nodes[parent]:
            return True
        if not deep:
            return False
        root = root if root is not None else parent
        for sub in self._nodes[parent]:
            if self._has_constaint(sub, child, deep=deep, root=root):
                return True
        return False

    def add_constraint(self, parent, child):
        _log.debug(f'Adding constraint {parent} -> {child}')
        if not self._has_constaint(parent, child, deep=True):
            self._nodes[parent].append(child)
            if child not in self._nodes:
                self._nodes[child] = []
            return True
        return False

    def _rank_nodes(self, nodes, lvl=0):
        for node in nodes:
            node.rank = lvl
            self._rank_nodes(node.dependencies, lvl + 1)

    def _build_layers(self, nodes):
        layers = defaultdict(list)
        for node in nodes:
            layers[node.rank].append(node)
        return layers

    def build_layers(self):
        nodes = self._build_nodes()
        layers = self._build_layers(nodes.values())
        return [ v for k, v in sorted(layers.items(), key=lambda l: l[0])]
