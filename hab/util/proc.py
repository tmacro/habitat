class Tailer(Thread):
    def __init__(self, fd, done, echo=True, file=sys.stderr):
        super().__init__()
        self._fd = fd
        self._output = []
        self._done = done
        self._echo = file if echo else None
        self._out = file

    def run(self):
        while not self._done.is_set():
            line = self._fd.readline()
            self._output.append(line)
            if self._echo:
                self._echo.write(line)
            
    def output(self):
        return ''.join(self._output)

class Process(Thread):
    def __init__(self, cmd, echo=True, **kwargs):
        super().__init__()
        self._cmd = cmd
        self._kwargs = kwargs
        self._output  = dict(stdout=[], stderr=[])
        self._done = Event()
        self._echo = echo
           
    def run(self):
        self._proc = subprocess.Popen(shlex.split(self._cmd), stderr=subprocess.PIPE, stdout=subprocess.PIPE, encoding="utf-8", **self._kwargs)
        stdout_tailer = Tailer(self._proc.stdout, self._done, echo=self._echo)
        stdout_tailer.start()
        stderr_tailer = Tailer(self._proc.stderr, self._done, echo=self._echo)
        stderr_tailer.start()
        while self._proc.poll() is None:
            try:
                self._proc.wait(1)
            except subprocess.TimeoutExpired:
                pass
        self._done.set()
        self._output['stdout']  = stdout_tailer.output()
        self._output['stderr']  = stderr_tailer.output()

    def wait(self):
        self._done.wait()
        return self._proc.poll()

    @property
    def stdout(self):
        return self._output['stdout']

def run(cmd, env=None, **kwargs):
    return Process(cmd, env=env, **kwargs)