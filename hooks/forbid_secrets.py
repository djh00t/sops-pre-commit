#!/usr/bin/env python3
"""
This module provides functionality to check for unencrypted secrets in
files, encrypt them using SOPS (Secrets OPerationS), and handle
encryption/decryption operations. It supports various secret types and
can handle Kubernetes secrets specifically.
"""

import argparse
import os
import re
import socket
import subprocess
import sys
from datetime import datetime
from typing import List, Optional

from ruamel.yaml import YAML, YAMLError

# Constants
ROOT_DIR = subprocess.getoutput("git rev-parse --show-toplevel")
AGE_PUBLIC_KEY_PATH = os.path.join(ROOT_DIR, ".age.pub")
AGE_PRIVATE_KEY_PATH = os.path.join(ROOT_DIR, "age.agekey")

# Debug levels
DEBUG_LEVELS = {
    "INFO": 0,
    "WARN": 1,
    "ERROR": 2,
    "DEBUG": 3,
    "TRACE": 4,
    "FATAL": 5,
}


class SecretsManager:
    """Manages encryption and decryption of secrets using SOPS."""

    def __init__(self):
        self.yaml = YAML(typ="rt")
        self.key_age_public = self._read_key_file(AGE_PUBLIC_KEY_PATH)
        self.key_age_private = self._read_key_file(
            AGE_PRIVATE_KEY_PATH, line_number=1
        )
        self.warn_only_mode = not (
            self.key_age_public and self.key_age_private
        )

    def _read_key_file(
        self, file_path: str, line_number: Optional[int] = None
    ) -> Optional[str]:
        """Reads a key from a file.

        Args:
            file_path: The path to the key file.
            line_number: The line number to read (optional).

        Returns:
            The key as a string, or None if the file is not found or an error
            occurs.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                if line_number is not None:
                    return file.readlines()[line_number].strip()
                return file.read().strip()
        except FileNotFoundError:
            self.debug(1, f"Warning: Key file not found: {file_path}")
            return None
        except IOError as e:
            self.debug(2, f"Error reading key file {file_path}: {str(e)}")
            return None

    def debug(self, level: int, *messages: str) -> None:
        """Logs debug messages with different severity levels.

        Args:
            level: The debug level (0-5).
            *messages: The messages to log.
        """
        debug_levels = ["INFO", "WARN", "ERROR", "DEBUG", "TRACE", "FATAL"]
        color_codes = [
            "\033[1;32m",
            "\033[1;33m",
            "\033[1;31m",
            "\033[1;34m",
            "\033[1;38;5;208m",
            "\033[1;3;31m",
        ]
        reset_color = "\033[0m"
        current_date = datetime.now().strftime("%b %d %H:%M:%S")
        hostname = socket.gethostname()

        if (
            level <= DEBUG_LEVELS.get(os.environ.get("DEBUG_LEVEL", "WARN"), 1)
            or level == DEBUG_LEVELS["FATAL"]
        ):
            color = color_codes[level]
            level_str = debug_levels[level]
            print(
                f"{current_date} {hostname} {color}{level_str}:{reset_color}"
                f"\t{color}{' '.join(messages)}{reset_color}"
            )

    def encrypt_file(self, file_path: str) -> None:
        """Encrypts a file using SOPS.

        Args:
            file_path: The path to the file to encrypt.
        """
        if self.warn_only_mode:
            self.debug(1, f"WARN ONLY MODE: Would encrypt {file_path}")
            return

        if not self.check_if_encrypted(file_path):
            self.debug(0, "File Status: DECRYPTED")
            self.debug(0, "Action: ENCRYPTING")
            try:
                subprocess.run(
                    ["sops", "--encrypt", "--in-place", file_path], check=True
                )
                self.debug(0, "File Status: ENCRYPTED")
            except subprocess.CalledProcessError as e:
                self.debug(2, f"ERROR: Failed to encrypt file: {file_path}")
                self.debug(2, f"ERROR: {str(e)}")
        else:
            self.debug(0, "File Status: ENCRYPTED")
            self.debug(0, "Action: SKIPPING")

    def decrypt_file(self, file_path: str) -> None:
        """Decrypts a file using SOPS.

        Args:
            file_path: The path to the file to decrypt.
        """
        if self.warn_only_mode:
            self.debug(1, f"WARN ONLY MODE: Would decrypt {file_path}")
            return

        if self.check_if_encrypted(file_path):
            self.debug(0, "File Status: ENCRYPTED")
            self.debug(0, "Action: DECRYPTING")
            try:
                subprocess.run(
                    ["sops", "--decrypt", "--in-place", file_path], check=True
                )
                self.debug(0, "File Status: DECRYPTED")
            except subprocess.CalledProcessError as e:
                self.debug(2, f"ERROR: Failed to decrypt file: {file_path}")
                self.debug(2, f"ERROR: {str(e)}")
        else:
            self.debug(0, "File Status: DECRYPTED")
            self.debug(0, "Action: SKIPPING")

    def check_if_encrypted(self, file_path: str) -> bool:
        """Checks if a file is encrypted.

        Args:
            file_path: The path to the file to check.

        Returns:
            True if the file is encrypted, False otherwise.
        """
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        encrypted_file_regex = re.compile(
            r"^(-----BEGIN (AGE ENCRYPTED FILE|PGP MESSAGE)-----[\s\S]*?"
            r"-----END (AGE ENCRYPTED FILE|PGP MESSAGE)-----|ENC\[AES256_GCM,"
            r"data:.*?\]|encrypted_regex:.*)$",
            re.MULTILINE,
        )
        return bool(encrypted_file_regex.search(content))

    def check_kubernetes_secret_file(self, filename: str) -> bool:
        """Checks if a Kubernetes secret file is encrypted and encrypts it if
        not.

        Args:
            filename: The path to the Kubernetes secret file.

        Returns:
            True if the file was encrypted, False otherwise.
        """
        try:
            with open(filename, "r", encoding="utf-8") as file:
                documents = self.yaml.load_all(file)
                for doc in documents:
                    if isinstance(doc, dict) and doc.get("kind") == "Secret":
                        if not self.check_if_encrypted(filename):
                            self.debug(
                                1,
                                "WARNING: Detected unencrypted Kubernetes "
                                "Secret in file: {filename}",
                            )
                            self.encrypt_file(filename)
                            return True
                        self.debug(
                            0,
                            f"File is already encrypted with SOPS: "
                            f"{filename}",
                        )
                        return False
        except YAMLError as e:
            self.debug(2, f"ERROR: Error parsing YAML file {filename}: {e}")
        return False

    def contains_secret(self, filename: str, hook_id: str) -> bool:
        """Checks if a file contains a secret based on the hook identifier.

        Args:
            filename: The path to the file to check.
            hook_id: The identifier of the hook to use for checking.

        Returns:
            True if a secret is found and the file is encrypted, False
            otherwise.
        """
        if self.check_if_encrypted(filename):
            self.debug(0, f"File is already encrypted: {filename}")
            return False

        try:
            with open(filename, "r", encoding="utf-8") as file:
                file_content = file.read()

            check_function = SECRET_CHECKS.get(hook_id)
            if check_function and check_function(file_content):
                self.debug(
                    1,
                    f"WARNING: Detected potential "
                    f"{hook_id.replace('-', ' ').title()} in file: {filename}",
                )
                self.encrypt_file(filename)
                return True
        except IOError as e:
            self.debug(2, f"Error reading file {filename}: {str(e)}")

        return False


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
        r"-----END RSA PRIVATE KEY-----",
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
        r"PRIVATE KEY)-----",
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


def is_excluded(filename: str, exclude_patterns: List[str]) -> bool:
    """Checks if a file is excluded based on the provided patterns.

    Args:
        filename: The name of the file to check.
        exclude_patterns: A list of regex patterns to match against the
        filename.

    Returns:
        True if the file is excluded, False otherwise.
    """
    return any(re.search(pattern, filename) for pattern in exclude_patterns)


def main(argv: Optional[List[str]] = None) -> int:
    """Main function to manage secrets encryption and decryption using SOPS.

    Args:
        argv: List of command-line arguments.

    Returns:
        Exit code.
    """
    parser = argparse.ArgumentParser(
        description="Manage secrets encryption and decryption using SOPS."
    )
    parser.add_argument("filenames", nargs="*", help="Filenames to check.")
    parser.add_argument(
        "--hook-id",
        help="Identifier of the hook (e.g., aws-access-key-id, "
        "kubernetes-secret).",
        required=True,
    )
    parser.add_argument(
        "--exclude",
        nargs="*",
        help="Regex patterns for files to exclude from checks.",
        default=[],
    )
    parser.add_argument(
        "--action",
        choices=["encrypt", "decrypt"],
        default="encrypt",
        help="Action to perform on the files.",
    )
    args = parser.parse_args(argv)

    secrets_manager = SecretsManager()

    if secrets_manager.warn_only_mode:
        secrets_manager.debug(
            1,
            "WARNING: Running in WARN ONLY mode. Secrets will not be "
            "encrypted.",
        )
        secrets_manager.debug(
            1,
            "Please install SOPS and generate age keys to enable encryption.",
        )

    exclude_patterns = args.exclude
    hook_id = args.hook_id
    action = args.action

    files_with_secrets = []

    for filename in args.filenames:
        if is_excluded(filename, exclude_patterns):
            continue

        if is_excluded(filename, exclude_patterns):
            continue

        if (
            hook_id == "kubernetes-secret"
            and secrets_manager.check_kubernetes_secret_file(filename)
        ):
            files_with_secrets.append(filename)
        elif hook_id in SECRET_CHECKS and secrets_manager.contains_secret(
            filename, hook_id
        ):
            files_with_secrets.append(filename)
        elif hook_id not in SECRET_CHECKS:
            secrets_manager.debug(1, f"Warning: Unknown hook-id '{hook_id}'")

        if action == "decrypt":
            secrets_manager.decrypt_file(filename)

    if files_with_secrets:
        for file_with_secrets in files_with_secrets:
            secrets_manager.debug(
                1,
                "WARNING: Potential unencrypted secret "
                f"detected in file: {file_with_secrets}",
            )
        if secrets_manager.warn_only_mode:
            secrets_manager.debug(
                1,
                "Secrets were detected. Please review and encrypt manually "
                "if needed.",
            )
            return 1
        secrets_manager.debug(
            0, "Secrets were detected and encrypted where possible."
        )

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
