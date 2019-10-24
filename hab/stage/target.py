from uuid import uuid4
from ..tfvars import TempVarFile
from .. import terraform
from ..util.proc import run as procrun
from ..util.log import Log

_log = Log('target')

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
        with TempVarFile(tfvars, self._module.input_variables) as varfile:
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
            with TempVarFile(tfvars, self._module.input_variables) as varfile:
                cmd = terraform.destroy(*args, state=self.module.statefile, var_file=varfile.name, auto_approve=True, **kwargs)
                return self._run(cmd)
        return True, ''

    def clean(self, tfvars, *args, **kwargs):
        cmd = terraform.clean(self.module.statefile, self.module.planfile)
        return self._run(cmd)

    def fclean(self, tfvars, *args, **kwargs):
        cmd = terraform.fclean(self.module.path / '.terraform', self.module.statefile.with_suffix('.tfstate.backup'))
        return self._run(cmd)

    def before(self, tfvars, *args, **kwargs):
        for waiter in self._module.before:
            _kwargs = tfvars.collect(*waiter.args)
            success = waiter.execute(**_kwargs)
            if not success:
                return False, ''
        return True, ''

    def after(self, tfvars, *args, **kwargs):
        for waiter in self._module.after:
            _kwargs = tfvars.collect(*waiter.args)
            success = waiter.execute(**_kwargs)
            if not success:
                return False, ''
        return True, ''