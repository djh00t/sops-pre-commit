## [1.0.0-release.1](https://github.com/djh00t/sops-pre-commit/compare/v0.0.2...v1.0.0-release.1) (2024-07-31)


### ⚠ BREAKING CHANGES

* None

Signed-off-by: David Hooton <david@hooton.org>

* 🔧 chore(.pre-commit-config.yaml):Update comments and formatting in pre-commit ([c7ff947](https://github.com/djh00t/sops-pre-commit/commit/c7ff947a080ec5a3f5c13dbdf29e4b4ce803b73f))


### Features

* **github-actions:** add Auto PR workflow for automated pull request creation ([d94c69c](https://github.com/djh00t/sops-pre-commit/commit/d94c69ca7a2037290bb86fb5222ed732529dd96f))
* **workflow:** add full release workflow ([e320ec2](https://github.com/djh00t/sops-pre-commit/commit/e320ec2421c83cf4c7f0721d19544004ad912213))
* **requirements:** add initial dependencies list ([c5c1aa6](https://github.com/djh00t/sops-pre-commit/commit/c5c1aa64e349a64dc8c9b871605ebbe394c474c8))
* **requirements:** add jinja2 to project dependencies ([3dd0e96](https://github.com/djh00t/sops-pre-commit/commit/3dd0e96a6df6a6e563e35977fb5b4df7a29cd77b))
* **package.json:** add package metadata and update dependencies ([7645e7e](https://github.com/djh00t/sops-pre-commit/commit/7645e7ef38013a03392e20b6818d508f5d7239c5))
* **workflows:** add semantic-release script for automated versioning and ([af48bbf](https://github.com/djh00t/sops-pre-commit/commit/af48bbf9911666c10d39741bae40cf11239a7649))
* **workflows/pr_body_gen:** enhance PR body generation with branch name ([8acff4d](https://github.com/djh00t/sops-pre-commit/commit/8acff4d164065163124f4d03604cb7c761f46a09))
* **hooks/forbid_secrets:** improve handling of age encryption keys ([fabfeb2](https://github.com/djh00t/sops-pre-commit/commit/fabfeb234afb8ed8b4b897007e34f5e929e3e9b1))
* **pyproject.toml:** update project configuration and versioning ([aacaba3](https://github.com/djh00t/sops-pre-commit/commit/aacaba3ae1fd77be6742840ad53a5b8b8a957146))


### Bug Fixes

* **hooks/forbid_secrets:** add warning for missing .age.pub file during key ([e656feb](https://github.com/djh00t/sops-pre-commit/commit/e656feb1ae0d457ff2569042bd63056b2b66314f))
* **setup.py:** update package version to 0.0.3 ([bdc297e](https://github.com/djh00t/sops-pre-commit/commit/bdc297e2974beb929caa359bc84160ca3ad3a315))
* Update RSA and SSH private key checks to exclude invalid examples and ensure matching valid content only ([a05cee3](https://github.com/djh00t/sops-pre-commit/commit/a05cee36cd8f2e66fe404b22a2843becbb9d7d8a))

# [1.0.0](https://github.com/djh00t/sops-pre-commit/compare/v0.0.2...v1.0.0) (2024-07-31)


### Bug Fixes

* Update RSA and SSH private key checks to exclude invalid examples and ensure matching valid content only ([a05cee3](https://github.com/djh00t/sops-pre-commit/commit/a05cee36cd8f2e66fe404b22a2843becbb9d7d8a))


* 🔧 chore(.pre-commit-config.yaml):Update comments and formatting in pre-commit ([c7ff947](https://github.com/djh00t/sops-pre-commit/commit/c7ff947a080ec5a3f5c13dbdf29e4b4ce803b73f))


### BREAKING CHANGES

* None

Signed-off-by: David Hooton <david@hooton.org>

# [1.0.0](https://github.com/djh00t/sops-pre-commit/compare/v0.0.2...v1.0.0) (2024-07-31)


* 🔧 chore(.pre-commit-config.yaml):Update comments and formatting in pre-commit configuration file ([c7ff947](https://github.com/djh00t/sops-pre-commit/commit/c7ff947a080ec5a3f5c13dbdf29e4b4ce803b73f))


### Bug Fixes

* Update RSA and SSH private key checks to exclude invalid examples and ensure matching valid content only ([a05cee3](https://github.com/djh00t/sops-pre-commit/commit/a05cee36cd8f2e66fe404b22a2843becbb9d7d8a))


### BREAKING CHANGES

* None

Signed-off-by: David Hooton <david@hooton.org>
