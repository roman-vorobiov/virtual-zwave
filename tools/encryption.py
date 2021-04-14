from Cryptodome.Cipher import AES

from typing import List


Bytes = List[int]


def ecb_encrypt(key: Bytes, payload: Bytes) -> Bytes:
    cipher = AES.new(bytes(key), AES.MODE_ECB)
    return list(cipher.encrypt(bytes(payload)))


def ofb_encrypt(key: Bytes, payload: Bytes, initialization_vector: Bytes) -> Bytes:
    cipher = AES.new(bytes(key), AES.MODE_OFB, iv=bytes(initialization_vector))
    return list(cipher.encrypt(bytes(payload)))


def ofb_decrypt(key: Bytes, payload: Bytes, initialization_vector: Bytes) -> Bytes:
    cipher = AES.new(bytes(key), AES.MODE_OFB, iv=bytes(initialization_vector))
    return list(cipher.decrypt(bytes(payload)))


def cbc_encrypt(key: Bytes, payload: Bytes, initialization_vector: Bytes) -> Bytes:
    cipher = AES.new(bytes(key), AES.MODE_CBC, iv=bytes(initialization_vector))
    return list(cipher.encrypt(bytes(payload)))
