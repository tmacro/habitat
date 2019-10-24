import re
from ..util.decs import as_list
from .script import

_ARG_FORMAT = re.compile(r'{([a-zA-Z][a-zA-z0-9-_]+)}')

class Waiter:
    def __init__(self, script, args):
        self._script = script
        self._raw_args = args
        self._args = None

    @as_list
    def _extract_templated_args(self):
        for arg in self._args:
            for match in _ARG_FORMAT.finditer(arg):
                yield match.group(1)
    @property
    def args(self):
        if self._args is None:
            self._args = self._extract_templated_args()
        return self._args

    def execute(self, tfvars):
        _tfvars = {}
        for varfile in tfvars:
            _tfvars.update(varfile.coolec)
