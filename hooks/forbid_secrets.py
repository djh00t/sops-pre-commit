"""
This module provides functionality to check for unencrypted secrets in files
and encrypt them using SOPS (Secrets OPerationS). It supports various secret
types and can handle Kubernetes secrets specifically.
"""

import argparse
import os
import re
import subprocess
import sys
from typing import Optional

import yaml  # type: ignore

KUSTOMIZE_REGEX = r"^\$patch:\sdelete"


root_dir = subprocess.getoutput("git rev-parse --show-toplevel")


def read_key_file(
    file_path: str, line_number: Optional[int] = None
) -> Optional[str]:
    """Reads a key from a file.

    If line_number is specified, reads that specific line.

    Args:
        file_path: The path to the file.
        line_number: The line number to read (optional).

    Returns:
        The content of the file or the specific line.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            if line_number is not None:
                return file.readlines()[line_number].strip()
            return file.read().strip()
    except FileNotFoundError:
        return ""


key_age_public = read_key_file(os.path.join(root_dir, ".age.pub"))
key_age_private = read_key_file(
    os.path.join(root_dir, "age.agekey"), line_number=1
)


def encrypt_file(file_path: str) -> None:
    """Encrypts the given file using SOPS if it is not already encrypted.

    Args:
        file_path: The path to the file to encrypt.
    """
    if not check_if_encrypted(file_path):
        print("File Status:   DECRYPTED")
        print("Action:        ENCRYPTING")
        try:
            subprocess.run(
                ["sops", "--encrypt", "--in-place", file_path], check=True
            )
        except subprocess.CalledProcessError as e:
            print(
                f"ERROR: Failed to encrypt file: {file_path}", file=sys.stderr
            )
            print(f"ERROR: {str(e)}", file=sys.stderr)
            raise
        print("File Status:   ENCRYPTED")
    else:
        print("File Status:   ENCRYPTED")
        print("Action:        SKIPPING")


def check_contains_key_age_public(file_path: str) -> bool:
    """Checks if the given file contains the key_age_public string.

    Args:
        file_path: The path to the file.

    Returns:
        True if the file contains the key_age_public string, False otherwise.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        if key_age_public and key_age_public in content:
            return True
    except FileNotFoundError:
        print(f"ERROR: File {file_path} not found.", file=sys.stderr)
    return False


def check_if_encrypted(file_path: str) -> bool:
    """Checks if the given file is encrypted.

    Looks for the SOPS encryption markers.

    Args:
        file_path: The path to the file.

    Returns:
        True if the file is encrypted, False otherwise.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    encrypted_file_regex = re.compile(
        r"^(-----BEGIN (AGE ENCRYPTED FILE|PGP MESSAGE)-----[\s\S]*?"
        r"-----END (AGE ENCRYPTED FILE|PGP MESSAGE)-----|ENC\[AES256_GCM,"
        r"data:.*?\]|encrypted_regex:.*)$",  # noqa
        re.MULTILINE,
    )

    return bool(encrypted_file_regex.search(content))


def check_aws_access_key_id(content: str) -> re.Match | None:
    """Checks if the content contains an AWS Access Key ID.

    Args:
        content: The content to check.

    Returns:
        A regex match object if an AWS Access Key ID is found, None otherwise.
    """
    return re.search(r"AKIA[0-9A-Z]{16}", content)


def check_aws_secret_access_key(content: str) -> re.Match | None:
    """Checks if the content contains an AWS Secret Access Key.

    Args:
        content: The content to check.

    Returns:
        A regex match object if an AWS Secret Access Key is found, None
        otherwise.
    """
    return re.search(r'(?i)aws(.{0,20})?[\'"\s]?([0-9a-zA-Z/+]{40})', content)


def check_rsa_private_key(content: str) -> re.Match | None:
    """Checks if the content contains an RSA Private Key.

    Args:
        content: The content to check.

    Returns:
        A regex match object if an RSA Private Key is found, None otherwise.
    """
    return re.search(
        r"-----BEGIN RSA PRIVATE KEY-----\s*([A-Za-z0-9+/=\s]+)\s*"
        r"-----END RSA PRIVATE KEY-----",  # noqa
        content,
        re.DOTALL,
    )


def check_ssh_private_key(content: str) -> re.Match | None:
    """Checks if the content contains an SSH Private Key.

    Args:
        content: The content to check.

    Returns:
        A regex match object if an SSH Private Key is found, None otherwise.
    """
    return re.search(
        r"-----BEGIN ((EC|OPENSSH|DSA) PRIVATE KEY|RSA PRIVATE KEY)-----\s*"
        r"([A-Za-z0-9+/=\s]+)\s*-----END ((EC|OPENSSH|DSA) PRIVATE KEY|RSA "
        r"PRIVATE KEY)-----",  # noqa
        content,
        re.DOTALL,
    )


def check_github_access_token(content: str) -> re.Match | None:
    """Checks if the content contains a GitHub Access Token.

    Args:
        content: The content to check.

    Returns:
        A regex match object if a GitHub Access Token is found, None
        otherwise.
    """
    return re.search(r"ghp_[0-9a-zA-Z]{36}", content)


def check_generic_api_key(content: str) -> re.Match | None:
    """Checks if the content contains a generic API key.

    Args:
        content: The content to check.

    Returns:
        A regex match object if a generic API key is found, None otherwise.
    """
    return re.search(
        r'(?i)api(_|-)?key[\'"\\s]?[:=][\'"\\s]?[0-9a-zA-Z]{32,}', content
    )


def check_gcp_api_key(content: str) -> re.Match | None:
    """Checks if the content contains a GCP API key.

    Args:
        content: The content to check.

    Returns:
        A regex match object if a GCP API key is found, None otherwise.
    """
    return re.search(r"AIza[0-9A-Za-z\\-_]{35}", content)


def check_jwt(content: str) -> re.Match | None:
    """Checks if the content contains a JWT token.

    Args:
        content: The content to check.

    Returns:
        A regex match object if a JWT token is found, None otherwise.
    """
    return re.search(
        r"eyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]*", content
    )


def check_slack_webhook_url(content: str) -> re.Match | None:
    """Checks if the content contains a Slack webhook URL.

    Args:
        content: The content to check.

    Returns:
        A regex match object if a Slack webhook URL is found, None otherwise.
    """
    return re.search(
        r"https://hooks.slack.com/services/T[A-Z0-9]{8}/B[A-Z0-9]{8}/"
        r"[a-zA-Z0-9]{24}",
        content,
    )


def check_google_oauth_client_secret(content: str) -> re.Match | None:
    """Checks if the content contains a Google OAuth client secret.

    Args:
        content: The content to check.

    Returns:
        A regex match object if a Google OAuth client secret is found, None
        otherwise.
    """
    return re.search(r'(?i)"client_secret":"[a-zA-Z0-9-_]{24}', content)


SECRET_CHECKS = {
    "aws-access-key-id": check_aws_access_key_id,
    "aws-secret-access-key": check_aws_secret_access_key,
    "rsa-private-key": check_rsa_private_key,
    "ssh-private-key": check_ssh_private_key,
    "github-access-token": check_github_access_token,
    "generic-api-key": check_generic_api_key,
    "gcp-api-key": check_gcp_api_key,
    "jwt": check_jwt,
    "slack-webhook-url": check_slack_webhook_url,
    "google-oauth-client-secret": check_google_oauth_client_secret,
}

EXCLUDE_PATTERNS: list[str] = []


def is_excluded(filename: str, exclude_patterns: list[str]) -> bool:
    """Checks if the given filename matches any of the exclude patterns.

    Args:
        filename: The name of the file. exclude_patterns: A list of regex
        patterns to exclude.

    Returns:
        True if the filename matches any of the exclude patterns, False
        otherwise.
    """
    return any(re.search(pattern, filename) for pattern in exclude_patterns)


def is_kubernetes_secret(data: dict) -> bool:
    """Determines if the provided data structure represents a Kubernetes
    secret.

    Args:
        data: The data structure to check.

    Returns:
        True if the data represents a Kubernetes secret, False otherwise.
    """
    return data.get("kind", "").lower() == "secret" and data.get(
        "apiVersion", ""
    ).startswith("v1")


def check_kubernetes_secret_file(filename: str) -> bool:
    """Checks if the given filename contains a Kubernetes secret.

    Args:
        filename: The name of the file.

    Returns:
        True if the file contains a Kubernetes secret, False otherwise.
    """
    try:
        with open(filename, "r", encoding="utf-8") as file:
            documents = yaml.safe_load_all(file)
            for doc in documents:
                if isinstance(doc, list):
                    for item in doc:
                        if is_kubernetes_secret(item):
                            if not check_if_encrypted(filename):
                                print(
                                    "WARNING: Detected unencrypted Kubernetes"
                                    "Secret "
                                    f"in file: {filename}",
                                    file=sys.stderr,
                                )
                                encrypt_file(filename)
                                return True
                            print(
                                "File is already encrypted with SOPS: "
                                f"{filename}"
                            )
                            return False
                elif is_kubernetes_secret(doc):
                    if not check_if_encrypted(filename):
                        print(
                            "WARNING: Detected unencrypted Kubernetes Secret "
                            f"in file: {filename}",
                            file=sys.stderr,
                        )
                        encrypt_file(filename)
                        return True
                    print(f"File is already encrypted with SOPS: {filename}")
                    return False
    except yaml.YAMLError as e:
        print(
            f"ERROR: Error parsing YAML file {filename}: {e}", file=sys.stderr
        )
    return False


def contains_secret(filename: str, hook_id: str) -> bool:
    """Checks if the given filename contains an unencrypted secret.

    Searches for patterns.

    Args:
        filename: The name of the file.
        hook_id: The identifier of the hook.

    Returns:
        True if the file contains an unencrypted secret, False otherwise.
    """
    if check_if_encrypted(filename):
        print(
            f"File is already encrypted with SOPS: {filename}", file=sys.stderr
        )
        if check_contains_key_age_public(filename):
            print(
                "WARNING: Detected key_age_public in encrypted file: "
                f"{filename}",
                file=sys.stderr,
            )
        return False

    with open(filename, "r", encoding="utf-8") as file:
        file_content = file.read()

    check_function = SECRET_CHECKS.get(hook_id)
    if check_function and check_function(file_content):
        print(
            "WARNING: Detected {hook_id.replace('-', ' ').title()} in file: "
            f"{filename}",
            file=sys.stderr,
        )
        encrypt_file(filename)
        return True
    return False


def is_sops_installed() -> bool:
    """Checks if SOPS is installed by attempting to call it.

    Returns:
        True if SOPS is installed, False otherwise.
    """
    try:
        subprocess.run(
            ["sops", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def prompt_install_sops() -> bool:
    """Prompts the user to install SOPS if it is not installed.

    Returns:
        True if the user approves and SOPS is installed, False otherwise.
    """
    print(
        "ERROR: SOPS is not installed. It is required to encrypt secrets.",
        file=sys.stderr,
    )
    approval = (
        input("Would you like to install SOPS now? [y/N]: ").strip().lower()
    )
    if approval == "y":
        try:
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    "requirements.txt",
                ],
                check=True,
            )
            print("SOPS has been successfully installed.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to install SOPS: {e}", file=sys.stderr)
            return False
    else:
        print("SOPS installation was not approved. Exiting.", file=sys.stderr)
        return False


def check_keys_present() -> bool:
    """Checks if the necessary age or gpg keys are present.

    Returns:
        True if keys are present, False otherwise.
    """
    if not key_age_public or not key_age_private:
        print(
            "ERROR: No age or gpg keys found. Instructions can be found at: "
            "https://github.com/djh00t/sops-pre-commit/blob/main/docs/encrypt"
            "ion-keys-not-found.md or exclude the file",
            file=sys.stderr,
        )
        return False
    return True


def main(
    argv: Optional[list[str]] = None,
    exclude_patterns: Optional[list[str]] = None,
) -> int:
    """Main function that parses arguments and checks each file for secrets and
    encryption.

    Args:
        argv: A list of command-line arguments.
        exclude_patterns: A list of regex patterns to exclude.

    Returns:
        An integer exit code.
    """
    # Parse arguments first to handle help and other options.
    parser = argparse.ArgumentParser(
        description="Checks for unencrypted Kubernetes secrets or other speci"
        "fied secrets and encrypts them using SOPS if found.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("filenames", nargs="*", help="Filenames to check.")
    parser.add_argument(
        "--hook-id",
        help="Identifier of the hook (e.g., aws-access-key-id, kubernetes-sec"
        "ret).",
        required=True,
    )
    parser.add_argument(
        "--exclude",
        nargs="*",
        help="Regex patterns for files to exclude from checks.",
        default=[],
    )
    args = parser.parse_args(argv)

    secrets_detected = False

    # Check if SOPS is installed and prompt the user to install it if not.
    if not is_sops_installed() and not prompt_install_sops():
        return 1

    exclude_patterns = args.exclude or []

    # Check for hook_id arguments
    hook_id = args.hook_id

    # Setup files_with_secrets list
    files_with_secrets = []

    # Check for Kubernetes secrets
    if hook_id == "kubernetes-secret":
        # Check for Kubernetes secrets in files
        files_with_secrets = [
            f
            for f in args.filenames
            if not is_excluded(f, exclude_patterns)
            and check_kubernetes_secret_file(f)
        ]
    else:
        # Check for secrets in files
        files_with_secrets = [
            f
            for f in args.filenames
            if not is_excluded(f, exclude_patterns)
            and contains_secret(f, hook_id)
        ]

    # Check if the necessary keys are present, if not prompt user to generate
    # them.
    if files_with_secrets and not check_keys_present():
        return 1

    # Check for hook_id arguments
    hook_id = args.hook_id

    # Setup files_with_secrets list
    files_with_secrets = []

    # Check for Kubernetes secrets
    if hook_id == "kubernetes-secret":
        # Check for Kubernetes secrets in files
        files_with_secrets = [
            f
            for f in args.filenames
            if not is_excluded(f, exclude_patterns)
            and check_kubernetes_secret_file(f)
        ]
    else:
        # Check for secrets in files
        files_with_secrets = [
            f
            for f in args.filenames
            if not is_excluded(f, exclude_patterns)
            and contains_secret(f, hook_id)
        ]

    return_code = 0

    # Loop through files_with_secrets and log warnings
    for file_with_secrets in files_with_secrets:
        secrets_detected = True
        print(
            "WARNING: Unencrypted Kubernetes secret detected in file: "
            f"{file_with_secrets}",
            file=sys.stderr,
        )
        return_code = 1
    # Log success message if secrets were detected and encrypted
    if secrets_detected:
        print("Secrets were detected and encrypted.", file=sys.stderr)
    return return_code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))  # pylint: disable=no-value-for-parameter
