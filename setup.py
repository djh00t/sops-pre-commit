"""
Setup configuration for the sops-pre-commit package.
"""

import os
import re

from setuptools import find_packages, setup  # type: ignore


def get_version():
    """
    Retrieve the version of the package from the version.py file.

    Returns:
        str: The version string.

    Raises:
        RuntimeError: If the version string cannot be found.
    """
    version_file = os.path.join(os.path.dirname(__file__), "version.py")
    with open(version_file, encoding="utf-8") as version_file_obj:
        code = version_file_obj.read()
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]", code, re.M
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="sops-pre-commit",
    version=get_version(),
    packages=find_packages(),
    description="Check for unencrypted secrets and encrypt them using sops and"
    "age/gpg. Forked from https://github.com/onedr0p/sops-pre-commit",
    url="https://github.com/djh00t/sops-pre-commit",
    author="David Hooton",
    author_email="sops-pre-commit+david@hooton.org",
    platforms="linux",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    install_requires=[
        "argparse",
        "datetime",
        "typing",
        "ruamel.yaml",
    ],
    entry_points={
        "console_scripts": [
            "forbid_secrets = hooks.forbid_secrets:main",
        ],
    },
)
