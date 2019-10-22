from .parse import parse_tfvars, parse_tfvars_json, parse_terraform_output
from .util.decs import as_list
from tempfile import NamedTemporaryFile
import json

class TFVars:
    def __init__(self, source, *args):
        self._source = source
        self._vars = args

    def collect(self):
        return self._source.collect(*self._vars)

    def __repr__(self):
        return f'<TFVars: { " ".join(self._vars) }'

class BaseVarFile:
    def __init__(self, name, **kwargs):
        self._name = name
        self._tfvars = kwargs
        self.keys = list(self._tfvars.keys())

    def collect(self, *args):
        return { k: self._tfvars[k] for k in args if k in self._tfvars }

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
        if path.suffix == '.json':
            loader = parse_tfvars_json
        elif path.suffix == '.tfvars':
            loader = parse_tfvars
        return { v.name: v.value for v in loader(text) }

    @classmethod
    def from_file(cls, path):
        return cls(path.name, **cls._load_file(path))

class TargetBackedVarFile(BaseVarFile):
    def __init__(self, target, **kwargs):
        super().__init__(target.name, **kwargs)
        self._target = target
        self._resolved = False

    @as_list
    def _keys(self):
        return self._target.module.output_variables

    @classmethod
    def from_target(cls, target):
        return cls(target)

    def resolve(self):
        success, stdout = self._target.output()
        if success:
            data = parse_terraform_output(stdout)
            self._tfvars = { v.name: v.value for v in  data }
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
    def from_target(target):
        return TargetBackedVarFile.from_target(target)

class TempVarFile:
    def __init__(self, tfvars):
        self._tfvars = tfvars
        self._tempfile = None

    def __enter__(self):
        self._tempfile = NamedTemporaryFile('w', suffix='.tfvars.json', encoding='utf-8')
        tfvars = {}
        print(self._tfvars)
        print('*' * 50)
        for tfvar in self._tfvars:
            tfvars.update(tfvar.collect())
        print(tfvars)
        json.dump(tfvars, self._tempfile)
        self._tempfile.flush()
        return self._tempfile

    def __exit__(self, *args):
        self._tempfile.close()

