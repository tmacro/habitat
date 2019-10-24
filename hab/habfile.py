from collections import namedtuple
from .util.decs import as_tuple

HabFile = namedtuple('HabFile', ['habitats', 'biomes', 'modules', 'scripts', 'version'])
Habitat = namedtuple('Habitat', ['name', 'biomes'] )
Biome = namedtuple('Biome', ['name', 'modules'])
Module = namedtuple('Module', ['name', 'should_destroy', 'before', 'after', 'provides', 'depends_on'])
Script = namedtuple('Script', ['name', 'path'])
ModuleScript = namedtuple('ModuleScript', ['name', 'args'])
ModuleScriptArg = namedtuple('ModuleScriptArg', ['name', 'module'])

@as_tuple
def _load_module_scripts(data):
    for script in data:
        yield ModuleScript(
            name=script.get('name'),
            args=tuple(script.get('args', [])),
        )

@as_tuple
def _load_modules(data):
    for module in data:
        yield Module(
            name=module.get('name'),
            should_destroy=module.get('should_destroy', True),
            provides=tuple(module.get('provides', [])),
            depends_on=tuple(module.get('depends_on', [])),
            before=_load_module_scripts(module.get('before', [])),
            after=_load_module_scripts(module.get('after', []))
        )

@as_tuple
def _load_scripts(data):
    for script in data:
        yield Script(
            name=script.get('name'),
            path=script.get('path')
        )


@as_tuple
def _load_biomes(data):
    for biome in data:
        yield Biome(
            name=biome.get('name'),
            modules=tuple(biome.get('modules'))
        )


@as_tuple
def _load_habitats(data):
    for habitat in data:
        yield Habitat(
            name=habitat.get('name'),
            biomes=tuple(habitat.get('biomes'))
        )

def load_habfile(data):
    return HabFile(
        habitats=_load_habitats(data.get('habitats', [])),
        biomes=_load_biomes(data.get('biomes', [])),
        modules=_load_modules(data.get('modules', [])),
        scripts=_load_scripts(data.get('scripts', [])),
        version=data.get('version')
    )