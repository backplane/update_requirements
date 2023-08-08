#!/usr/bin/env python3
""" python program which updates requirements.txt files in-place """
import argparse
import json
import logging
import re
import urllib.request

# see https://peps.python.org/pep-0440/#version-specifiers
req_spec = re.compile(
    # fmt: off
    r'(?P<package>.+?)'
    r'(?:'
    r'(?P<operator>'
    r'~=|'  # Compatible release clause
    r'==|'  # Version matching clause
    r'!=|'  # Version exclusion clause
    r'<=|'  # Inclusive ordered comparison clause (le)
    r'>=|'  # Inclusive ordered comparison clause (ge)
    r'<|'   # Exclusive ordered comparison clause (lt)
    r'>|'   # Exclusive ordered comparison clause (gt)
    r'==='  # Arbitrary equality clause
    r')'
    r'(?P<version>.+)'
    r')?'
    r'$'
    # fmt: on
)


def strip_bracketed(pkgspec: str) -> str:
    """returns the input with any trailing [bracket-enclosed] text removed"""
    return re.sub(r"(?:\[.+\])?$", "", pkgspec)


def updated_requirements(requirements_file: str) -> str:
    """
    Reads a requirements.txt file, returns contents updated by:
     * sorting
     * updating the versions to the latest available

    Args:
      requirements_file: The path to the requirements.txt file to update
    """
    logging.info("updated_requirements processing %s", requirements_file)

    with open(requirements_file, "rt", encoding="utf-8") as reqfh:
        requirements = reqfh.read().splitlines()
    return "\n".join([get_latest_version(req) for req in sorted(requirements)])


def get_latest_version(requirement: str) -> str:
    """
    Gets the latest version of a python package from pypi

    Args:
      requirement: The requirement string, in the form e.g. `package==version`.

    Returns:
      The latest version of the package.
    """
    logging.debug('get_latest_version for input "%s"', requirement)

    # Get the package name and version spec operator
    if match := req_spec.match(requirement.strip()):
        groups = match.groupdict()
        package = groups["package"]
        operator = groups["operator"]
    else:
        raise ValueError("expecting a requirement string")

    stripped_package = strip_bracketed(package)
    pypi_url = f"https://pypi.org/pypi/{stripped_package}/json"
    logging.debug("requesting package info from %s", pypi_url)

    with urllib.request.urlopen(pypi_url) as response:  # nosec: fixed URL used
        data = json.loads(response.read().decode())
        latest_version = data["info"]["version"]

    logging.debug('get_latest_version got latest_version="%s"', latest_version)

    # replace the operator "==" operator with "~=", leave other operators untouched
    if not operator or operator == "==":
        operator = "~="

    # Return the latest version.
    return f"{package}{operator}{latest_version}"


def write_text(path: str, contents: str, encoding="utf8") -> int:
    """
    write the given text contents to the file at the given path, return number of bytes
    written
    """
    with open(path, "wt", encoding=encoding) as outfh:
        return outfh.write(contents)


def main() -> None:
    """
    entrypoint for command-line execution. returns an int suitable for use by sys.exit()
    """
    argp = argparse.ArgumentParser(
        description=(
            "Update requirements.txt files (optionally in-place)"
            "; NOTE: Currently, version numbers are updated without regard for "
            "the version comparison operators in the requirements file, this is "
            "likely to change in the future"
        ),
        prog=__package__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    argp.add_argument(
        "file",
        nargs="+",
        help="path to the requirements.txt file",
    )
    argp.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="enable more verbose output",
    )
    argp.add_argument(
        "-i",
        "--inplace",
        action="store_true",
        help="update the file in-place instead of printing to stdout",
    )
    args = argp.parse_args()

    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.DEBUG if args.debug else logging.WARNING,
    )

    for file_path in args.file:
        updated_content = updated_requirements(file_path)
        if args.inplace:
            logging.info("updating %s in-place", file_path)
            write_text(file_path, updated_content)
            continue
        print(updated_content)
    logging.debug("done")


if __name__ == "__main__":
    main()
