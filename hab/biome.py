from .error import (AmbiguousProvidesError, InvalidBiomeError,
                    InvalidModuleError)
from .dependency import DependencyGraph
from .stage import Target, Stage
from .util.decs import as_list
from .tfvars import TFVars
from .util.type import is_iterable, is_string
from .util.log import Log

_log = Log('biome')

class Biome:
    def __init__(self, name, env, start_at=None, stop_at=None):
        self.name = name
        self._env = env
        self._habfile = None
        self._targets = None
        self.__modules = None
        self._stages = None
        self._start_at = start_at
        self._stop_at = stop_at
        if not self._has_biome:
            raise InvalidBiomeError(self.name)

    @property
    def env(self):
        return self._env

    @property
    def _has_biome(self):
        _log.debug('Checking for biome existence')
        return self.name in [b.name for b in self._env.habfile.biomes]

    def _load_modules(self):
        biomes_modules = {}
        _log.debug('Selecting biome modules...')
        for biome in self._env.habfile.biomes:
            if biome.name == self.name:
                for name in biome.modules:
                    if name not in self._env.modules:
                        raise InvalidModuleError(name)
                    _log.debug(f'Selected module {name}')
                    biomes_modules[name] = self._env.modules[name]
                break
        return biomes_modules

    @property
    def _modules(self):
        if self.__modules is None:
            self.__modules = self._load_modules()
        return self.__modules

    def _build_targets(self):
        _log.debug('Building targets...')
        targets = {}
        for module in self._modules.values():
            if is_iterable(module.provides):
                _log.debug(f'Module {module.name} provides multiple targets')
                for provider in module.provides:
                    if provider in targets:
                        raise AmbiguousProvidesError(
                                module.name,
                                targets[provider].module.name,
                                provider
                            )
                    _log.debug(f'- Added Target {provider} from {module.name}')
                    targets[provider] = Target(provider, module)
                    targets[targets[provider].id] = targets[provider]
            elif is_string(module.provides):
                if module.provides in targets:
                    raise AmbiguousProvidesError(
                            module.name,
                            targets[module.provides].module.name,
                            module.provides
                        )
                _log.debug(f'Added Target {module.provides} from {module.name}')
                targets[module.provides] = Target(module.provides, module)
                targets[targets[module.provides].id] = targets[module.provides]
        return targets

    @property
    def targets(self):
        if self._targets is None:
            self._targets = self._build_targets()
        return self._targets

    def _inferred_dependencies(self):
        _log.debug('Inferring module dependencies...')
        _log.debug('Building output variable index...')
        output_vars = {}
        for target in set(self.targets.values()):
            for tfvar in target.module.output_variables:
                output_vars[tfvar] = target.provides
        for target in set(self.targets.values()):
            for tfvar in target.module.input_variables:
                if tfvar in output_vars:
                    _log.debug(f'Matched {tfvar} from {target.name} with {output_vars[tfvar]}')
                    yield target.provides, output_vars[tfvar]

    def _explicit_dependencies(self):
        _log.debug('Adding dependencies from habfile...')
        for target in set(self.targets.values()):
            for child in target.module.depends_on:
                if child not in self.targets:
                    raise InvalidModuleError(target.module.name)
                _log.debug(f'Adding {self.targets[child].name} as a dependency of {target.name}')
                yield target.provides, self.targets[child].provides

    def _build_graph(self):
        _log.debug('Building dependency graph...')
        graph = DependencyGraph()
        for parent, child in self._explicit_dependencies():
            graph.add_constraint(parent, child)
        for parent, child in self._inferred_dependencies():
            graph.add_constraint(parent, child)
        return graph

    @as_list
    def _build_stages(self):
        graph = self._build_graph()
        _log.debug('Building stages...')
        for layer in graph.build_layers():
            targets = [ self.targets[t.id] for t in layer ]
            _log.debug(f'Built stage with targets: {", ".join(t.name for t in targets)}')
            yield Stage(targets, self)

    @property
    def stages(self):
        if self._stages is None:
            self._stages = self._build_stages()
        return self._stages
