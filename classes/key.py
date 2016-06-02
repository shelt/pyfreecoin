#!/usr/bin/env python
import os
import ecdsa as ec
import hashlib as hl

import freecoin as fc
from freecoin.util.hashlib import b58_encode

class Key:
    def __init__(self, secret=None):
        if secret:
            self.secret = secret
        else:
            self.secret = ec.SigningKey.generate(curve=ec.SECP256k1)
        self.public = self.secret.get_verifying_key()
        self.addr = self._compute_address()
    
    def to_file(self):
        os.makedirs(fc.DIR_KEYS, exist_ok=True)
        with open(os.path.join(fc.DIR_KEYS, self.addr), 'w') as f:
            f.write(self.secret.to_pem().decode())
    
    @staticmethod
    def from_file(addr):
        secret = ec.SigningKey.generate()
        os.makedirs(fc.DIR_KEYS, exist_ok=True)
        with open(os.path.join(fc.DIR_KEYS, addr)) as f:
            secret.from_pem(f.read())
        return Key(secret=secret)

    def _compute_address(self):
        a = hl.sha256(self.public.to_string()).digest()
        b = hl.sha256(a).digest()
        c = hl.sha1(b).digest()
        return b58_encode(int.from_bytes(c + (hl.sha1(c).digest())[:4], byteorder='big'))
