"""
Setup configuration for the project.
"""

import toml
from setuptools import find_packages, setup


def get_version():
    """
    Reads the version from the pyproject.toml file.

    Returns:
        The version string.
    """
    with open("pyproject.toml", "r", encoding="utf-8") as f:
        pyproject_data = toml.load(f)
    return pyproject_data["tool"]["semantic_release"]["version"]


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sops-pre-commit",
    version=get_version(),
    author="David Hooton",
    author_email="klingon_tools+david@hooton.org",
    description="Check for unencrypted secrets and encrypt them using sops and"
    "age/gpg. Forked from https://github.com/onedr0p/sops-pre-commit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/djh00t/sops-pre-commit",
    packages=find_packages(),
    python_requires=">=3.6",
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
    include_package_data=True,
    data_files=[("", ["CHANGELOG.md", "README.md"])],
)
