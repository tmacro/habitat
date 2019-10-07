
class HabitatError(Exception):
    _msg = 'Unhandled Error'
    def __init__(self, *args, **kwargs):
        return super().__init__(self._msg%args, **kwargs)

class InvalidBiomeError(HabitatError):
    _msg = '%s is not a valid biome!'

class AmbiguousProvidesError(HabitatError):
    _msg = '%s and %s both provide %s!'

class InvalidModuleError(HabitatError):
    _msg = '%s is not a valid module!'