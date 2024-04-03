"""
This script is a pre-commit hook that checks for unencrypted Kubernetes secrets in files.
It uses regular expressions to identify secret definitions and ignores them if they are
encrypted with SOPS or marked for deletion in Kustomize patches. If an unencrypted secret
is found, it exits with a non-zero status code to block the commit.
"""
from __future__ import print_function

import argparse
import re
import sys

SECRET_REGEX = r"^kind:\ssecret$"
SOPS_REGEX = r"ENC.AES256"
KUSTOMIZE_REGEX = r"^\$patch:\sdelete"


CREATION_RULES_PATH_REGEX = r"your_path_regex_here"  # Replace with your actual regex

def is_encrypted_with_sops(filename):
    """
    Checks if the given filename is encrypted with SOPS.
    """
    with open(filename, 'r') as file:
        return SOPS_REGEX in file.read()

def contains_secret(filename):
    """
    Checks if the given filename contains an unencrypted Kubernetes secret.
    """
    with open(filename, mode="r") as file_checked:
        lines = file_checked.read()
        kubernetes_secret = re.findall(
            SECRET_REGEX, lines, flags=re.IGNORECASE | re.MULTILINE
        )
        # Check if the file matches the creation rules path regex and is not encrypted
        if re.search(CREATION_RULES_PATH_REGEX, filename) and not is_encrypted_with_sops(filename):
            print(
                "File matches creation rules path regex but is not encrypted with SOPS: {0}".format(filename)
            )
            return True
        if kubernetes_secret:
            ignore_secret = re.findall(
                SOPS_REGEX, lines, flags=re.IGNORECASE | re.MULTILINE
            ) or re.findall(KUSTOMIZE_REGEX, lines, flags=re.IGNORECASE | re.MULTILINE)
            if not ignore_secret:
                return True
    return False

def main(argv=None):
    """
    Main function that parses arguments and checks each file for secrets and encryption.
    """
    """
    Main function that parses arguments and checks each file for secrets.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*", help="filenames to check")
    args = parser.parse_args(argv)
    files_with_secrets = [f for f in args.filenames if contains_secret(f)]
    return_code = 0
    for file_with_secrets in files_with_secrets:
        print(
            "Unencrypted Kubernetes secret detected in file: {0}".format(
                file_with_secrets
            )
        )
        return_code = 1
    return return_code


if __name__ == "__main__":
    """
    If this script is executed as the main module, start the main function.
    """
    sys.exit(main(sys.argv[1:]))
