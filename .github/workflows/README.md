# GitHub Workflows

This directory contains the GitHub Actions workflows for this repository. Below is a brief description of each workflow:

## Workflows Overview

This directory contains the GitHub Actions workflows for this repository. Below is a brief description of each workflow and the path that each change takes from the development branch through to being pushed to PyPI.

### auto-pr.yaml
This workflow automatically creates a pull request when changes are pushed to any branch except `main` and `master`. It ensures that changes are reviewed before being merged into the main branch.

### run-tests.yaml
This workflow runs the test suite to ensure that the codebase is functioning correctly. It is triggered on pull requests and pushes to the main branch. It includes steps to check out the code, set up Python, cache pip dependencies, and run tests.

### deploy.yaml
This workflow handles the deployment process. It is triggered when changes are pushed to the main branch. It includes steps to check out the code, set up Python, install dependencies, increment the version, create and merge a version update PR, build and test the package, and deploy to TestPyPI and PyPI.

### release-drafter.yaml
This workflow drafts a new release based on the merged pull requests. It is triggered when changes are pushed to the main branch. It uses the `release-drafter` action to generate release notes.

## Path from Development to PyPI

1. **Development Branch**: Developers push changes to feature branches.
2. **Auto PR**: The `auto-pr.yaml` workflow creates a pull request for the new branch.
3. **Run Tests**: The `run-tests.yaml` workflow runs tests on the pull request to ensure code quality.
4. **Merge to Main**: Once the pull request is approved and merged into the `main` branch, the `deploy.yaml` workflow is triggered.
5. **Deploy**: The `deploy.yaml` workflow increments the version, creates a version update PR, builds and tests the package, and deploys it to TestPyPI and PyPI.
6. **Release Drafter**: The `release-drafter.yaml` workflow generates release notes for the new version.

This process ensures that all changes are tested, reviewed, and documented before being deployed to PyPI.
