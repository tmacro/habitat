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
- Environment: Represents operating env, derived from *.tf files, directory structure, and the habfile
    - Modules
        - input variables
        - output variables
        - waiters (before/after)
    - Varfiles: Represents configuration values or values derived from module output
    - Scripts: User defined paths to external scripts, for use in modules as waiters

- Biome: Represents state derived from env
    - Stage: A number of Targets that can be applied in parallel
    - Target:  Implements operations on a module, consumes Varsfiles, Modules and Scripts (through waiters)

- Runner: Consumes Biome, executes underlying terraform commands

