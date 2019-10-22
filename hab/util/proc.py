from io import StringIO
import sys
from threading import Thread, Event
import subprocess
import shlex
from .log import Log

_log = Log('proc')

class TBuffer(Thread):
    def __init__(self, stream, echo=True, output=sys.stderr):
        super().__init__()
        self._stream = stream
        self._buffer = StringIO()
        self._echo = output if echo else None

    @property
    def data(self):
        return self._buffer.getvalue()

    def run(self):
        while True:
            try:
                line = self._stream.readline()
                self._buffer.write(line)
                if self._echo:
                    self._echo.write(line)
            except ValueError:
                break
    
    def close(self):
        self._buffer.close()
        self.join()

    def start(self):
        super().start()
        return self

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
    def cwd(self):
        return self._kwargs.get('cwd')

    @cwd.setter
    def cwd(self, value):
        self._kwargs['cwd'] = value

    @property
    def started(self):
        return self._started.is_set()

    def run(self):
        self._started.set()
        _log.debug(f'Starting process { self._cmd }')
        if self.echo:
            self._kwargs['stdout'] = self._kwargs['stderr'] = subprocess.PIPE
            self._kwargs['encoding'] = 'utf-8'
        print(self._kwargs)
        self._proc = subprocess.Popen(shlex.split(self._cmd), **self._kwargs)
        if self.echo:
            self._stdout = TBuffer(self._proc.stdout).start()
            self._stderr = TBuffer(self._proc.stderr).start()
        while self._proc.poll() is None:
            try:
                self._proc.wait(timeout=1)
            except subprocess.TimeoutExpired:
                pass
        self._done.set()
        _log.debug(f'{ self._cmd } exited { self._proc.poll() }')

    def wait(self):
        if not self.started:
            self.start()
        self._done.wait()
        return self._proc.poll()

    def stdout(self):
        if not self.started:
            self.start()
            self.wait()
        if self._stdout is not None:
            return self._stdout.data

    def stderr(self):
        if not self.started:
            self.start()
            self.wait()
        if self._stderr is not None:
            return self._stderr.data

    def join(self):
        if self.echo:
            self._stdout.close()
            self._stderr.close()
        super().join()

def run(*args, **kwargs):
    proc = Process(*args, **kwargs)
    proc.start()
    retcode = proc.wait()
    stdout = proc.stdout()
    proc.join()
    return retcode, stdout