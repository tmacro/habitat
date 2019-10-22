from collections import defaultdict
from .error import UnexpectedFlagError

_FLAGS = defaultdict(dict)

def _format_kwarg(name, value, with_equal=True, is_flag=False):
    _name = name.replace('_', '-')
    if is_flag:
        return f'-{ _name }' if value else ''
    _value = str(value)
    if isinstance(value, bool):
        _value = _value.lower()
    return f'-{ _name }{ "=" if with_equal else " " }{ _value }'

def flag(name, **kwargs):
    def outer(func):
        _FLAGS[func][name] = kwargs
        return func
    return outer

def format_flags(func):
    def inner(*args, **kwargs):
        format_args = _FLAGS[func]
        flags = []
        for name, value in kwargs.items():
            if name not in format_args:
                raise UnexpectedFlagError(name)
            flags.append(_format_kwarg(name, value, **format_args[name]))
        return func(args, flags)
    return inner

def _format_command(cmd, args, flags):
    return f'terraform { cmd } { " ".join(flags) } { " ".join(str(a) for a in args) }'

@format_flags
@flag('backend')
@flag('backend_config')
@flag('force_copy', is_flag=True)
@flag('from_module')
@flag('get')
@flag('get_plugins')
@flag('input')
@flag('lock')
@flag('lock_timeout')
@flag('no_color', is_flag=True)
@flag('plugin_dir', with_equal=False)
@flag('reconfigure', is_flag=True)
@flag('upgrade')
@flag('verify_plugins')
def init(args, flags):
    return _format_command('init', args, flags)

@format_flags
@flag('json', is_flag=True)
@flag('no_color', is_flag=True)
def validate(args, flags):
    return _format_command('validate', args, flags)

@format_flags
@flag('destroy', is_flag=True)
@flag('detailed_exitcode', is_flag=True)
@flag('input')
@flag('lock')
@flag('lock_timeout')
@flag('no_color', is_flag=True)
@flag('out')
@flag('parallelism')
@flag('refresh')
@flag('state')
@flag('target')
@flag('var', with_equal=False)
@flag('var_file')
def plan(args, flags):
    return _format_command('plan', args, flags)

@format_flags
@flag('backup')
@flag('auto_approve', is_flag=True)
@flag('lock')
@flag('lock_timeout')
@flag('input')
@flag('no_color')
@flag('parallelism')
@flag('refresh')
@flag('state')
@flag('state_out')
@flag('target')
@flag('var')
@flag('var_file')
def apply(args, flags):
    return _format_command('apply', args, flags)

@format_flags
@flag('state')
@flag('no_color', is_flag=True)
@flag('json', is_flag=True)
def output(args, flags):
    return _format_command('output', args, flags)

@format_flags
@flag('backup')
@flag('auto_approve', is_flag=True)
@flag('lock')
@flag('lock_timeout')
@flag('no_color')
@flag('parallelism')
@flag('refresh')
@flag('state')
@flag('state_out')
@flag('target')
@flag('var')
@flag('var_file')
def destroy(args, flags):
    return _format_command('destroy', args, flags)

def clean(*args):
    return f'rm -f { " ".join(str(s) for s in args) }'

def fclean(*args):
    return f'rm -rf { " ".join(str(s) for s in args) }'
