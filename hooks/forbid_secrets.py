import argparse
import logging
import os
import re
import subprocess
import sys

import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KUSTOMIZE_REGEX = r"^\$patch:\sdelete"


root_dir = subprocess.getoutput("git rev-parse --show-toplevel")

def read_key_file(file_path: str, line_number: int = None) -> str:
    """Reads a key from a file.

    If line_number is specified, reads that specific line.

    Args:
        file_path: The path to the file.
        line_number: The line number to read (optional).

    Returns:
        The content of the file or the specific line.
    """
    try:
        with open(file_path, "r") as file:
            if line_number is not None:
                return file.readlines()[line_number].strip()
            return file.read().strip()
    except FileNotFoundError:
        return None

key_age_public = read_key_file(os.path.join(root_dir, ".age.pub"))
key_age_private = read_key_file(os.path.join(root_dir, "age.agekey"), line_number=1)


def encrypt_file(file_path: str) -> None:
    """Encrypts the given file using SOPS if it is not already encrypted.

    Args:
        file_path: The path to the file to encrypt.
    """
    if not check_if_encrypted(file_path):
        logger.info("File Status:   DECRYPTED")
        logger.info("Action:        ENCRYPTING")
        try:
            subprocess.run(["sops", "--encrypt", "--in-place", file_path], check=True)
        except subprocess.CalledProcessError as e:
            logger.error("Failed to encrypt file: %s", file_path)
            logger.error("Error: %s", str(e))
            raise
        logger.info("File Status:   ENCRYPTED")
    else:
        logger.info("File Status:   ENCRYPTED")
        logger.info("Action:        SKIPPING")


def check_contains_key_age_public(file_path: str) -> bool:
    """Checks if the given file contains the key_age_public string.

    Args:
        file_path: The path to the file.

    Returns:
        True if the file contains the key_age_public string, False otherwise.
    """
    try:
        with open(file_path, "r") as file:
            content = file.read()
        if key_age_public and key_age_public in content:
            return True
    except FileNotFoundError:
        logger.error("File %s not found.", key_age_public)
    return False


def check_if_encrypted(file_path: str) -> bool:
    """Checks if the given file is encrypted.

    Looks for the SOPS encryption markers.

    Args:
        file_path: The path to the file.

    Returns:
        True if the file is encrypted, False otherwise.
    """
    with open(file_path, "r") as file:
        content = file.read()

    encrypted_file_regex = re.compile(
        r"^(-----BEGIN (AGE ENCRYPTED FILE|PGP MESSAGE)-----[\s\S]*?-----END (AGE ENCRYPTED FILE|PGP MESSAGE)-----|ENC\[AES256_GCM,data:.*?\]|encrypted_regex:.*)$",
        re.MULTILINE,
    )

    return bool(encrypted_file_regex.search(content))


def check_aws_access_key_id(content: str) -> re.Match | None:
    return re.search(r"AKIA[0-9A-Z]{16}", content)


def check_aws_secret_access_key(content: str) -> re.Match | None:
    return re.search(r'(?i)aws(.{0,20})?[\'"\s]?([0-9a-zA-Z/+]{40})', content)


def check_rsa_private_key(content: str) -> re.Match | None:
    return re.search(
        r"-----BEGIN RSA PRIVATE KEY-----\s*([A-Za-z0-9+/=\s]+)\s*-----END RSA PRIVATE KEY-----",
        content,
        re.DOTALL,
    )


def check_ssh_private_key(content: str) -> re.Match | None:
    return re.search(
        r"-----BEGIN ((EC|OPENSSH|DSA) PRIVATE KEY|RSA PRIVATE KEY)-----\s*([A-Za-z0-9+/=\s]+)\s*-----END ((EC|OPENSSH|DSA) PRIVATE KEY|RSA PRIVATE KEY)-----",
        content,
        re.DOTALL,
    )


def check_github_access_token(content: str) -> re.Match | None:
    return re.search(r"ghp_[0-9a-zA-Z]{36}", content)


def check_generic_api_key(content: str) -> re.Match | None:
    return re.search(r'(?i)api(_|-)?key[\'"\\s]?[:=][\'"\\s]?[0-9a-zA-Z]{32,}', content)


def check_gcp_api_key(content: str) -> re.Match | None:
    return re.search(r"AIza[0-9A-Za-z\\-_]{35}", content)


def check_jwt(content: str) -> re.Match | None:
    return re.search(
        r"eyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]*", content
    )


def check_slack_webhook_url(content: str) -> re.Match | None:
    return re.search(
        r"https://hooks.slack.com/services/T[A-Z0-9]{8}/B[A-Z0-9]{8}/[a-zA-Z0-9]{24}",
        content,
    )


def check_google_oauth_client_secret(content: str) -> re.Match | None:
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

EXCLUDE_PATTERNS = []




def is_excluded(filename: str, exclude_patterns: list[str]) -> bool:
    """Checks if the given filename matches any of the exclude patterns.

    Args:
        filename: The name of the file.
        exclude_patterns: A list of regex patterns to exclude.

    Returns:
        True if the filename matches any of the exclude patterns, False otherwise.
    """
    return any(re.search(pattern, filename) for pattern in exclude_patterns)


def is_kubernetes_secret(data: dict) -> bool:
    """Determines if the provided data structure represents a Kubernetes secret.

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
        with open(filename, "r") as file:
            documents = yaml.safe_load_all(file)
            for doc in documents:
                if is_kubernetes_secret(doc):
                    if not check_if_encrypted(filename):
                        logger.warning("Detected unencrypted Kubernetes Secret in file: %s", filename)
                        encrypt_file(filename)
                        return True
                    else:
                        logger.info("File is already encrypted with SOPS: %s", filename)
                        return False
    except yaml.YAMLError as e:
        logger.error("Error parsing YAML file %s: %s", filename, e)
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
        logger.info("File is already encrypted with SOPS: %s", filename)
        if check_contains_key_age_public(filename):
            logger.warning("Detected key_age_public in encrypted file: %s", filename)
        return False

    with open(filename, "r") as file:
        file_content = file.read()

    check_function = SECRET_CHECKS.get(hook_id)
    if check_function and check_function(file_content):
        logger.warning("Detected %s in file: %s", hook_id.replace('-', ' ').title(), filename)
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
    logger.error("SOPS is not installed. It is required to encrypt secrets.")
    approval = input("Would you like to install SOPS now? [y/N]: ").strip().lower()
    if approval == "y":
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                check=True,
            )
            logger.info("SOPS has been successfully installed.")
            return True
        except subprocess.CalledProcessError as e:
            logger.error("Failed to install SOPS: %s", e)
            return False
    else:
        logger.info("SOPS installation was not approved. Exiting.")
        return False


def main(argv: list[str] = None) -> int:
    """Main function that parses arguments and checks each file for secrets and encryption.

    Args:
        argv: A list of command-line arguments.

    Returns:
        An integer exit code.
    """
    global EXCLUDE_PATTERNS
    secrets_detected = False
    if not is_sops_installed():
        if not prompt_install_sops():
            return 1


    parser = argparse.ArgumentParser(
        description="Checks for unencrypted Kubernetes secrets."
    )
    parser.add_argument("filenames", nargs="*", help="Filenames to check.")
    parser.add_argument("--hook-id", help="Identifier of the hook.", required=True)
    parser.add_argument(
        "--exclude",
        nargs="*",
        help="Regex patterns for files to exclude from checks.",
        default=[],
    )
    args = parser.parse_args(argv)

    EXCLUDE_PATTERNS = args.exclude
    hook_id = args.hook_id

    files_with_secrets = []
    if hook_id == "kubernetes-secret":
        files_with_secrets = [
            f
            for f in args.filenames
            if not is_excluded(f, EXCLUDE_PATTERNS) and check_kubernetes_secret_file(f)
        ]
    else:
        files_with_secrets = [
            f
            for f in args.filenames
            if not is_excluded(f, EXCLUDE_PATTERNS) and contains_secret(f, hook_id)
        ]

    return_code = 0
    for file_with_secrets in files_with_secrets:
        secrets_detected = True
        logger.warning(
            "Unencrypted Kubernetes secret detected in file: %s", file_with_secrets
        )
        return_code = 1
    if secrets_detected:
        logger.info("Secrets were detected and encrypted.")
    return return_code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))  # pylint: disable=no-value-for-parameter
