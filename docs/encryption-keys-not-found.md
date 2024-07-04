# Setting Up SOPS, Age/GPG, and Generating Keys

This guide will help you install SOPS, Age/GPG, and generate keys that can be used by SOPS. For more detailed information, refer to the [Manage Kubernetes secrets with SOPS](https://fluxcd.io/flux/guides/mozilla-sops/) page.

## Installing SOPS

To install SOPS, you can use the following commands:

### On macOS
```sh
brew install sops
```

### On Linux
```sh
sudo apt-get install sops
```

### On Windows
Download the latest release from the [SOPS GitHub releases page](https://github.com/mozilla/sops/releases) and add it to your PATH.

## Installing Age

To install Age, you can use the following commands:

### On macOS
```sh
brew install age
```

### On Linux
Download the latest release from the [Age GitHub releases page](https://github.com/FiloSottile/age/releases) and add it to your PATH.

### On Windows
Download the latest release from the [Age GitHub releases page](https://github.com/FiloSottile/age/releases) and add it to your PATH.

## Generating Age Keys

To generate Age keys, use the following command:
```sh
age-keygen -o ~/.config/sops/age/keys.txt
```

## Installing GPG

To install GPG, you can use the following commands:

### On macOS
```sh
brew install gnupg
```

### On Linux
```sh
sudo apt-get install gnupg
```

### On Windows
Download the latest release from the [GnuPG website](https://gnupg.org/download/) and follow the installation instructions.

## Generating GPG Keys

To generate GPG keys, use the following command:
```sh
gpg --full-generate-key
```

Follow the prompts to create your key pair.

## Excluding Files from Pre-Commit Hooks

If you need to exclude specific files from the pre-commit hooks, you can do so by modifying the `.pre-commit-config.yaml` file. However, be cautious and only exclude files if the keys are being added for tests or documentation purposes.

### Example

```yaml
- repo: local
  hooks:
    - id: kubernetes-secret
      name: Check for unencrypted Kubernetes secrets
      entry: python hooks/forbid_secrets.py --hook-id kubernetes-secret
      language: system
      files: ((^|/)*.(ya?ml)$)
      exclude: tests/.*\-fail\.ya?ml$
```

In this example, files matching the pattern `tests/.*\-fail\.ya?ml$` are excluded from the `kubernetes-secret` hook.

For more details, refer to the [Manage Kubernetes secrets with SOPS](https://fluxcd.io/flux/guides/mozilla-sops/).
