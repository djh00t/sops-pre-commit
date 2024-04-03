"""
This script provides functionality to encrypt or decrypt files using SOPS (Secrets OPerationS).
It can handle individual files, directories, and patterns with wildcards. The script determines
whether files are already encrypted or decrypted and performs the opposite action, skipping files
that do not require processing.
"""
#!/usr/bin/env python3
