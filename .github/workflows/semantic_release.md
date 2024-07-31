
# Managing Releases with Semantic Release and GitHub Actions

This document explains how we manage releases for our Python library using `semantic-release`. It covers the installation, configuration, and workflow setup to ensure automatic versioning, changelog generation, and publishing to PyPI.

## Overview

`semantic-release` automates the versioning and release process based on commit messages following the Conventional Commits standard. It helps in maintaining a consistent and predictable release process.

## Installation

### Install Dependencies

First, install the required dependencies by running the following commands:

```bash
npm install -D semantic-release @semantic-release/changelog @semantic-release/git @semantic-release/github @semantic-release/release-notes-generator @semantic-release/exec
```

## Configuration

### `.releaserc` File

Create a `.releaserc` file in the root of your repository with the following content:

```json
{
  "branches": ["main", "release"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/changelog",
    "@semantic-release/github"
  ]
}
```

### Setup Python Version Management

Ensure your `setup.py` dynamically reads the version from a `version.py` file.

1. **`version.py`**: Create a file named `version.py` in the root of your repository with the following content:

    ```python
    __version__ = "0.1.0"
    ```

2. **`setup.py`**: Modify your `setup.py` to read the version from `version.py`:

    ```python
    import os
    import re
    from setuptools import setup, find_packages

    def get_version():
        version_file = os.path.join(os.path.dirname(__file__), 'version.py')
        with open(version_file) as f:
            code = f.read()
            version_match = re.search(r"^__version__ = ['"]([^'"]*)['"]", code, re.M)
            if version_match:
                return version_match.group(1)
            raise RuntimeError("Unable to find version string.")

    setup(
        name='your_package_name',
        version=get_version(),
        packages=find_packages(),
        # other setup arguments...
    )
    ```

## GitHub Actions Workflow

Create a GitHub Actions workflow to automate the release process. Add the following YAML configuration to `.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    branches:
      - main

jobs:
  release:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v2

      - name: Set up Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '16'

      - name: Install Node.js dependencies
        run: npm install

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.x'

```

### GitHub Secrets

Ensure you have the following secrets set up in your GitHub repository:

- `PYPI_USER_AGENT`: Your PyPI API key

## Conventional Commits

Our commit messages follow the Conventional Commits standard. Here’s a brief guide:

- `feat: description` for new features
- `fix: description` for bug fixes
- `docs: description` for documentation changes
- `style: description` for formatting changes
- `refactor: description` for code refactoring
- `test: description` for adding or modifying tests
- `chore: description` for maintenance tasks

## Release Process

When a commit is pushed to the `main` branch, the GitHub Actions workflow will:

1. Checkout the code.
2. Set up the Node.js and Python environments.
3. Install the necessary dependencies.
4. Run `semantic-release` to:
   - Analyze commits to determine the next version.
   - Generate release notes and update the changelog.
   - Commit the updated changelog and version files.
   - Create a GitHub release.
   - Build the Python package.
   - Publish the package to PyPI using `twine`.

### Example Release

A typical GitHub release will include:

- **Title**: `vX.X.X` (new version number)
- **Release Notes**:
    ```
    ## [v1.2.0] - 2024-06-26

    ### Features

    - **api:** add user authentication endpoint ([#12](https://github.com/your-repo/issues/12)) ([abcdef1](https://github.com/your-repo/commit/abcdef1))
    - **core:** implement new caching strategy ([#15](https://github.com/your-repo/issues/15)) ([1234567](https://github.com/your-repo/commit/1234567))

    ### Bug Fixes

    - **db:** fix connection leak issue ([#20](https://github.com/your-repo/issues/20)) ([89abcd1](https://github.com/your-repo/commit/89abcd1))
    - **ui:** correct alignment of buttons ([#22](https://github.com/your-repo/issues/22)) ([6543210](https://github.com/your-repo/commit/6543210))

    ### Documentation

    - **readme:** update installation instructions ([#30](https://github.com/your-repo/issues/30)) ([0fedcba](https://github.com/your-repo/commit/0fedcba))

    ### Changelog

    See the full changelog [here](https://github.com/your-repo/CHANGELOG.md).

    ---
    This release was generated automatically by [semantic-release](https://github.com/semantic-release/semantic-release).
    ```

## Summary

By following the steps outlined in this document, we ensure a consistent and automated release process for our Python library, leveraging the power of `semantic-release` to handle versioning, changelog generation, and publishing to PyPI. This setup not only saves time but also reduces human error, ensuring our releases are predictable and reliable.
