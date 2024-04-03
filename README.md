# sops-pre-commit
This is a fork of
[onedr0p/sops-pre-commit](https://github.com/onedr0p/sops-pre-commit) with SOPS
encryption of all unencrypted kubernetes secrets added.

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/djh00t/sops-pre-commit/main.svg)](https://results.pre-commit.ci/latest/github/djh00t/sops-pre-commit/main)

Sops [pre-commit](https://pre-commit.com/) hook.

* Check for unencrypted Kubernetes secrets in manifest files.
* Encrypt unencrypted Kubernetes secrets using SOPS.

## Requirements

* Pre-commit 1.2 or later
* SOPS 3.8.1 or later (Earlier versions may work but are untested)

## Installation

Add the following to your `.pre-commit-config.yaml`


```yaml
- repo: https://github.com/djh00t/sops-pre-commit
  rev: v1.0.0
  hooks:
    - id: forbid-secrets
```

## License

This software is licensed under the MIT license (see the LICENSE file).
