# Data sources
## For configuration
- *.tfvars files
- *.tfvars.json files
- Module output
- CLI flags
- environment variables

## For operating environment
- *.tf Modules files
- directory structure

# Object structure
- Environment: Represents operating env, derived from *.tf files and dir structure
    - Modules
        - input variables
        - output variables
    - Varfiles: Represents configuration values or values derived from module output

- Biome: Represents state derived from env
    - Stage: A number of Targets that can be applied in parallel
    - Target:  Implements operations on a module, consumes DataSources
    - DataSource: Represents sources of variables for consumption, maybe file or module based

- Runner: Consumes Habitat, executes underlying terraform commands

