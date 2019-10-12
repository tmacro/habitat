from tempfile import TemporaryFile
import sys
from threading import Thread, Event
import subprocess
import shlex

class TBuffer:
    def __init__(self, echo=True, file=sys.stderr):
        self._buffer = TemporaryFile()
        self._echo = file if echo else None

    def write(self, data):
        self._buffer.write(data)
        if self._echo is not None:
            self._echo.write(data)

    def read(self):
        self._buffer.seek(0)
        data = self._buffer.read()
        self._buffer.close()
        return data

    @property
    def fileno(self):
        return self._buffer.fileno

class Process(Thread):
    def __init__(self, cmd, echo=True, **kwargs):
        super().__init__()
        self._cmd = cmd
        self._kwargs = kwargs
        self.echo = echo
        self._started = Event()
        self._done = Event()
        self._stdout = None
        self._stderr = None

    @property
    def cwd(self)
        return self._kwargs.get('cwd')

    @cwd.setter
    def cwd(self, value):
        self._kwargs['cwd'] = value

    @property
    def started(self):
        return self._started.is_set()

    def run(self):
        self._started.set()
        if self.echo:
            self._stdout = TBuffer()
            self._stderr = TBuffer()
            self._kwargs['stdout'] = self._stdout
            self._kwargs['stderr'] = self._stderr
            self._kwargs['encoding'] = 'utf-8'
        self._proc = subprocess.Popen(shlex.split(self._cmd), **self._kwargs)
        while self._proc.poll() is None:
            try:
                self._proc.wait(1)
            except subprocess.TimeoutExpired:
                pass
        self._done.set()

    def wait(self):
        self._done.wait()
        return self._proc.poll()

    def stdout(self):
        if not self.started:
            self.start()
            self.wait()
        return self._stdout.read()

    def stderr(self):
        if not self.started:
            self.start()
            self.wait()
        return self._stderr.read()

def run(cmd, env=None, **kwargs):
    return Process(cmd, env=env, **kwargs)
