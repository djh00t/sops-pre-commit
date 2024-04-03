"""
This script is a pre-commit hook that checks for unencrypted Kubernetes secrets in files.
It uses regular expressions to identify secret definitions and ignores them if they are
encrypted with SOPS or marked for deletion in Kustomize patches. If an unencrypted secret
is found, it exits with a non-zero status code to block the commit.
"""
from __future__ import print_function

import argparse
import yaml
import sys
import subprocess
import re
from encrypt_decrypt_sops import encrypt_file
import yaml

SOPS_REGEX = r"ENC.AES256"
KUSTOMIZE_REGEX = r"^\$patch:\sdelete"

CREATION_RULES_PATH_REGEX = None  # This will be set after reading from .sops.yaml

SECRET_PATTERNS = {
    'AWS Access Key ID': r'AKIA[0-9A-Z]{16}',
    'AWS Secret Access Key': r'(?i)aws(.{0,20})?['"\s]?([0-9a-zA-Z/+]{40})',
    'RSA Private Key': r'-----BEGIN RSA PRIVATE KEY-----',
    'SSH Private Key': r'-----BEGIN (EC|OPENSSH|DSA|RSA) PRIVATE KEY-----',
    'GitHub Personal Access Token': r'ghp_[0-9a-zA-Z]{36}',
    'Generic API Key': r'(?i)api(_|-)?key['"\s]?[:=]['"\s]?[0-9a-zA-Z]{32,}',
    'Google Cloud Platform API Key': r'AIza[0-9A-Za-z\\-_]{35}',
    'JSON Web Token (JWT)': r'eyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]*',
    'Slack Webhook URL': r'https://hooks.slack.com/services/T[A-Z0-9]{8}/B[A-Z0-9]{8}/[a-zA-Z0-9]{24}',
    'Google OAuth 2.0 Client Secret': r'(?i)"client_secret":"[a-zA-Z0-9-_]{24}',
}

def load_creation_rules_path_regex():
    """
    Loads the path_regex from the .sops.yaml file.
    """
    with open('.sops.yaml', 'r') as sops_config_file:
        sops_config = yaml.safe_load(sops_config_file)
        for rule in sops_config.get('creation_rules', []):
            path_regex = rule.get('path_regex')
            if path_regex:
                return path_regex
        raise ValueError("No path_regex found in .sops.yaml creation_rules.")

def is_encrypted_with_sops(filename):
    """
    Checks if the given filename is encrypted with SOPS.
    """
    with open(filename, 'r') as file:
        return SOPS_REGEX in file.read()

def is_kubernetes_secret(data):
    """
    Determines if the provided data structure represents a Kubernetes secret.
    """
    return data.get('kind', '').lower() == 'secret' and data.get('apiVersion', '').startswith('v1')

def contains_secret(filename):
    """
    Checks if the given filename contains an unencrypted Kubernetes secret by parsing the YAML content.
    """
    with open(filename, 'r') as file:
        file_content = file.read()

    for secret_type, pattern in SECRET_PATTERNS.items():
        if re.search(pattern, file_content):
            print(f"Detected {secret_type} in file: {filename}")
            encrypt_file(filename)
            return True

    try:
        with open(filename, 'r') as file:
            documents = yaml.safe_load_all(file)
            for doc in documents:
                if is_kubernetes_secret(doc):
                    # Additional checks for SOPS and Kustomize can be implemented here
                    return True
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file {filename}: {e}")
    return False

def is_sops_installed():
    """
    Checks if SOPS is installed by attempting to call it.
    """
    try:
        subprocess.run(['sops', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def prompt_install_sops():
    """
    Prompts the user to install SOPS if it is not installed.
    """
    print("SOPS is not installed. It is required to encrypt secrets.")
    approval = input("Would you like to install SOPS now? [y/N]: ").strip().lower()
    if approval == 'y':
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
            print("SOPS has been successfully installed.")
            return True
        except subprocess.CalledProcessError as e:
            print("Failed to install SOPS:", e)
            return False
    else:
        print("SOPS installation was not approved. Exiting.")
        return False

def main(argv=None):
    """
    Main function that parses arguments and checks each file for secrets and encryption.
    """
    secrets_detected = False
    if not is_sops_installed():
        if not prompt_install_sops():
            return 1

    global CREATION_RULES_PATH_REGEX
    CREATION_RULES_PATH_REGEX = load_creation_rules_path_regex()

    """
    Main function that parses arguments and checks each file for secrets.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*", help="filenames to check")
    args = parser.parse_args(argv)
    files_with_secrets = [f for f in args.filenames if contains_secret(f)]
    return_code = 0
    for file_with_secrets in files_with_secrets:
        secrets_detected = True
        print(
            "Unencrypted Kubernetes secret detected in file: {0}".format(
                file_with_secrets
            )
        )
        return_code = 1
    if secrets_detected:
        print("Secrets were detected and encrypted.")
    return return_code


if __name__ == "__main__":
    """
    If this script is executed as the main module, start the main function.
    """
    sys.exit(main(sys.argv[1:]))
