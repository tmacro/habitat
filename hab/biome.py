from .error import (AmbiguousProvidesError, InvalidBiomeError,
                    InvalidModuleError)
from .stage import Target
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
        return targets

    @property
    def targets(self):
        if self._targets is None:
            self._targets = self._build_targets()
        return self._targets
