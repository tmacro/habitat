import re
from .util.decs import as_list
from enum import Enum
from collections import namedtuple
from uuid import uuid4
import yaml
import json
import jsonschema
from jsonschema.exceptions import ValidationError
from pathlib import PosixPath
from .habfile import load_habfile

HABFILE_SCHEMA_PATH = f'{ PosixPath(__file__).resolve().parent / "habfile.json" }'
with open(HABFILE_SCHEMA_PATH) as f:
    HABFILE_SCHEMA  = json.load(f)

class TFVarType(Enum):
    INPUT = 1
    OUTPUT = 2
    CONFIG = 3

# For convenience when specifying defaults
_EmptyNamedTuple = namedtuple('EmptyDikt', [])()
_EmptyTuple = tuple()

HabFile = namedtuple('HabFile', ['habitats', 'biomes', 'modules', 'scripts', 'version'])
Habitat = namedtuple('Habitat', ['name', 'biomes'] )
Biome = namedtuple('Biome', ['name', 'modules'])
Module = namedtuple('Module', ['name', 'should_destroy', 'before', 'after', 'provides', 'depends_on'])
Script = namedtuple('Script', ['name', 'path'])
ModuleScript = namedtuple('ModuleScript', ['name', 'args', 'args_from'])
ModuleScriptArg = namedtuple('ModuleScriptArg', ['name', 'module'])

TFVar = namedtuple('TFVar', [
        'name',
        'var_type',
        'value',
        'sensitive'
    ],
    defaults=[
        None,
        False
    ])

TYPE_MAPPINGS = {
    'string': str,
    'number': int,
    'list(string)': str
}

QUOTES = ['"', "'"]
def _has_quotes(line):
    start = line[0]
    end = line[-1]
    return start in QUOTES and end in QUOTES and start == end

def _strip_quotes(line):
    if _has_quotes(line):
        return line[1:-1]
    return line

# Tries to guess the type (string/int) of a tfvar value
# Returns a function to coerce the given value to its type
def _guess_type(value):
    if _has_quotes(value):
        return lambda x: str(_strip_quotes(x))
    try:
        int(value)
    except ValueError:
        return str
    return int

# Converts a dictionary to a namedtuple with matching keys
def _to_namedtuple(name, dikt):
    dikt_type = namedtuple(name, dikt.keys())
    return dikt_type(**dikt)

class Patterns:
    tf_input_var_block = re.compile(r'^variable\s+"(?P<name>\w+)"\s+{\n(?P<conf>(?:[\t ]*\w+[\t ]*=[\t ]*[\S\t ]+\n)+)^}', flags=re.MULTILINE)
    tf_output_var_block = re.compile(r'^output\s+"(?P<name>\w+)"\s+{\n(?P<conf>(?:[\t ]*\w+[\t ]*=[\t ]*[\S\t ]+\n)+)^}', flags=re.MULTILINE)
    tf_block_values = re.compile(r'^[\t ]*(?P<key>\w+)[\t ]*=[\t ]*(?P<value>[\S\t ]+)[\t ]*$', flags=re.MULTILINE)
    tfvar_value = re.compile(r'^(?P<key>[\w_-]+)[\t ]+=[\t ]+(?P<value>[\S\t ]+)$', flags=re.MULTILINE)

@as_list
def parse_tfvars(text):
    for tfvar in Patterns.tfvar_value.finditer(text):
        value = tfvar.group('value')
        yield TFVar(name=tfvar.group('key'), value=_guess_type(value)(value), var_type=TFVarType.CONFIG)

def parse_tfvars_json(text):
    data = json.loads(text)
    for name, value in data.items():
        yield TFVar(name=name, value=value, var_type=TFVarType.CONFIG)

@as_list
def parse_terraform_output(text):
    data = json.loads(text)
    for key, info in data.items():
        yield TFVar(name=key, var_type=info['type'], value=info['value'], sensitive=info['sensitive'])

@as_list
def parse_tf_input(text):
    for tfvar in Patterns.tf_input_var_block.finditer(text):
        yield TFVar(name=tfvar.group('name'), var_type=TFVarType.INPUT)

@as_list
def parse_tf_output(text):
    for tfvar in Patterns.tf_output_var_block.finditer(text):
        varconf = dict(name=tfvar.group('name'), var_type=TFVarType.OUTPUT)
        for value in Patterns.tf_block_values.finditer(tfvar.group('conf')):
            if value.group('key') == 'sensitive':
                varconf['sensitive'] = value.group('value') == 'true'
        yield TFVar(**varconf)

def parse_habfile(text):
    data =  yaml.load(text)
    try:
        jsonschema.validate(instance=data, schema=HABFILE_SCHEMA)
    except ValidationError as e:
        return None
    return load_habfile(data)
