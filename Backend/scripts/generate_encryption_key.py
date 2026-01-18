#!/usr/bin/env python3
"""
Generate a Fernet encryption key for securing sensitive data

Run this script to generate a new encryption key:
    python scripts/generate_encryption_key.py

Copy the output to your .env file as ENCRYPTION_KEY
"""

from cryptography.fernet import Fernet


def generate_key():
    """Generate a new Fernet encryption key"""
    key = Fernet.generate_key()
    return key.decode()


if __name__ == "__main__":
    encryption_key = generate_key()
    print("\n" + "=" * 60)
    print("ENCRYPTION KEY GENERATED")
    print("=" * 60)
    print("\nAdd this to your .env file:\n")
    print(f"ENCRYPTION_KEY={encryption_key}")
    print("\n" + "=" * 60)
    print("\nWARNING: Keep this key secure and never commit it to git!")
    print("=" * 60 + "\n")
