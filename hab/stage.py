class Target:
    def __init__(self, provides, module):
        self.provides = provides
        self._module = module
        self.id = uuid4().hex

    @property
    def module(self):
        return self._module

    def init(self):
        pass

    def validate(self):
        pass

    def plan(self):
        pass

    def apply(self):
        pass

    def output(self):
        pass

    def clean(self):
        pass

    def fclean(self):
        pass

class Stage:
    def __init__(self, targets, biome):
        self._targets = targets
        self._biome = biome

    @property
    def targets(self):
        return self._targets

    def __repr__(self):
        return f'<Stage: { ", ".join(t.module.name for t in self._targets) }>'
