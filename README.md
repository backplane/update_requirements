# update_requirements

This utility updates requirements.txt files (optionally in-place), sorts them, and updates the version numbers therein.

*NOTE:* Currently, version numbers are updated without regard for the version comparison operators already in the requirements file, this can do bad things in non-trivial requirements files. This limitation is likely to change in the future.

## Usage Text

The following text is printed when the program is invoked with the `-h` or `--help` flags:

```
usage: update_requirements [-h] [-d] [-i] file [file ...]

Update requirements.txt files (optionally in-place); NOTE: Currently, version
numbers are updated without regard for the version comparison operators in the
requirements file, this is likely to change in the future

positional arguments:
  file           path to the requirements.txt file

options:
  -h, --help     show this help message and exit
  -d, --debug    enable more verbose output (default: False)
  -i, --inplace  update the file in-place instead of printing to stdout
                 (default: False)

```
