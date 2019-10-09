from .error import (AmbiguousProvidesError, InvalidBiomeError,
                    InvalidModuleError, NonexistentDependencyError)
from .dependency import DependencyGraph
from .stage import Target, Stage

class Biome:
    def __init__(self, name, env, habfile_path):
        self.name = name
        self._env = env
        self._habfile_path = habfile_path
        self._habfile = None
        self._targets = None
        self.__modules = None
        self._stages = None
        if not self._has_biome:
            raise InvalidBiomeError(self.name)

    @property
    def _has_biome(self):
        return self.name in [b.name for b in self._env.habfile.biomes]

    def _load_modules(self):
        biomes_modules = {}
        for biome in self._env.habfile.biomes:
            if biome.name == self.name:
                for name in biome.modules:
                    if name not in self._env.modules:
                        raise InvalidModuleError(name)
                    biomes_modules[name] = self._env.modules[name]
                break
        return biomes_modules

    @property
    def _modules(self):
        if self.__modules is None:
            self.__modules = self._load_modules()
        return self.__modules

    def _build_targets(self):
        targets = {}
        for module in self._modules.values():
            if is_iterable(module.provides):
                for provider in module.provides:
                    if provider in targets:
                        raise AmbiguousProvidesError(
                                module.name,
                                targets[provider].module.name,
                                provider
                            )
                    targets[provider] = Target(provider, module)
            elif is_string(module.provides):
                if module.provides in targets:
                    raise AmbiguousProvidesError(
                            module.name,
                            targets[module.provides].module.name,
                            module.provides
                        )
                targets[module.provides] = Target(module.provides, module)
                targets[targets[module.provides].id] = targets[module.provides]
        return targets

    @property
    def targets(self):
        if self._targets is None:
            self._targets = self._build_targets()
        return self._targets

    def _inferred_dependencies(self):
        output_vars = {}
        for provides, target in self.targets.items():
            for tfvar in target.module.output_variables:
                output_vars[tfvar] = target.id
        for provides, target in self.targets.items():
            for tfvar in target.module.input_variables:
                if tfvar in output_vars:
                    yield target.id, output_vars[tfvar]

    def _explicit_dependencies(self):
        for provides, target in self.targets.items():
            for child in target.module.depends_on:
                if child not in self.targets:
                    raise NonexistentDependencyError(target.module.name, child)
                yield target.id, self.targets[child].id

    def _build_graph(self):
        graph = DependencyGraph()
        for parent, child in self._explicit_dependencies():
            graph.add_constraint(parent, child)
        for parent, child in self._inferred_dependencies():
            graph.add_constraint(parent, child)
        return graph

    @as_list
    def _build_stages(self):
        graph = self._build_graph()
        for layer in graph.build_layers():
            targets = [ self.targets[t.name] for t in layer ]
            yield Stage(targets, self)

    @property
    def stages(self):
        if self._stages is None:
            self._stages = self._build_stages()
        return self._stages
