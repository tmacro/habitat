from .parse import parse_tfvars, parse_tfvars_json
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

    def _keys(self):
        return self._module.output_variables
        
    @classmethod
    def from_module(cls, module):
        return cls(module.name)

    def resolve(self):
        data = self._module.output()
        self._tfvars = { k: v['value'] for k,v in  data.items() }
        self._resolved = True

    def collect(self, **kwargs):
        if not self._resolved:
            self.resolve()
        return super().collect(**kwargs)

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

# class VarFiles:
#     def __init__(self, paths, modules):
#         self._varfiles = {}
#         self._varfiles.update(self._load_files(paths))
#         self._varfiles.update(self._load_modules(modules))

#     def _load_files(self, paths):
#         varfiles = {}
#         for path in paths:
#             varfile = VarFileLoader.from_file(path)
#             varfiles[varfile.name] = varfile
#         return varfiles

#     def _load_modules(self, modules):
#         varfiles = {}
#         for module in modules:
#             varfile = VarFileLoader.from_module(module)
#             varfiles[varfile.name] = varfile
#         return varfiles

#     def collect(self, *args):
#         tfvars = {}
#         for varfile in self._varfiles.values():
#             tfvars.update(varfile.collect(args))
#         return tfvars