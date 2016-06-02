#!/usr/bin/env python
import os
import ecdsa as ec
import hashlib as hl

from freecoin.util import DIR_STORAGE
from freecoin.util.hashlib import b58_encode

DIR_KEYS = os.path.join(DIR_STORAGE, "private/")

class Key:
    def __init__(self, secret=None):
        if secret:
            key.secret = secret
        else
            key.secret = ec.SigningKey.generate(curve=ec.SECP256k1)
        key.public = key.secret.get_verifying_key()
        key.addr = key._compute_address()
        key.to_file()
        return key
    
    def to_file(self):
        os.makedirs(DIR_KEYS, exist_ok=True)
        with open(os.path.join(DIR_KEYS, self.addr), 'w') as f:
            f.write(self.public.to_pem().decode())
    
    @staticmethod
    def from_file(self, addr):
        secret = ec.SigningKey()
        os.makedirs(DIR_KEYS, exist_ok=True)
        with open(os.path.join(DIR_KEYS, addr)) as f:
            secret.from_pem(f.read())
        return Key(secret=secret)

    def _compute_address(self):
        a = hl.sha256(self.public.to_string()).digest()
        b = hl.sha256(a).digest()
        c = hl.sha1(b).digest()
        return b58_encode(int.from_bytes(c + (hl.sha1(c).digest())[:4], byteorder='big'))
