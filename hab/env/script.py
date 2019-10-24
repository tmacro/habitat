import re
from ..util.decs import as_list

class Script:
    def __init__(self, name, path):
        self.name = name
        self.path = path
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

    def cmd(self, *args):
        return f'{self.path} {" ".join(args)}'

    def execute(self, *args):
        pass

_ARG_FORMAT = re.compile(r'{([a-zA-Z][a-zA-z0-9-_]+)}')
