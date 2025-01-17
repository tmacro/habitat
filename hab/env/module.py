from uuid import uuid4
from ..parse import parse_tf_input, parse_tf_output
from ..util.decs import as_list

class TFModule:
    def __init__(self, name, path, statefile, provides=None, depends_on=None, should_destroy=True, before=None, after=None):
        self.id = uuid4().hex
        self.name = name
        self.path = path
        self.statefile = statefile
        self.planfile = statefile.with_suffix('.plan')
        self.provides = provides if provides is not None else [name]
        self.depends_on = depends_on if depends_on is not None else tuple()
        self.should_destroy = should_destroy
        self.before = before if before is not None else list()
        self.after = after if after is not None else list()

        self._input_vars = None
        self._output_vars = None
        self._discovered = False

    def _discover_variables(self):
        input_vars = []
        output_vars = []
        for tf_file in self.path.rglob('*.tf'):
            with open(tf_file) as f:
                txt = f.read()
            for tfvar in parse_tf_input(txt):
                input_vars.append(tfvar.name)
            for tfvar in parse_tf_output(txt):
                output_vars.append(tfvar.name)
        self._input_vars = input_vars
        self._output_vars = output_vars
        self._discovered = True

    @property
    def input_variables(self):
        if not self._discovered:
            self._discover_variables()
        return self._input_vars

    @property
    def output_variables(self):
        if not self._discovered:
            self._discover_variables()
        return self._output_vars

    def __repr__(self):
        return f'<TFModule: {self.name}'
