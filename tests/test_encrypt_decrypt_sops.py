import os
import subprocess
import sys

import pytest

from hooks.encrypt_decrypt_sops import (
    check_if_encrypted,
    decrypt_file,
    encrypt_file,
    root_dir,
)

# Define the paths to the test files
TEST_FILES_DIR = "tests"
SECRET_PASS_FILE = os.path.join(TEST_FILES_DIR, "secret-pass.yaml")
SECRET_FAIL_FILE = os.path.join(TEST_FILES_DIR, "secret-fail.yaml")

# Global variables for temporary key files
temp_age_pub = False
temp_age_key = False


@pytest.fixture
def setup_files():
    # Ensure the test files are in a known state before each test
    # Generate temporary .age.pub and age.agekey files if they don't exist

    if not os.path.exists(os.path.join(root_dir, "age.agekey")):
        subprocess.run(
            ["age-keygen", "-o", os.path.join(root_dir, "age.agekey")],
            check=True,
        )

    if not os.path.exists(os.path.join(root_dir, ".age.pub")):
        with open(
            os.path.join(root_dir, "age.agekey"), "r", encoding="utf-8"
        ) as f:
            lines = f.readlines()
            public_key = lines[1].split(": ")[1].strip()
        with open(
            os.path.join(root_dir, ".age.pub"), "w", encoding="utf-8"
        ) as f:
            f.write(public_key)
    try:
        result = subprocess.run(
            ["sops", "--encrypt", "--in-place", SECRET_PASS_FILE],
            capture_output=True,
            check=True,
            text=True,
        )
        if result.returncode != 0:
            print(
                f"ERROR: Failed to encrypt {SECRET_PASS_FILE}: "
                f"{result.stderr}",
                file=sys.stderr,
            )
    except subprocess.CalledProcessError as e:
        print(
            f"ERROR: Failed to encrypt {SECRET_PASS_FILE}: {e}",
            file=sys.stderr,
        )
    try:
        result = subprocess.run(
            ["sops", "--decrypt", "--in-place", SECRET_FAIL_FILE],
            capture_output=True,
            check=True,
            text=True,
        )
        if result.returncode != 0:
            print(
                f"ERROR: Failed to decrypt {SECRET_FAIL_FILE}: "
                f"{result.stderr}",
                file=sys.stderr,
            )
    except subprocess.CalledProcessError as e:
        print(
            f"ERROR: Failed to decrypt {SECRET_FAIL_FILE}: {e}",
            file=sys.stderr,
        )
    yield
    # Clean up after tests
    try:
        result = subprocess.run(
            ["sops", "--decrypt", "--in-place", SECRET_PASS_FILE],
            capture_output=True,
            check=True,
            text=True,
        )
        if result.returncode != 0:
            print(
                f"ERROR: Failed to decrypt {SECRET_PASS_FILE}: "
                f"{result.stderr}",
                file=sys.stderr,
            )
    except subprocess.CalledProcessError as e:
        print(
            f"ERROR: Failed to decrypt {SECRET_PASS_FILE}: {e}",
            file=sys.stderr,
        )
    try:
        result = subprocess.run(
            ["sops", "--encrypt", "--in-place", SECRET_FAIL_FILE],
            capture_output=True,
            check=True,
            text=True,
        )
        if result.returncode != 0:
            print(
                f"ERROR: Failed to encrypt {SECRET_FAIL_FILE}: "
                f"{result.stderr}",
                file=sys.stderr,
            )
    except subprocess.CalledProcessError as e:
        print(
            f"ERROR: Failed to encrypt {SECRET_FAIL_FILE}: {e}",
            file=sys.stderr,
        )


def test_encrypt_file():
    decrypt_file(SECRET_PASS_FILE)
    assert not check_if_encrypted(SECRET_PASS_FILE)
    encrypt_file(SECRET_PASS_FILE)
    assert check_if_encrypted(SECRET_PASS_FILE)


def test_decrypt_file():
    encrypt_file(SECRET_FAIL_FILE)
    assert check_if_encrypted(SECRET_FAIL_FILE)
    decrypt_file(SECRET_FAIL_FILE)
    assert not check_if_encrypted(SECRET_FAIL_FILE)
    if temp_age_pub:
        os.remove(os.path.join(root_dir, ".age.pub"))
    if temp_age_key:
        os.remove(os.path.join(root_dir, "age.agekey"))
