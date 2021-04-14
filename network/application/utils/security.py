from tools import ecb_encrypt, ofb_encrypt, ofb_decrypt, cbc_encrypt

from typing import List, Optional


Bytes = List[int]

BLOCK_SIZE = 16


def pad_with_zeros(payload: Bytes, block_size: int):
    if (extra := len(payload) % block_size) != 0:
        payload.extend([0x00] * (block_size - extra))


def calculate_authentication_tag(key: Bytes, payload: Bytes) -> Bytes:
    pad_with_zeros(payload, BLOCK_SIZE)
    ciphertext = cbc_encrypt(key, payload, [0x00] * BLOCK_SIZE)
    # Authentication tag is the last iteration of a CBC cypher truncated to 8 bytes
    return ciphertext[-BLOCK_SIZE:-(BLOCK_SIZE // 2)]


class SecurityUtils:
    def __init__(self):
        self.authentication_key = None
        self.encryption_key = None

        self.set_network_key([0x00] * BLOCK_SIZE)

    def set_network_key(self, network_key: Bytes):
        self.authentication_key = ecb_encrypt(network_key, [0x55] * BLOCK_SIZE)
        self.encryption_key = ecb_encrypt(network_key, [0xAA] * BLOCK_SIZE)

    def encrypt_and_sign(
        self,
        payload: Bytes,
        sender_nonce: Bytes,
        receiver_nonce: Bytes,
        header: int,
        sender: int,
        receiver: int
    ):
        iv = sender_nonce + receiver_nonce
        encrypted = self.encrypt(payload, iv)
        mac = self.sign(encrypted, iv, header, sender, receiver)
        return encrypted, mac

    def decrypt_and_verify(
        self,
        payload: Bytes,
        sender_nonce: Bytes,
        receiver_nonce: Bytes,
        mac: Bytes,
        header: int,
        sender: int,
        receiver: int
    ) -> Optional[Bytes]:
        iv = sender_nonce + receiver_nonce
        if self.verify(payload, iv, header, sender, receiver, mac):
            return self.decrypt(payload, iv)

    def encrypt(self, payload: Bytes, iv: Bytes) -> Bytes:
        return ofb_encrypt(self.encryption_key, payload, iv)

    def decrypt(self, payload: Bytes, iv: Bytes) -> Bytes:
        return ofb_decrypt(self.encryption_key, payload, iv)

    def sign(self, payload: Bytes, iv: Bytes, header: int, sender: int, receiver: int) -> Bytes:
        auth_data = [*iv, header, sender, receiver, len(payload), *payload]
        pad_with_zeros(auth_data, BLOCK_SIZE)
        ciphertext = cbc_encrypt(self.authentication_key, auth_data, [0x00] * BLOCK_SIZE)
        return ciphertext[-BLOCK_SIZE:-(BLOCK_SIZE // 2)]

    def verify(self, payload: Bytes, iv: Bytes, header: int, sender: int, receiver: int, mac: Bytes) -> bool:
        tag = self.sign(payload, iv, header, sender, receiver)
        return tag == mac
