import concurrent.futures
from .util.decs import as_list
from .util.log import Log

_log = Log('runner')

class Action:
    def __init__(self,  stage, command):
        self._stage = stage
        self._command = command

    def execute(self, executor):
        _log.debug(f'Executing {self._command} in {self._stage}')
        tasks = self._stage.execute(executor, self._command)
        results = concurrent.futures.wait(tasks.keys())
        success = all(map(lambda f: f.result()[0], results.done))
        failures = []
        if not success:
            failures = [ tasks[t] for t in filter(lambda t: not t.result()[0], results.done) ]
        return success, failures

class Runner:
    def __init__(self, stages, max_workers=None):
        self._stages = stages
        self._max_workers = max_workers if max_workers is not None else len(stages) + 5

    def _build_actions(self, command):
        for stage in self._stages:
            yield Action(stage, command)

    def execute(self, command):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            for action in self._build_actions(command):
                success, failures = action.execute(executor)
                if not success:
                    _log.error(f'Modules { " ".join(failures) } failed to {command}')
                    return False
        return True
