import sys
import os.path
from pathlib import PosixPath
import argparse
from .env import Environment, Biome


def _exit(status):
    exit_code = 0 if status else 1
    sys.exit(exit_code)

TRUTHY = [
    'y',
    'yes'
]
def _confirm(msg, default=False):
    t = 'Y' if default else 'y'
    f = 'N' if not default else 'n'
    resp = input(f'{msg} ({t}/{f}): ')
    if not resp.strip():
        return default
    return resp.strip().lower() in TRUTHY       

_COMMANDS = {}

def cmd_type(name):
    cmd = _COMMANDS.get(name)
    if not cmd:
        return _COMMANDS.get('_default')(name)
    return cmd

def path_type(path):
    return PosixPath(path).resolve()

def directory_type(path):
    resolved = path_type(path)
    if resolved.exists() and not resolved.is_dir():
        print(f'{resolved.as_posix()} is not a directory!')
        _exit(False)
    return resolved

def file_type(path):
    resolved = path_type(path)
    if resolved.exists() and not resolved.is_file():
        print(f'{resolved.as_posix()} is not a file!')
        _exit(False)
    return resolved

def get_args(*args):
    parser = argparse.ArgumentParser(
		prog=os.path.basename(sys.argv[0]),
		description='Easy multi-module terraform')
    parser.set_defaults(confirm=True)
    parser.add_argument('command', action = 'store', type=cmd_type, help='Terraform command to execute.')
    parser.add_argument('--vf', '--var-file', action='append', default=[], type=directory_type, metavar='VARFILE', dest='varfiles', help='Path to .tfvars or .tfvars.json files. Can be used multiple times.')
    parser.add_argument('-c', '--config', action='store', default='hab.yaml', type=file_type, help='Path to the hab configuration file. Defaults to ./hab.yaml.')
    parser.add_argument('-m', '--modules', action='store', default='.', type=directory_type, dest='modules_dir', help='Path to the directory containing your modules. Defaults to the current directory.')
    parser.add_argument('-y', '--auto-confirm', action='store_true', dest='skip_confirmation', help='Assume yes to user prompts.')
    parser.add_argument('--start-at', action='store', dest='start_at', help='Start at this module, ignoring dependencies.')
    parser.add_argument('--stop-at', action='store', dest='stop_at', help='Stop executing at the module.')
    parser.add_argument('-b', '--biome', action='store', required=True, help='Biome to apply')
    return parser.parse_args(*args)

def cmd(name):
    def inner(func):
        _COMMANDS[name] = func
        return func
    return inner

def ask_for_confirmation(msg):
    def outer(func):    
        def inner(flags, *args, **kwargs):
            if not flags.skip_confirmation and not _confirm(msg):
                return _exit(False)
            return func(flags, *args, **kwargs)
        return inner
    return outer

def return_as_exit_code(func):
    def inner(*args, **kwargs):
        return _exit(func(*args, **kwargs))
    return inner

def with_environment(func):
    def inner(flags, *args, **kwargs):
        env = Environment(flags.config, flags.modules_dir, flags.varfiles)
        # env = Environment(hab_config, cwd=flags.config.parent,  modules_dir=flags.modules_dir)
        return func(flags, env, *args, **kwargs)
    return inner
    
@cmd('_default')
def default_cmd(name):
    def inner(flags):
        print(f'Unknown module `{name}`')
        return get_args(['--help'])
    return inner

@cmd('test')
@ask_for_confirmation('Really do this?')
@return_as_exit_code
@with_environment
def test_cmd(flags, env):
    hab = Biome(flags.biome, env, flags.config)
    print(hab.stages)


def entry():
    args = get_args()
    args.command(args)