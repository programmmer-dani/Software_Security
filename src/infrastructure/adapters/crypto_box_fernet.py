# src/infrastructure/adapters/crypto_box_fernet.py

from src.application.ports.crypto_box import CryptoBox
from src.infrastructure.crypto.fernet_box import encrypt, decrypt

class CryptoBoxFernet(CryptoBox):
    def encrypt(self, plaintext: str) -> str:
        return encrypt(plaintext)
    
    def decrypt(self, ciphertext: str) -> str:
        return decrypt(ciphertext)
