from uuid import uuid4
from .util.decs import as_list
from .tfvars import TFVars, TempVarFile, VarFileLoader
import concurrent.futures
from . import terraform
from .util.proc import run as procrun
from .util.log import Log

_log = Log('stage')

_TARGET_CMD_DEPS = {
    'init': [],
    'validate': [ 'init' ],
    'plan': [ 'init', 'validate' ],
    'apply': [ 'init', 'validate', 'plan' ],
    'output': [ 'init', 'validate', 'plan', 'apply' ],
    'destroy': [],
    'clean': [],
    'fclean': [ 'clean' ],
}

class Target:
    def __init__(self, provides, module):
        self.provides = provides
        self._module = module
        self.id = uuid4().hex
        self._results = dict()

    @property
    def module(self):
        return self._module

    @property
    def name(self):
        return self._module.name

    def _run(self, cmd):
        if cmd not in self._results:
            retcode, stdout = procrun(cmd, cwd=self.module.path)
            self._results[cmd] = (retcode == 0, stdout)
        return self._results[cmd]

    def init(self, tfvars, *args, **kwargs):
        cmd = terraform.init(*args, **kwargs)
        return self._run(cmd)

    def validate(self, tfvars, *args, **kwargs):
        cmd = terraform.validate(*args, **kwargs)
        return self._run(cmd)

    def plan(self, tfvars, *args, **kwargs):
        with TempVarFile(tfvars) as varfile:
            cmd = terraform.plan(*args, state=self.module.statefile, out=self.module.planfile, var_file=varfile.name, **kwargs)
            return self._run(cmd)

    def apply(self, tfvars, *args, **kwargs):
        cmd = terraform.apply(*args, self.module.planfile, state=self.module.statefile, **kwargs)
        return self._run(cmd)

    def output(self, *args, **kwargs):
        cmd = terraform.output(*args[1:], state=self.module.statefile, json=True, **kwargs)
        return self._run(cmd)

    def destroy(self, tfvars, *args, **kwargs):
        if self._module.should_destroy:
            with TempVarFile(tfvars) as varfile:
                cmd = terraform.destroy(*args, state=self.module.statefile, var_file=varfile.name, auto_approve=True, **kwargs)
                return self._run(cmd)
        return True, ''

    def clean(self, tfvars, *args, **kwargs):
        cmd = terraform.clean(self.module.statefile, self.module.planfile)
        return self._run(cmd)

    def fclean(self, tfvars, *args, **kwargs):
        cmd = terraform.fclean(self.module.path / '.terraform', self.module.statefile.with_suffix('.tfstate.backup'))
        return self._run(cmd)

class Stage:
    def __init__(self, targets, biome):
        self._targets = targets
        self._biome = biome

    @as_list
    def _build_tfvars(self, target):
        for varfile in self._biome.env.varfiles:
            tfvars = [ v for v in target.module.input_variables if v in varfile.keys ]
            if tfvars:
                yield TFVars(varfile, *tfvars)
        for module in self._biome.env.modules.values():
            tfvars = [ v for v in target.module.input_variables if v in module.output_variables ]
            # print(module)
            if tfvars:
                varfile = VarFileLoader.from_target(Target('__config__', module))
                yield TFVars(varfile, *tfvars)

    @property
    def targets(self):
        return self._targets

    def _execute_target(self, target, command):
        _log.debug('Executing dependent commands')
        for dep in _TARGET_CMD_DEPS.get(command):
            success, _ = getattr(target, dep)(self._build_tfvars(target))
            if not success:
                return False, ''
        _log.debug('Executing command')
        print(getattr(target, command))
        return getattr(target, command)(self._build_tfvars(target))

    def execute(self, executor, command):
        tasks = []
        for target in self.targets:
            task = executor.submit(self._execute_target, target, command)
            tasks.append(task)
        return tasks

    def __repr__(self):
        return f'<Stage: { ", ".join(t.module.name for t in self._targets) }>'


class Runner:
    def __init__(self, stages, max_workers=None):
        self._stages = stages
        self._max_workers = max_workers if max_workers is not None else len(stages) + 5

    @classmethod
    def _execute_stage(cls, executor, stage, command, prevtask=None):
        if prevtask is not None:
            print(f'Waiting for previous before executing {stage}')
            if not prevtask.result():
                return False
        print(f'Done Waiting, Executing {stage}')
        tasks = stage.execute(executor, command)
        results = concurrent.futures.wait(tasks)
        return all(map(lambda f: f.result()[0], results.done))

    def execute(self, command):
        prevtask = None
        tasks = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            for stage in self._stages:
                print(f'Executing {stage}')
                if not self._execute_stage(executor, stage, command, prevtask):
                    print(f'Stage {stage} failed to apply')
                    return False
            # print(results)
            # if not all(map(lambda f: f.result(), results.done)):
            #     print (f'{ len(list(filter(lambda f: not f.result(), results.done))) } Stages did not complete successfully!')
            return True