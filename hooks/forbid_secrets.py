"""
This script is a pre-commit hook that checks for unencrypted Kubernetes secrets in files.
It uses regular expressions to identify secret definitions and ignores them if they are
encrypted with SOPS or marked for deletion in Kustomize patches. If an unencrypted secret
is found, it exits with a non-zero status code to block the commit.
"""
from __future__ import print_function
SOPS_REGEX = r"ENC.AES256"
KUSTOMIZE_REGEX = r"^\$patch:\sdelete"
DEBUG_LEVEL = 0  # Set the desired debug level here, 0 for no debug output
EXCLUDE_PATTERNS = []
root_dir = subprocess.getoutput('git rev-parse --show-toplevel')
key_age_public = open(os.path.join(root_dir, '.age.pub')).read().strip()
CREATION_RULES_PATH_REGEX = None  # This will be set after reading from .sops.yaml

SOPS_REGEX = r"ENC.AES256"
KUSTOMIZE_REGEX = r"^\$patch:\sdelete"

CREATION_RULES_PATH_REGEX = None  # This will be set after reading from .sops.yaml

root_dir = subprocess.getoutput('git rev-parse --show-toplevel')
key_age_public = open(os.path.join(root_dir, '.age.pub')).read().strip()

DEBUG_LEVEL = 0  # Set the desired debug level here, 0 for no debug output

def debug(level, message):
    """
    Prints a debug message with a given level.
    """
    if level <= DEBUG_LEVEL:
        print("DEBUG: {}".format(message))

def encrypt_file_if_needed(file_path):
    """
    Encrypts the given file using SOPS if it is not already encrypted.
    """
    if check_if_encrypted(file_path):
        debug(0, "File is already encrypted with SOPS: {}".format(file_path))
        return
    debug(0, "File Status:   DECRYPTED")
    debug(0, "Action:        ENCRYPTING")
    try:
        subprocess.run(['sops', '--encrypt', '--in-place', file_path], check=True)
    except subprocess.CalledProcessError as e:
        debug(2, "Failed to encrypt file:", file_path)
        debug(2, "Error:", str(e))
        raise
    debug(0, "File Status:   ENCRYPTED")

def check_if_encrypted(file_path):
    """
    Checks if the given file is encrypted by looking for the SOPS encryption marker.
    """
    with open(file_path, 'r') as file:
        content = file.read()
    return '- recipient: ' + key_age_public in content

def main():
    """
    Main function that parses arguments and checks each file for secrets.
    """
    parser = argparse.ArgumentParser(description="Checks for unencrypted Kubernetes secrets.")
    parser.add_argument("filenames", nargs="*", help="Filenames to check.")
    parser.add_argument("--hook-id", help="Identifier of the hook.", required=True)
    parser.add_argument("--exclude", nargs="*", help="Regex patterns for files to exclude from checks.", default=[])
    args = parser.parse_args()

    EXCLUDE_PATTERNS = args.exclude
    hook_id = args.hook_id

    files_with_secrets = []
    if hook_id == 'kubernetes-secret':
        files_with_secrets = [f for f in args.filenames if not is_excluded(f, EXCLUDE_PATTERNS) and check_kubernetes_secret_file(f)]
    else:
        files_with_secrets = [f for f in args.filenames if not is_excluded(f, EXCLUDE_PATTERNS) and contains_secret(f, hook_id)]

    return_code = 0
    for file_with_secrets in files_with_secrets:
        print(
            "Unencrypted Kubernetes secret detected in file: {0}".format(
                file_with_secrets
            )
        )
        encrypt_file_if_needed(file_with_secrets)
        return_code = 1
    if return_code:
        print("Secrets were detected and encrypted.")
    return return_code

if __name__ == "__main__":
    sys.exit(main())


if __name__ == "__main__":
    """
    If this script is executed as the main module, start the main function.
    """
    sys.exit(main(sys.argv[1:]))

SOPS_REGEX = r"ENC.AES256"
KUSTOMIZE_REGEX = r"^\$patch:\sdelete"

CREATION_RULES_PATH_REGEX = None  # This will be set after reading from .sops.yaml

DEBUG_LEVEL = 0  # Set the desired debug level here, 0 for no debug output

def debug(level, message):
    """
    Prints a debug message with a given level.
    """
    if level <= DEBUG_LEVEL:
        print("DEBUG: {}".format(message))


def check_aws_access_key_id(content):
    return re.search(r'AKIA[0-9A-Z]{16}', content)

def check_aws_secret_access_key(content):
    return re.search(r'(?i)aws(.{0,20})?[\'"\s]?([0-9a-zA-Z/+]{40})', content)

def check_rsa_private_key(content):
    return re.search(r'-----BEGIN RSA PRIVATE KEY-----', content)

def check_ssh_private_key(content):
    return re.search(r'-----BEGIN (EC|OPENSSH|DSA|RSA) PRIVATE KEY-----\s*([A-Za-z0-9+/=\s]+)\s*-----END (EC|OPENSSH|DSA|RSA) PRIVATE KEY-----', content, re.DOTALL)

def check_github_access_token(content):
    return re.search(r'ghp_[0-9a-zA-Z]{36}', content)

def check_generic_api_key(content):
    return re.search(r'(?i)api(_|-)?key[\'"\\s]?[:=][\'"\\s]?[0-9a-zA-Z]{32,}', content)

def check_gcp_api_key(content):
    return re.search(r'AIza[0-9A-Za-z\\-_]{35}', content)

def check_jwt(content):
    return re.search(r'eyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]*', content)

def check_slack_webhook_url(content):
    return re.search(r'https://hooks.slack.com/services/T[A-Z0-9]{8}/B[A-Z0-9]{8}/[a-zA-Z0-9]{24}', content)

def check_google_oauth_client_secret(content):
    return re.search(r'(?i)"client_secret":"[a-zA-Z0-9-_]{24}', content)

SECRET_CHECKS = {
    'aws-access-key-id': check_aws_access_key_id,
    'aws-secret-access-key': check_aws_secret_access_key,
    'rsa-private-key': check_rsa_private_key,
    'ssh-private-key': check_ssh_private_key,
    'github-access-token': check_github_access_token,
    'generic-api-key': check_generic_api_key,
    'gcp-api-key': check_gcp_api_key,
    'jwt': check_jwt,
    'slack-webhook-url': check_slack_webhook_url,
    'google-oauth-client-secret': check_google_oauth_client_secret,
}
EXCLUDE_PATTERNS = []

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
        
def is_excluded(filename, exclude_patterns):
    """
    Checks if the given filename matches any of the exclude patterns.
    """
    return any(re.search(pattern, filename) for pattern in exclude_patterns)

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



root_dir = subprocess.getoutput('git rev-parse --show-toplevel')
key_age_public = open(os.path.join(root_dir, '.age.pub')).read().strip()

def check_if_encrypted(file_path):
    """
    Checks if the given file is encrypted by looking for the SOPS encryption marker.
    """
    with open(file_path, 'r') as file:
        content = file.read()
    return '- recipient: ' + key_age_public in content

def check_kubernetes_secret_file(filename):
    """
    Checks if the given filename contains a Kubernetes secret.
    """
    try:
        with open(filename, 'r') as file:
            documents = yaml.safe_load_all(file)
            for doc in documents:
                if is_kubernetes_secret(doc):
                    if not check_if_encrypted(filename):
                        print(f"Detected unencrypted Kubernetes Secret in file: {filename}")
                        encrypt_file(filename)
                        return True
                    else:
                        print(f"File is already encrypted with SOPS: {filename}")
                        return False
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file {filename}: {e}")
    return False

def contains_secret(filename, hook_id):
    """
    Checks if the given filename contains an unencrypted secret by searching for patterns.
    """
    if check_if_encrypted(filename):
        debug(0, "File is already encrypted with SOPS: {}".format(filename))
        return False

    with open(filename, 'r') as file:
        file_content = file.read()

    check_function = SECRET_CHECKS.get(hook_id)
    if check_function and check_function(file_content):
        print(f"Detected {hook_id.replace('-', ' ').title()} in file: {filename}")
        encrypt_file(filename)
        return True
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
    global EXCLUDE_PATTERNS
    secrets_detected = False
    if not is_sops_installed():
        if not prompt_install_sops():
            return 1

    global CREATION_RULES_PATH_REGEX
    CREATION_RULES_PATH_REGEX = load_creation_rules_path_regex()

    """
    Main function that parses arguments and checks each file for secrets.
    """
    parser = argparse.ArgumentParser(description="Checks for unencrypted Kubernetes secrets.")
    parser.add_argument("filenames", nargs="*", help="Filenames to check.")
    parser.add_argument("--hook-id", help="Identifier of the hook.", required=True)
    parser.add_argument("--exclude", nargs="*", help="Regex patterns for files to exclude from checks.", default=[])
    args = parser.parse_args(argv)

    EXCLUDE_PATTERNS = args.exclude
    hook_id = args.hook_id

    files_with_secrets = []
    if hook_id == 'kubernetes-secret':
        files_with_secrets = [f for f in args.filenames if not is_excluded(f, EXCLUDE_PATTERNS) and check_kubernetes_secret_file(f)]
    else:
        files_with_secrets = [f for f in args.filenames if not is_excluded(f, EXCLUDE_PATTERNS) and contains_secret(f, hook_id)]

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
