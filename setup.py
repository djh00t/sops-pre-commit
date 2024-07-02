from setuptools import find_packages, setup

setup(
    name="sops-pre-commit",
    description="Check for unencrypted Kubernetes secrets in manifest files and encrypt them before allowing git to push. Forked from https://github.com/onedr0p/sops-pre-commit",
    url="https://github.com/djh00t/sops-pre-commit",
    version="1.0.0",
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
    packages=find_packages("."),
    entry_points={
        "console_scripts": [
            "forbid_secrets = hooks.forbid_secrets:main",
        ],
    },
)
