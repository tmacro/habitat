from itertools import chain

from .module import TFModule
from .parse import parse_habfile
from .tfvars import VarFileLoader
from .util.decs import as_dict, as_list
from .util.log import Log

_log = Log('environment')

class Environment:
    def __init__(self, habfile_path, modules_dir, varfile_paths, state_dir):
        self._habfile_path = habfile_path
        self._modules_dir = modules_dir
        self._varfile_paths = varfile_paths
        self._state_dir = state_dir
        self._varfiles = None
        self._modules = None
        self._habfile = None

    def _load_habfile(self):
        _log.debug('Loading habfile...')
        with open(self._habfile_path) as f:
            return parse_habfile(f.read())

    def _get_statefile(self, module):
        if not self._state_dir.exists():
            self._state_dir.mkdir()
        return self._state_dir / f'{module}.tfstate'

    @as_dict
    def _load_modules(self):
        _log.debug('Loading modules...')
        hab_modules = { m.name: m for m in self.habfile.modules }
        for path in filter(lambda p: p.is_dir() and len(list(p.glob('*.tf'))), self._modules_dir.glob('*')):
            kwargs = {}
            if path.name in hab_modules:
                kwargs['depends_on'] = hab_modules[path.name].depends_on
                kwargs['should_destroy'] = hab_modules[path.name].should_destroy
                kwargs['provides'] = hab_modules[path.name].provides if hab_modules[path.name].provides else None
            _log.debug(f'Found module {path.name}, depends on: {kwargs.get("depends_on")}, provides: {kwargs.get("provides")}')
            yield path.name, TFModule(path.name, path, self._get_statefile(path.name), **kwargs)

    @as_list
    def _load_varfiles(self):
        _log.debug('Loading varfiles...')
        for path in self._varfile_paths:
            _log.debug(f'Loaded varfile from {path}')
            yield VarFileLoader.from_file(path)

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
