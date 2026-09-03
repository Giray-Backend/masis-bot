import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

def _get_cipher():
    key = os.getenv("FERNET_KEY")
    if not key:
        raise ValueError("FERNET_KEY is missing from .env")
    return Fernet(key.encode())

def encrypt_api_key(raw_key: str) -> str:
    cipher = _get_cipher()
    return cipher.encrypt(raw_key.encode()).decode()

def decrypt_api_key(encrypted_key: str) -> str:
    cipher = _get_cipher()
    return cipher.decrypt(encrypted_key.encode()).decode()