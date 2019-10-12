from .parse import parse_tfvars, parse_tfvars_json, parse_tf_output
from .util.decs import as_list

class BaseVarFile:
    def __init__(self, name, **kwargs):
        self._name = name
        self._tfvars = kwargs

    def collect(self, *args):
        return { k: self._tfvars[k] for k in args if k in self._tfvars }

    @as_list
    def _keys(self):
        return self._tfvars.keys()

    @property
    def keys(self):
        return self._keys()

    @as_list
    def _values(self):
        return self._tfvars.values()

    @property
    def values(self):
        return self._values()

    @property
    def name(self):
        return self._name

class FileBackedVarFile(BaseVarFile):
    @staticmethod
    def _load_file(path):
        with open(path) as f:
            text = f.read()
        if path.suffix == 'json':
            loader = parse_tfvars
        elif path.suffix == 'tfvars':
            loader = parse_tfvars_json
        return { v.name: v.value for v in loader(text) }

    @classmethod
    def from_file(cls, path):
        return cls(path.name, **cls._load_file(path))

class ModuleBackedVarFile(BaseVarFile):
    def __init__(self, module, **kwargs):
        super().__init__(module.name, **kwargs)
        self._module = module
        self._resolved = False

    @as_list
    def _keys(self):
        return self._module.output_variables

    @classmethod
    def from_module(cls, module):
        return cls(module.name)

    def resolve(self):
        data = parse_tf_output(self._module.output().stdout())
        self._tfvars = { k: v['value'] for k,v in  data.items() }
        self._resolved = True

    def collect(self, *args):
        if not self._resolved:
            self.resolve()
        return super().collect(*args)

    def _values():
        if not self._resolved:
            self.resolve()
        return super()._values()

class VarFileLoader:
    @staticmethod
    def from_file(path):
        return FileBackedVarFile.from_file(path)

    @staticmethod
    def from_module(module):
        return ModuleBackedVarFile.from_module(module)


class TFVar:
    def __init__(self, name, source):
        self._name = name
        self._source = source

    def value(self):
        return self._source.collect(name)
