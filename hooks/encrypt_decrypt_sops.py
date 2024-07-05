#!/usr/bin/env python3

"""
This script provides functionality to encrypt or decrypt files using SOPS
(Secrets OPerationS). It can handle individual files, directories, and patterns
with wildcards. The script determines whether files are already encrypted or
decrypted and performs the opposite action, skipping files that do not require
processing.
"""

import argparse
import os
import re
import socket
import subprocess
import sys
from datetime import datetime

from ruamel.yaml import YAML

root_dir = subprocess.getoutput("git rev-parse --show-toplevel")

yaml = YAML(typ="rt")

try:
    with open(
        os.path.join(root_dir, ".age.pub"), "r", encoding="utf-8"
    ) as pub_file:
        KEY_AGE_PUBLIC = pub_file.read().strip()
except FileNotFoundError:
    KEY_AGE_PUBLIC = ""

try:
    with open(
        os.path.join(root_dir, "age.agekey"), "r", encoding="utf-8"
    ) as key_file:
        KEY_AGE_PRIVATE = key_file.readlines()[1].strip()
except FileNotFoundError:
    KEY_AGE_PRIVATE = ""

DEBUG_LEVEL = 2  # Default debug level set to show warnings and errors


def debug(debug_msg_level, *debug_msg):
    """
    Outputs debug messages to the console with varying levels of severity.
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
    if DEBUG_LEVEL >= debug_msg_level or debug_msg_level == 5:
        color = color_codes[debug_msg_level]
        level_str = debug_levels[debug_msg_level]
        print(
            f"{current_date} {hostname} {color}{level_str}:{reset_color}\t"
            f"{color}{' '.join(debug_msg)}{reset_color}"
        )


def check_if_encrypted(file_path):
    """
    Checks if the given file is encrypted by looking for the SOPS encryption
    marker.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    return "- recipient: " + KEY_AGE_PUBLIC in content


def decrypt_file(file_path):
    """
    Decrypts the given file using SOPS if it is encrypted.
    """
    if check_if_encrypted(file_path):
        debug(0, "File Status:   ENCRYPTED")
        debug(0, "Action:        DECRYPTING")
        subprocess.run(
            ["sops", "--decrypt", "--in-place", file_path], check=True
        )
        debug(0, "File Status:   DECRYPTED")
    else:
        debug(0, "File Status:   DECRYPTED")
        debug(0, "Action:        SKIPPING")


def encrypt_file(file_path):
    """
    Encrypts the given file using SOPS if it is not already encrypted.
    """
    if not check_if_encrypted(file_path):
        debug(0, "File Status:   DECRYPTED")
        debug(0, "Action:        ENCRYPTING")
        try:
            subprocess.run(
                ["sops", "--encrypt", "--in-place", file_path], check=True
            )
        except subprocess.CalledProcessError as e:
            debug(2, "Failed to encrypt file:", file_path)
            debug(2, "Error:", str(e))
            raise
        debug(0, "File Status:   ENCRYPTED")
    else:
        debug(0, "File Status:   ENCRYPTED")
        debug(0, "Action:        SKIPPING")


def validate_file(file_path):
    """
    Validates if the given path is a file and returns the normalized absolute
    path.
    """
    if os.path.isfile(file_path):
        debug(3, "Validate file:", file_path)
        return os.path.normpath(file_path)
    debug(2, "File not found:", file_path)
    return None


def explode_wildcards(pattern):
    """
    Expands wildcard patterns to a list of matching file paths.
    """
    return [
        os.path.join(os.getcwd(), f)
        for f in sorted(
            subprocess.getoutput(f"ls -A {pattern} 2> /dev/null").split()
        )
    ]


def explode_directories(directory):
    """
    Recursively walks through a directory and returns a list of all file paths.
    """
    valid_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            valid_files.append(os.path.join(root, file))
    return valid_files


def value_router(value):
    """
    Determines the type of the given value (file, directory, or wildcard) and
    routes it accordingly.
    """
    if os.path.isfile(value):
        debug(0, "Routing:", value, "is a file")
        return [validate_file(value)]
    if os.path.isdir(value):
        debug(0, "Routing:", value, "is a directory")
        return explode_directories(value)
    if re.search(r"[\*\?\[\]\{\}\|]", value):
        debug(0, "Routing:", value, "is a regex/wildcard value")
        return explode_wildcards(value)

    debug(2, "Invalid value:", value)
    return []


def handle_args(args):
    """
    Processes command-line arguments and returns a list of files to be
    processed.
    """
    files_to_process = []
    for arg in args:
        debug(3, "Processing:", arg)
        files_to_process.extend(value_router(arg))
    return files_to_process


def main(local_debug_level=DEBUG_LEVEL):
    """
    The main function that parses arguments and processes files for encryption
    or decryption.
    """
    parser = argparse.ArgumentParser(
        description="Encrypt or Decrypt files with SOPS"
    )
    parser.print_help = parser.print_help
    parser.add_argument(
        "files", nargs="+", help="Files or directories to process"
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug output"
    )
    parsed_args = parser.parse_args()

    local_debug_level = 3 if parsed_args.debug else local_debug_level
    # Use the module level debug_level if not overridden by parsed_args.debug

    action = (
        "encrypt" if "encrypt" in os.path.basename(__file__) else "decrypt"
    )

    for file_path in parsed_args.files:
        if action == "encrypt" and not check_if_encrypted(file_path):
            debug(0, "Encrypting:", file_path)
            encrypt_file(file_path)
        if action == "decrypt" and check_if_encrypted(file_path):
            debug(0, "Decrypting:", file_path)
            decrypt_file(file_path)
        else:
            debug(0, "Skipping:", file_path)


if __name__ == "__main__":
    with open(
        os.path.join(root_dir, ".age.pub"), encoding="utf-8"
    ) as pub_file:
        KEY_AGE_PUBLIC = pub_file.read().strip()
    with open(
        os.path.join(root_dir, "age.agekey"), encoding="utf-8"
    ) as key_file:
        KEY_AGE_PRIVATE = key_file.readlines()[1].strip()
    files_to_process_list = handle_args(sys.argv[1:])
    main(DEBUG_LEVEL)
