from ..tfvars import TFVars, VarFileLoader
from ..util.decs import as_list
from ..util.log import Log
from .target import Target
from itertools import chain

_log = Log('stage')

_TARGET_CMD_DEPS = {
    'init': [],
    'validate': [ 'init' ],
    'plan': [ 'init', 'validate' ],
    'apply': [ 'init', 'validate', 'plan', 'before' ],
    'output': [ 'init', 'validate', 'plan', 'apply' ],
    'destroy': [],
    'clean': [],
    'fclean': [ 'clean' ],
}

_TARGET_CMD_FINISH = {
    'destroy': [ 'after' ]
}

class Stage:
    def __init__(self, targets, biome):
        self._targets = targets
        self._biome = biome
        self.__tfvars = None

    def _build_tfvars(self):
        varfiles_from_targets = [VarFileLoader.from_target(Target('__config__', module)) for module in self._biome.env.modules.values()]
        return TFVars(list(chain(self._biome.env.varfiles, varfiles_from_targets)))

    @property
    def _tfvars(self):
        if self.__tfvars is None:
            self.__tfvars = self._build_tfvars()
        return self.__tfvars

    # @as_list
    # def _build_tfvars(self, target):
    #     for varfile in self._biome.env.varfiles:
    #         tfvars = [ v for v in target.module.input_variables if v in varfile.keys ]
    #         if tfvars:
    #             yield TFVars(varfile, *tfvars)
    #     for module in self._biome.env.modules.values():
    #         tfvars = [ v for v in target.module.input_variables if v in module.output_variables ]
    #         if tfvars:
    #             varfile = VarFileLoader.from_target(Target('__config__', module))
    #             yield TFVars(varfile, *tfvars)

    @property
    def targets(self):
        return self._targets

    def _execute_target(self, target, command):
        for dep in _TARGET_CMD_DEPS.get(command):
            success, _ = getattr(target, dep)(self._tfvars)
            if not success:
                return False, ''
        success, stdout = getattr(target, command)(self._tfvars)
        if not success or command not in _TARGET_CMD_FINISH:
            return success, stdout
        for finisher in _TARGET_CMD_FINISH.get(command):
            _success, _ = getattr(target, finisher)(self._tfvars)
            if not _success:
                return False, ''
        return 


    def execute(self, executor, command):
        tasks = {}
        for target in self.targets:
            task = executor.submit(self._execute_target, target, command)
            tasks[task] = target.name
        return tasks

    def __repr__(self):
        return f'<Stage: { ", ".join(t.module.name for t in self._targets) }>'
