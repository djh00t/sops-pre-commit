# sops-pre-commit
This is a fork of
[onedr0p/sops-pre-commit](https://github.com/onedr0p/sops-pre-commit) with SOPS
encryption of all unencrypted kubernetes secrets added.

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/djh00t/sops-pre-commit/main.svg)](https://results.pre-commit.ci/latest/github/djh00t/sops-pre-commit/main)

Sops [pre-commit](https://pre-commit.com/) hook.

This pre-commit hook checks for unencrypted Kubernetes secrets in manifest files and encrypts them using SOPS.

## Usage

To use this pre-commit hook, add the following to your `.pre-commit-config.yaml` file in your git repository:

```yaml
- repo: https://github.com/djh00t/sops-pre-commit
  rev: v1.0.0  # Use the latest release
  hooks:
    - id: forbid-secrets
      args: ['--hook-id', 'kubernetes-secret']  # Specify the hook id for Kubernetes secrets
```

You can also pass additional arguments to customize the behavior of the hook, such as `--exclude` to specify patterns for files to exclude from checks.

## Configuration

The hook can be configured by modifying the `.pre-commit-config.yaml` file. You can specify different hook ids to check for various types of secrets, such as AWS access keys, SSH private keys, etc.

## Installation

To install this pre-commit hook, you need to have pre-commit and SOPS installed on your system.

## Supported Hooks

This pre-commit plugin provides several hooks to check for different types of secrets. Below is a list of available hook ids and their descriptions:

- `aws-access-key-id`: Checks for AWS Access Key IDs that might be hardcoded in files.
- `aws-secret-access-key`: Checks for AWS Secret Access Keys that might be hardcoded in files.
- `rsa-private-key`: Checks for RSA private keys that might be hardcoded in files.
- `ssh-private-key`: Checks for SSH private keys that might be hardcoded in files.
- `github-access-token`: Checks for GitHub access tokens that might be hardcoded in files.
- `generic-api-key`: Checks for generic API keys that might be hardcoded in files.
- `gcp-api-key`: Checks for Google Cloud Platform API keys that might be hardcoded in files.
- `jwt`: Checks for JSON Web Tokens (JWT) that might be hardcoded in files.
- `slack-webhook-url`: Checks for Slack webhook URLs that might be hardcoded in files.
- `google-oauth-client-secret`: Checks for Google OAuth client secrets that might be hardcoded in files.

To configure a hook, add the corresponding `id` to your `.pre-commit-config.yaml` file and specify any additional arguments if needed.

1. Install pre-commit:
   ```
   pip install pre-commit
   ```

2. Install SOPS:
   - For macOS: `brew install sops`
   - For other platforms, see the [SOPS release page](https://github.com/mozilla/sops/releases).

3. Add the pre-commit hook configuration to your `.pre-commit-config.yaml` as shown above.

4. Run `pre-commit install` to set up the git hook scripts.

Now pre-commit will run automatically on `git commit`!

## Requirements
Sops [pre-commit](https://pre-commit.com/) hook.

* Check for unencrypted Kubernetes secrets in manifest files.
* Encrypt unencrypted Kubernetes secrets using SOPS.

## Requirements

* Pre-commit 1.2 or later
* SOPS 3.8.1 or later (Earlier versions may work but are untested)

## License

This software is licensed under the MIT license (see the LICENSE file).
