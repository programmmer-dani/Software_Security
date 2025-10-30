

from abc import ABC, abstractmethod

class CryptoBox(ABC):
    @abstractmethod
    def encrypt(self, plaintext: str) -> str:
        pass
    
    @abstractmethod
    def decrypt(self, ciphertext: str) -> str:
        pass
