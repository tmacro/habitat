import re
from ..util.decs import as_list
from ..util.proc import run as procrun
_ARG_FORMAT = re.compile(r'{([a-zA-Z][a-zA-z0-9-_]+)}')

class Script:
    def __init__(self, name, path):
        self.name = name
        self.path = path
      
    def cmd(self, *args):
        return f'{self.path} {" ".join(args)}'

class Waiter:
    def __init__(self, script, flags):
        self._script = script
        self._flags = flags
        self._args = None

    @as_list
    def _extract_templated_args(self):
        for flag in self._flags:
            for match in _ARG_FORMAT.finditer(flag):
                yield match.group(1)
    @property
    def args(self):
        if self._args is None:
            self._args = self._extract_templated_args()
        return self._args

    def execute(self, **kwargs):
        _flags = [ f.format(**kwargs) for f in self._flags ]
        print(_flags)
        retcode, stdout = procrun(self._script.cmd(*_flags))
        return retcode == 0
