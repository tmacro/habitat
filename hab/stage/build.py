from .stage import Stage
from ..error import InvalidModuleError
from .graph import DependencyGraph
from ..util.decs import as_list
from ..util.log import Log

_log = Log('stage.graph')

def _inferred_dependencies(targets):
    _log.debug('Inferring module dependencies...')
    _log.debug('Building output variable index...')
    output_vars = {}
    for target in set(targets.values()):
        for tfvar in target.module.output_variables:
            output_vars[tfvar] = target.provides
    for target in set(targets.values()):
        for tfvar in target.module.input_variables:
            if tfvar in output_vars:
                _log.debug(f'Matched {tfvar} from {target.name} with {output_vars[tfvar]}')
                yield target.provides, output_vars[tfvar]

def _explicit_dependencies(targets):
    _log.debug('Adding dependencies from habfile...')
    for target in set(targets.values()):
        for child in target.module.depends_on:
            if child not in targets:
                raise InvalidModuleError(target.module.name)
            _log.debug(f'Adding {targets[child].name} as a dependency of {target.name}')
            yield target.provides, targets[child].provides

def _build_graph(targets):
    _log.debug('Building dependency graph...')
    graph = DependencyGraph()
    for parent, child in _explicit_dependencies(targets):
        graph.add_constraint(parent, child)
    for parent, child in _inferred_dependencies(targets):
        graph.add_constraint(parent, child)
    return graph

@as_list
def build_stages(targets, biome):
    graph = _build_graph(targets)
    _log.debug('Building stages...')
    for layer in graph.build_layers():
        _targets = [ targets[t.id] for t in layer ]
        _log.debug(f'Built stage with targets: {", ".join(t.name for t in _targets)}')
        yield Stage(_targets, biome)
