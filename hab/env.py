from pathlib import PosixPath
from pprint import pprint
from uuid import uuid4

from .error import (AmbiguousProvidesError, InvalidBiomeError,
                    InvalidModuleError)

from .dependency import DependencyGraph
from .module import TFModule
from .parse import parse_habfile
from .tfvars import VarFileLoader
from .util.decs import as_dict, as_list
from .util.type import is_string, is_iterable

class Environment:
    def __init__(self, habfile_path, modules_dir, varfile_paths):
        self._habfile_path = habfile_path
        self._modules_dir = modules_dir
        self._varfile_paths = varfile_paths
        self._varfiles = None
        self._modules = None
        self._habfile = None

    def _load_habfile(self):
        with open(self._habfile_path) as f:
            return parse_habfile(f.read())
    
    @as_dict 
    def _load_modules(self):
        hab_modules = { m.name: m for m in self.habfile.modules }
        for path in filter(lambda p: p.is_dir(), self._modules_dir.glob('*')):
            kwargs = {}
            if path.name in hab_modules:
                kwargs['depends_on'] = hab_modules[path.name].depends_on
            yield path.name, TFModule(path.name, path, **kwargs)

    def _load_varfiles(self):
        return {
            path.name: VarFileLoader.from_file(path) for path in self._varfile_paths
        }

    @property
    def varfiles(self):
        if self._varfiles is None:
            self._varfiles = self._load_varfiles()
        return self._varfiles

    @property
    def modules(self):
        if self._modules is None:
            self._modules = self._load_modules()
        return self._modules

    @property
    def habfile(self):
        if self._habfile is None:
            self._habfile = self._load_habfile()
        return self._habfile

class Target:
    def __init__(self, provides, module):
        self.provides = provides
        self._module = module
        self.id = uuid4().hex

    @property
    def module(self):
        return self._module

    def init(self):
        pass
    
    def validate(self):
        pass

    def plan(self):
        pass

    def apply(self):
        pass

    def output(self):
        pass

    def clean(self):
        pass

    def fclean(self):
        pass

class Stage:
    def __init__(self, targets, biome):
        self._targets = targets
        self._biome = biome

    @property
    def targets(self):
        return self._targets

    def __repr__(self):
        return f'<Stage: { ", ".join(t.module.name for t in self._targets) }>'

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