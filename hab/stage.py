class Target:
    def __init__(self, provides, module):
        self.provides = provides
        self._module = module
        self.id = uuid4().hex

    @property
    def module(self):
        return self._module

    @property
    def name(self):
        return self._module.name

    @property
    def output_variables(self):
        return self._module.output_variables

    @property
    def input_variables(self):
        return self._module.input_variables

class Stage:
    def __init__(self, targets, biome):
        self._targets = targets
        self._biome = biome

    @property
    def targets(self):
        return self._targets

    def __repr__(self):
        return f'<Stage: { ", ".join(t.module.name for t in self._targets) }>'
